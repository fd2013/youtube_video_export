"""A small Tkinter application for exporting videos from a YouTube channel."""

from __future__ import annotations

import csv
import os
from typing import Dict, List, Optional

import requests
import tkinter as tk
from tkinter import filedialog, messagebox

# Environment variable that can be used to provide the YouTube API key.
API_KEY_ENV = "YOUTUBE_API_KEY"

# Replace the default value below with your YouTube Data API key. The environment
# variable above takes precedence when available.
API_KEY_FALLBACK = "YOUR_YOUTUBE_API_KEY"

# Base URL for the YouTube Data API
BASE_URL = "https://www.googleapis.com/youtube/v3"

# Requests session reused across calls to benefit from connection pooling.
SESSION = requests.Session()


class YouTubeExporterError(RuntimeError):
    """Raised when the YouTube API responds with an error."""


def resolve_api_key() -> str:
    """Return the API key from the environment or the fallback constant.

    Raises:
        YouTubeExporterError: If neither a valid environment key nor the fallback
            value has been replaced by the user.
    """

    key = os.getenv(API_KEY_ENV) or API_KEY_FALLBACK
    if key and key != "YOUR_YOUTUBE_API_KEY":
        return key
    raise YouTubeExporterError(
        "A YouTube Data API key is required. Set the YOUTUBE_API_KEY environment "
        "variable or update API_KEY_FALLBACK in the script."
    )


def fetch_json(url: str, params: Dict[str, str]) -> Dict[str, object]:
    """Fetch JSON data from the YouTube API, handling HTTP and API errors."""

    try:
        response = SESSION.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:  # pragma: no cover - GUI script
        raise YouTubeExporterError(f"Failed to reach the YouTube API: {exc}") from exc

    data = response.json()
    if isinstance(data, dict) and "error" in data:
        error_info = data["error"].get("message", "Unknown error")
        raise YouTubeExporterError(f"YouTube API error: {error_info}")
    return data


def get_uploads_playlist_id(channel_id: str, api_key: str) -> Optional[str]:
    """Return the playlist ID containing the channel uploads."""

    url = f"{BASE_URL}/channels"
    params = {
        "part": "contentDetails",
        "id": channel_id,
        "key": api_key,
    }
    data = fetch_json(url, params)

    try:
        return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except (IndexError, KeyError) as exc:
        raise YouTubeExporterError(
            "Could not retrieve the uploads playlist for the provided channel ID."
        ) from exc


def get_videos_from_playlist(playlist_id: str, api_key: str) -> List[Dict[str, str]]:
    """Fetch all videos from the given playlist."""

    videos: List[Dict[str, str]] = []
    url = f"{BASE_URL}/playlistItems"
    params: Dict[str, str] = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": "50",
        "key": api_key,
    }

    while True:
        data = fetch_json(url, params)

        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            resource = snippet.get("resourceId", {})
            video_id = resource.get("videoId")
            title = snippet.get("title", "Untitled video")
            if not video_id:
                continue
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            videos.append({"title": title, "url": video_url})

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break
        params["pageToken"] = next_page_token

    return videos


def save_to_csv(videos: List[Dict[str, str]], file_path: str) -> None:
    """Persist the collected video information into a CSV file."""

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Title", "URL"])
        writer.writeheader()
        for video in videos:
            writer.writerow({"Title": video["title"], "URL": video["url"]})


def fetch_and_save() -> None:
    """Handle the button click: retrieve videos and export them to CSV."""

    status_var.set("")
    channel_id = channel_id_entry.get().strip()
    if not channel_id:
        messagebox.showerror("Error", "Please enter a Channel ID.")
        return

    try:
        api_key = resolve_api_key()
        status_var.set("Fetching videos…")
        root.update_idletasks()

        playlist_id = get_uploads_playlist_id(channel_id, api_key)
        videos = get_videos_from_playlist(playlist_id, api_key)
    except YouTubeExporterError as exc:
        messagebox.showerror("Error", str(exc))
        status_var.set("")
        return

    if not videos:
        messagebox.showinfo(
            "No Videos Found",
            "The channel uploads playlist is empty or unavailable.",
        )
        status_var.set("")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
    )
    if not file_path:
        messagebox.showwarning("Cancelled", "Save operation cancelled.")
        status_var.set("")
        return

    try:
        save_to_csv(videos, file_path)
    except OSError as exc:
        messagebox.showerror("Error", f"Failed to save CSV file: {exc}")
        status_var.set("")
        return

    messagebox.showinfo("Success", f"Data saved to {file_path}")
    status_var.set(f"Saved {len(videos)} videos.")


# Create GUI
root = tk.Tk()
root.title("YouTube Channel Video Exporter")
root.geometry("420x220")

label = tk.Label(root, text="Enter YouTube Channel ID:")
label.pack(pady=10)

channel_id_entry = tk.Entry(root, width=50)
channel_id_entry.pack(pady=5)

fetch_button = tk.Button(
    root, text="Fetch Videos and Save to CSV", command=fetch_and_save, width=35
)
fetch_button.pack(pady=10)

status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, fg="gray")
status_label.pack(pady=5)

root.mainloop()
