# berlayar/utils/session.py

import os
import json
from datetime import datetime
from PIL import Image
import requests  # For downloading images from URLs

class SessionManager:
    def __init__(self, base_dir="sessions_data"):
        self.base_dir = base_dir
        self.session_dir = self._initialize_session_directory()
        self.user_data = {}
        self.story_log = []

    def _initialize_session_directory(self):
        session_dir_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session_path = os.path.join(self.base_dir, session_dir_name)
        os.makedirs(session_path, exist_ok=True)
        return session_path

    def save_user_preferences(self, user_data):
        self.user_data = user_data
        preferences_path = os.path.join(self.session_dir, "user_preferences.json")
        with open(preferences_path, 'w') as file:
            json.dump(self.user_data, file, indent=4)

    def append_story_interaction(self, interaction):
        self.story_log.append(interaction)
        log_path = os.path.join(self.session_dir, "story_log.json")
        with open(log_path, 'w') as file:
            json.dump(self.story_log, file, indent=4)

    def save_image_from_url(self, image_url, filename="cover_image.png"):
        image_path = os.path.join(self.session_dir, filename)
        response = requests.get(image_url)
        with open(image_path, 'wb') as file:
            file.write(response.content)

    def save_image(self, image, filename="cover_image.png"):
        image_path = os.path.join(self.session_dir, filename)
        image.save(image_path)

    def save_complete_story(self, story_history):
        history_path = os.path.join(self.session_dir, "complete_story.json")
        with open(history_path, 'w') as file:
            json.dump(story_history, file, indent=4)
