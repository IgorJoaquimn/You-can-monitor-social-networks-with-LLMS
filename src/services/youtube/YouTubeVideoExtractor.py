import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from youtube_transcript_api import YouTubeTranscriptApi
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor 

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

class YouTubeVideoExtractor:
    def __init__(self, api_key, db_location="database/transcripts.json", days_to_consider = 7):
        self.api_key = api_key
        self.db_location = db_location
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        
        today = datetime.now(timezone.utc).date()
        self.start_of_week = today - timedelta(days=days_to_consider)

    def fetch_channel_id(self, channel_username):
        url = f'https://www.youtube.com/{channel_username}'
        print(f"Collecting {url}...")
        
        response = requests.get(url)
        assert response.status_code == 200, f"Couldn't retrieve {channel_username} id, response {response.status}"
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        meta_tag = soup.find('meta', property='og:url')
        assert meta_tag, "No og:url meta tag found"

        url = meta_tag['content']
        channel_id = url.split('/')[-1]
        return channel_id
    
    def get_playlist_id(self, channel_id):
        request = self.youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        response = request.execute()
        assert response['items'][0]['contentDetails']['relatedPlaylists']['uploads'], f"Error while getting the playlist id of {channel_id}"
        return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
    def get_playlist_videos(self, playlist_id):
        videos = []
        next_page_token = None
        there_is_videos_to_collect = True

        while there_is_videos_to_collect:
            playlist_items_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()
            
            for video in playlist_items_response['items']:
                assert video['snippet']["publishedAt"], "Couldn't get the video publish date"
                publishedAt = video['snippet']["publishedAt"]
                cond_updated_videos = self.start_of_week <= datetime.strptime(publishedAt,DATE_FORMAT).date()
                videos.append(video)

            next_page_token = playlist_items_response.get('nextPageToken')
            cond_next_page = next_page_token != None
            there_is_videos_to_collect = cond_updated_videos and cond_next_page
            print(f"{playlist_id} - collected {len(videos):3}")
        return videos

    def get_video_transcript(self, video_id, languages=["pt", "en"]):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            return transcript
        except Exception as e:
            return ""

    def set_json_structure(self, channel_username, playlist_id, video):
        return {
            "channel_username": channel_username,
            "playlist_id": playlist_id,
            "title": video['snippet']["title"],
            "publishedAt": video['snippet']["publishedAt"],
            "transcript": self.get_video_transcript(video['snippet']['resourceId']['videoId'])
        }

    def scrape_single_channel(self, username):
        # Find the channel id for this user
        channel_id =  self.fetch_channel_id(username)
        assert channel_id, f"Couldn't get the channel id {username}"
        # Find his upload videos id
        playlist_id =  self.get_playlist_id(channel_id)
        assert playlist_id, f"Couldn't get the playlist id {username}"
        # Collect them all
        videos =  self.get_playlist_videos(playlist_id)
        assert videos, f"There is no video up to date in {username}"
        print(f"Collecting transcripts {username}\n")

        # Use ThreadPoolExecutor to process videos in parallel
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda video: self.set_json_structure(username, playlist_id, video), videos))
        return results

    def scrape_channels(self, channels):
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(self.scrape_single_channel, channels))
        return results

    def save_in_database(self,df: pd.DataFrame) -> bool:
        # Convert DataFrame to JSON string
        json_data = df.to_json(orient="records")

        os.makedirs(os.path.dirname(self.db_location),exist_ok=True)    
        # Write JSON data to file
        mode = 'a' if os.path.exists(self.db_location) else 'w'
        with open(self.db_location, mode) as f:
            f.write(json_data)
            f.write("\n")  # Add a newline after writing JSON data if appending
        return True

    def collect_channels(self, channels: List[str]) -> pd.DataFrame:
        channels_data = self.scrape_channels(channels)
        
        df = pd.DataFrame([video for channel_videos in channels_data for video in channel_videos])
        df.dropna(inplace=True)
        self.save_in_database(df)
        return df