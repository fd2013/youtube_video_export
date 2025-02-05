# YouTube Channel Video Exporter

This Python script allows you to fetch all uploaded videos from a specific YouTube channel and export the video titles and URLs to a CSV file. It features a simple graphical user interface (GUI) built with Tkinter.

## 🚀 Features
- Fetch all uploaded videos from a YouTube channel
- Export video titles and links to a CSV file
- User-friendly GUI for easy interaction

## 📋 Requirements
- Python 3.x
- Required libraries:
  - `requests`
  - `tkinter` (comes pre-installed with Python)

You can install `requests` using:
```bash
pip install requests
```

## 🔑 Getting a YouTube Data API Key
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the **YouTube Data API v3**.
4. Go to **APIs & Services > Credentials**.
5. Click **Create Credentials > API Key**.
6. Copy your API key and replace `YOUR_YOUTUBE_API_KEY` in the script.

## 🔍 How to Find a YouTube Channel ID
- For channels with `/channel/` in the URL:
  - Example: `https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw`
  - Channel ID: `UC_x5XG1OV2P6uZZ5FSM9Ttw`
- For channels with custom names (`/@username`):
  - Right-click > **View Page Source** > Search `channelId`.

## 💡 Usage
1. Replace `YOUR_YOUTUBE_API_KEY` with your actual API key in the script.
2. Run the script:
   ```bash
   python youtube_channel_import.py
   ```
3. Enter the YouTube Channel ID in the GUI.
4. Click **"Fetch Videos and Save to CSV"**.
5. Choose the destination to save the CSV file.

## 📦 Output
The CSV file will contain:
- **Title:** The title of the video
- **URL:** The direct link to the video

## 🛠️ Contributing
Feel free to fork the repository, make changes, and submit pull requests.

## 📄 License
This project is licensed under the MIT License.


