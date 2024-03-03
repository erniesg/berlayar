from datetime import datetime, timedelta
from typing import Optional
import uuid
from berlayar.schemas.user import UserModel
from berlayar.services.user import User

class Session:
    def __init__(self, user_service: User, storages=None, expiry_duration: timedelta = timedelta(hours=24)):
        self.user_service = user_service
        self.session_id: str = str(uuid.uuid4())
        self.start_time: datetime = datetime.now()
        self.last_accessed: datetime = datetime.now()
        self.session_end: bool = False
        self.expiry_duration: timedelta = expiry_duration
        self.storages = storages or []

    def create_or_update_user(self, user_data: dict) -> UserModel:
        """Create a new user or update an existing user."""
        mobile_number = user_data.get("mobile_number")
        existing_user = self.user_service.get_user_info(mobile_number)
        if existing_user:
            # Update user data if user exists
            return self.user_service.update_user(existing_user["user_id"], user_data)
        else:
            # Create a new user if user does not exist
            return self.user_service.create_user(user_data)

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
