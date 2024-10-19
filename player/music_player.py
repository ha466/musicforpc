import vlc
from ytmusicapi import YTMusic
import os
import json
from api.sample_api import sample_api
from utils.config import Config
import asyncio
from typing import List, Dict

class MusicPlayer:
    def __init__(self, config: Config):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.current_media = None
        self.ytmusic = YTMusic()
        self.playlist: List[dict] = []
        self.current_track_index = 0
        self.offline_mode = False
        self.play_history: List[dict] = []
        self.offline_cache: Dict[str, dict] = {}
        self.config = config
        asyncio.create_task(self.load_offline_cache())

    async def search(self, query: str) -> List[dict]:
        if self.offline_mode:
            return [track for track in self.offline_cache.values() if query.lower() in track['title'].lower()]
        try:
            return await sample_api.search_tracks(query)
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    async def play_title(self, title: str) -> None:
        if self.offline_mode:
            if title in self.offline_cache:
                await self.play_offline(title)
            else:
                raise Exception("This track is not available offline.")
        else:
            track = await sample_api.get_track_details(title)
            if track:
                try:
                    url = f"https://example.com/stream/{track['id']}"  # Placeholder URL
                    self.current_media = self.instance.media_new(url)
                    self.player.set_media(self.current_media)
                    await self.play()
                    self.playlist.append(track)
                    self.current_track_index = len(self.playlist) - 1
                    self.play_history.append(track)
                except Exception as e:
                    print(f"Error playing title: {e}")
                    raise
            else:
                raise Exception("Track not found")

    async def play_offline(self, title: str) -> None:
        try:
            offline_track = self.offline_cache[title]
            self.current_media = self.instance.media_new(offline_track['file_path'])
            self.player.set_media(self.current_media)
            await self.play()
            self.playlist.append(offline_track)
            self.current_track_index = len(self.playlist) - 1
            self.play_history.append(offline_track)
        except Exception as e:
            print(f"Error playing offline title: {e}")
            raise

    async def play(self) -> None:
        if self.current_media:
            self.player.play()

    async def pause(self) -> None:
        self.player.pause()

    async def stop(self) -> None:
        self.player.stop()

    async def next_track(self) -> None:
        if self.current_track_index < len(self.playlist) - 1:
            self.current_track_index += 1
            await self.play_title(self.playlist[self.current_track_index]['title'])

    async def previous_track(self) -> None:
        if self.current_track_index > 0:
            self.current_track_index -= 1
            await self.play_title(self.playlist[self.current_track_index]['title'])

    async def seek(self, position: float) -> None:
        if self.current_media:
            self.player.set_position(position / 100.0)

    async def set_volume(self, volume: int) -> None:
        self.player.audio_set_volume(volume)

    async def toggle_offline_mode(self) -> None:
        self.offline_mode = not self.offline_mode
        self.config.set('offline_mode', self.offline_mode)
        await self.config.save()

    async def download_for_offline(self, title: str) -> bool:
        if not self.offline_mode:
            track = await sample_api.get_track_details(title)
            if track:
                try:
                    file_path = os.path.join("offline_cache", f"{track['id']}.mp3")
                    os.makedirs("offline_cache", exist_ok=True)
                    # Simulate downloading the file
                    open(file_path, 'w').close()
                    self.offline_cache[title] = {'title': title, 'id': track['id'], 
                                                 'file_path': file_path}
                    await self.save_offline_cache()
                    return True
                except Exception as e:
                    print(f"Error downloading for offline: {e}")
                    return False
        return False

    async def load_offline_cache(self) -> None:
        try:
            self.offline_cache = self.config.get('offline_cache', {})
        except Exception as e:
            print(f"Error loading offline cache: {e}")
            self.offline_cache = {}

    async def save_offline_cache(self) -> None:
        self.config.set('offline_cache', self.offline_cache)
        await self.config.save()

    def get_play_history(self) -> List[dict]:
        return self.play_history[-10:]  # Return last 10 played tracks

    async def is_playing(self) -> bool:
        return self.player.is_playing()

    async def get_position(self) -> float:
        return self.player.get_position()