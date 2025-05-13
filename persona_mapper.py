# persona_mapper.py

import json
import logging
from collections import Counter

class PersonaMapper:
    def __init__(self):
        self.logger = logging.getLogger("PersonaMapper")

    def analyze_engagement(self, user_data):
        try:
            persona = {
                "interests": self._top_items(user_data.get("interests", [])),
                "engagement_style": self._classify_behavior(user_data.get("interactions", [])),
                "platform_usage": Counter(user_data.get("platforms", [])).most_common(1)[0][0]
            }
            return persona
        except Exception as e:
            self.logger.error(f"Persona mapping failed: {e}")
            return {}

    def _top_items(self, items):
        return [item for item, _ in Counter(items).most_common(3)]

    def _classify_behavior(self, interactions):
        if len(interactions) > 100:
            return "Power User"
        elif len(interactions) > 20:
            return "Regular Viewer"
        return "Occasional"
