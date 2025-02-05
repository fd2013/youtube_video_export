import requests
import csv
import tkinter as tk
from tkinter import filedialog, messagebox

# Replace with your YouTube Data API key
API_KEY = 'YOUR_YOUTUBE_API_KEY'

# Base URL for the YouTube Data API
BASE_URL = 'https://www.googleapis.com/youtube/v3'

def get_uploads_playlist_id(channel_id):
    url = f'{BASE_URL}/channels'
    params = {
        'part': 'contentDetails',
        'id': channel_id,
        'key': API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    try:
        uploads_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        return uploads_playlist_id
    except (IndexError, KeyError):
        print('Error retrieving uploads playlist ID.')
        return None

def get_videos_from_playlist(playlist_id):
    videos = []
    url = f'{BASE_URL}/playlistItems'
    params = {
        'part': 'snippet',
        'playlistId': playlist_id,
        'maxResults': 50,
        'key': API_KEY
    }

    while True:
        response = requests.get(url, params=params)
        data = response.json()

        for item in data.get('items', []):
            title = item['snippet']['title']
            video_id = item['snippet']['resourceId']['videoId']
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            videos.append({'title': title, 'url': video_url})

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
        params['pageToken'] = next_page_token

    return videos

def save_to_csv(videos, file_path):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Title', 'URL'])
        writer.writeheader()
        for video in videos:
            writer.writerow({'Title': video['title'], 'URL': video['url']})

def fetch_and_save():
    channel_id = channel_id_entry.get()
    if not channel_id:
        messagebox.showerror("Error", "Please enter a Channel ID")
        return

    playlist_id = get_uploads_playlist_id(channel_id)
    if playlist_id:
        videos = get_videos_from_playlist(playlist_id)
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            save_to_csv(videos, file_path)
            messagebox.showinfo("Success", f"Data saved to {file_path}")
        else:
            messagebox.showwarning("Cancelled", "Save operation cancelled.")
    else:
        messagebox.showerror("Error", "Unable to retrieve data. Check Channel ID and API key.")

# Create GUI
root = tk.Tk()
root.title("YouTube Channel Video Exporter")
root.geometry("400x200")

label = tk.Label(root, text="Enter YouTube Channel ID:")
label.pack(pady=10)

channel_id_entry = tk.Entry(root, width=50)
channel_id_entry.pack(pady=5)

fetch_button = tk.Button(root, text="Fetch Videos and Save to CSV", command=fetch_and_save)
fetch_button.pack(pady=20)

root.mainloop()
