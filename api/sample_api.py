import random
import asyncio
from typing import List, Dict

class SampleAPI:
    def __init__(self):
        self.tracks = [
            {"id": f"track_{i}", "title": f"Sample Track {i}", "artist": f"Artist {i}", 
             "genre": random.choice(["pop", "rock", "hip-hop", "electronic", "classical"])} 
            for i in range(1, 101)
        ]
        self.playlists = [
            {"id": f"playlist_{i}", "name": f"Playlist {i}", 
             "tracks": random.sample(self.tracks, random.randint(5, 20))}
            for i in range(1, 11)
        ]
        self.radio_stations = [
            {"id": f"station_{i}", "name": f"Station {i}", "genre": genre}
            for i, genre in enumerate(["pop", "rock", "hip-hop", "electronic", "classical"], 1)
        ]

    async def search_tracks(self, query: str, limit: int = 10) -> List[Dict]:
        await asyncio.sleep(0.1)  # Simulate network delay
        return random.sample([track for track in self.tracks if query.lower() in track['title'].lower()], min(limit, 10))

    async def get_track_details(self, track_id: str) -> Dict:
        await asyncio.sleep(0.05)  # Simulate network delay
        track = next((track for track in self.tracks if track['id'] == track_id), None)
        if track:
            return {**track, "duration": random.randint(180, 300), "album": f"Album {random.randint(1, 10)}"}
        return None

    async def get_recommendations(self, track_id: str, limit: int = 5) -> List[Dict]:
        await asyncio.sleep(0.1)  # Simulate network delay
        return random.sample([track for track in self.tracks if track['id'] != track_id], limit)

    async def get_top_tracks(self, limit: int = 20) -> List[Dict]:
        await asyncio.sleep(0.1)  # Simulate network delay
        return random.sample(self.tracks, limit)

    async def get_genres(self) -> List[str]:
        await asyncio.sleep(0.05)  # Simulate network delay
        return list(set(track['genre'] for track in self.tracks))

    async def get_radio_stations(self) -> List[Dict]:
        await asyncio.sleep(0.05)  # Simulate network delay
        return self.radio_stations

    async def get_user_playlists(self) -> List[Dict]:
        await asyncio.sleep(0.05)  # Simulate network delay
        return self.playlists

sample_api = SampleAPI()
__all__ = ['sample_api']