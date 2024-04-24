import asyncio
import aiohttp
import pandas as pd
import os.path
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build


class YouTubeVideoExtractor:
    def __init__(self, api_key, db_location="database/transcripts.json"):
        self.api_key = api_key
        self.db_location = db_location
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    async def fetch_channel_id(self, channel_username):
        url = f'https://www.youtube.com/{channel_username}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    meta_tag = soup.find('meta', property='og:url')

                    if meta_tag:
                        url = meta_tag['content']
                        channel_id = url.split('/')[-1]
                        return channel_id
                    else:
                        print("No og:url meta tag found.")
                else:
                    print(f"Failed to retrieve the webpage for {channel_username}. Status code:", response.status)

    async def fetch_videos_from_playlist(self, playlist_id, start_of_week):
        videos = []
        next_page_token = None

        while True:
            playlist_items_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            filtered_videos = [video for video in playlist_items_response['items'] if
                               start_of_week <= datetime.strptime(video['snippet']["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").date()]

            videos += filtered_videos

            if len(filtered_videos) != 50:
                break

            next_page_token = playlist_items_response.get('nextPageToken')
            if not next_page_token:
                break

        return videos

    async def scrape_channel_async(self, channel_username):
        channel_id = await self.fetch_channel_id(channel_username)
        if channel_id:
            playlist_id = await self.get_channel_playlist_id(channel_id)
            # Get the start date of the current week
            today = datetime.now(timezone.utc).date()
            start_of_week = today - timedelta(days=7)
            videos = await self.fetch_videos_from_playlist(playlist_id, start_of_week)
            return [await self.set_json_structure(channel_username,playlist_id,video) for video in videos]

    async def scrape_channels_async(self, channels):
        return await asyncio.gather(*[self.scrape_channel_async(channel) for channel in channels])

    async def get_channel_playlist_id(self, channel_id):
        request = self.youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        response = request.execute()
        return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    async def get_video_transcript(self, video_id, languages=["pt", "en"]):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            return transcript
        except Exception as e:
            print("Error:", e)
            return None

    async def set_json_structure(self, channel_username, playlist_id, video):
        return {
            "channel_username": channel_username,
            "playlist_id": playlist_id,
            "title": video['snippet']["title"],
            "publishedAt": video['snippet']["publishedAt"],
            "transcript": await self.get_video_transcript(video['snippet']['resourceId']['videoId'])
        }

    def save_in_database(self, channels):
        loop = asyncio.get_event_loop()
    
        channels_data = loop.run_until_complete(self.scrape_channels_async(channels))
        df = pd.DataFrame([video for channel_videos in channels_data for video in channel_videos])
        df.dropna(inplace=True)

        # Convert DataFrame to JSON string
        json_data = df.to_json(orient="records")

        # Write JSON data to file
        mode = 'a' if os.path.exists(self.db_location) else 'w'
        with open(self.db_location, mode) as f:
            f.write(json_data)
            f.write("\n")  # Add a newline after writing JSON data if appending