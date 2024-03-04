from datetime import datetime, timedelta
from typing import Optional
import uuid
import os
from berlayar.schemas.user import UserModel
from berlayar.services.user import User
from berlayar.utils.load_keys import load_environment_variables
from berlayar.dataops.storage.gcs import read_file_from_gcs
from berlayar.dataops.storage.local import LocalStorage
import json
import logging

class Session:
    def __init__(self, user_service: User, storages=None, expiry_duration: timedelta = timedelta(hours=24)):
        self.user_service = user_service
        self.session_id: str = str(uuid.uuid4())
        self.start_time: datetime = datetime.now()
        self.last_accessed: datetime = datetime.now()
        self.session_end: bool = False
        self.expiry_duration: timedelta = expiry_duration
        self.storages = storages or []
        load_environment_variables()
        self.GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize LocalStorage instance
        self.storage = LocalStorage()

        # Save session data to file
        self.save_session_to_file()

    def save_session_to_file(self):
        """Save session information to a JSON file."""
        session_data = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "session_end": self.session_end,
            "expiry_duration_hours": self.expiry_duration.total_seconds() / 3600
        }
        file_path = os.path.join("sessions", f"{self.session_id}.json")
        self.storage.save_data(file_path, session_data)

    def create_or_update_user(self, user_data: dict) -> UserModel:
        """Create a new user or update an existing user."""
        mobile_number = user_data.get("mobile_number")
        existing_user = self.user_service.get_user_info(mobile_number)
        if existing_user:
            # Update user data if user exists
            self.user = self.user_service.update_user(existing_user["user_id"], user_data)
            return self.user  # Return the updated user object
        else:
            # Create a new user if user does not exist
            created_user = self.user_service.create_user(user_data)
            if created_user:
                self.user = created_user  # Assign the created user object
                language = user_data.get("language", "en")  # Default to English if language is not specified
                instructions = self._load_instructions_from_gcs(language)
                self._send_message_to_user(self.user.user_id, instructions.get("welcome_message", "Welcome!"))  # Default message if welcome_message is not found
                print("Onboarding started successfully.")
                return self.user  # Return the created user object
            else:
                print("Failed to create user.")  # Print error message if user creation fails
                return None

    def process_user_response(self, response: str, user_data: dict):
        """Process user response."""
        user_id = user_data.get("user_id")
        if response.lower() in ['en', 'zh']:
            language = response.lower()
            # Correctly starts the onboarding process for the chosen language
            self._start_onboarding(user_id, language, user_data)
        else:
            # Sends an error message only if the response is indeed invalid
            error_message = "Invalid language selection. Please choose 'en' for English or 'zh' for Chinese."
            self._send_message_to_user(user_id, error_message)

    def _start_onboarding(self, user_id: str, language: str, user_data: dict):
        """Start the onboarding process for the user."""
        instructions = self._load_instructions_from_gcs(language)
        prompts = ["name_prompt", "age_prompt", "location_prompt"]
        for prompt in prompts:
            message = instructions.get(prompt, "Please provide the required information.")
            self._send_message_to_user(user_id, message)
            # Collect user response for each prompt
            # Assuming user responses are received through some messaging platform
            # and processed accordingly
        # Once all prompts are completed, update user details
        self.user_service.update_user(user_id, user_data)  # Assuming user_data contains all collected information

    def _send_message_to_user(self, user_id: str, message: str):
        """Send a message to the user."""
        # Code to send message to user (e.g., through messaging platform)
        pass

    def _load_instructions_from_gcs(self, language: str = "en"):
        """Load instructions from GCS for the specified language."""
        blob_name = f"berlayar/raw_data/instructions.json"
        instructions_json = read_file_from_gcs(self.GCS_BUCKET_NAME, blob_name)
        instructions = json.loads(instructions_json)
        return instructions.get(language, {})  # Return instructions for the specified language, default to empty dict

    def update_last_accessed(self):
        """Update the last accessed timestamp."""
        self.last_accessed = datetime.now()

    def check_session_expiry(self) -> bool:
        """Check if the session has expired."""
        if datetime.now() - self.last_accessed > self.expiry_duration:
            self.end_session()
            return True
        return False

    def end_session(self):
        """End the session."""
        self.session_end = True
        # Perform cleanup operations if needed

    def __repr__(self):
        return f"<Session(session_id={self.session_id}, session_end={self.session_end})>"
