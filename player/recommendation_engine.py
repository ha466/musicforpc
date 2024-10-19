from api.sample_api import sample_api
from typing import List, Dict
import asyncio

class RecommendationEngine:
    def __init__(self):
        self.track_features: Dict[str, Dict] = {}

    async def get_recommendations(self, play_history: List[Dict], num_recommendations: int = 5) -> List[Dict]:
        if not play_history:
            return []

        # Use the most recently played track for recommendations
        last_played = play_history[-1]
        recommendations = await sample_api.get_recommendations(last_played['id'], num_recommendations)

        return recommendations

    async def train_model(self, training_data: List[Dict]) -> None:
        # In a real scenario, this method would train your ML model
        # For this example, we'll just populate our track_features dictionary with some dummy data
        for track in training_data:
            track_details = await sample_api.get_track_details(track['id'])
            self.track_features[track['id']] = {
                'genre': track_details['genre'],
                # Other features would go here in a real scenario
            }