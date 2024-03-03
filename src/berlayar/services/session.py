# berlayar/src/berlayar/services/session.py
from datetime import datetime, timedelta
from typing import Optional
import uuid
from berlayar.schemas.user import UserModel, StoryProgress

class Session:
    def __init__(self, user: UserModel):
        self.session_id: str = str(uuid.uuid4())
        self.user: UserModel = user
        self.start_time: datetime = datetime.now()
        self.last_accessed: datetime = datetime.now()
        self.story_progress: Optional[StoryProgress] = None
        self.session_end: bool = False
        self.expiry_duration: timedelta = timedelta(hours=24)  # Example: 24-hour session expiry

    def update_last_accessed(self):
        self.last_accessed = datetime.now()

    def update_story_progress(self, story_id: str, progress: int):
        if self.story_progress and self.story_progress.story_id == story_id:
            self.story_progress.progress = progress
        else:
            self.story_progress = StoryProgress(story_id=story_id, progress=progress)

    def check_session_expiry(self) -> bool:
        """Check if the session has expired."""
        if datetime.now() - self.last_accessed > self.expiry_duration:
            self.end_session()
            return True
        return False

    def end_session(self):
        self.session_end = True
        # Here, you can perform cleanup operations such as logging session end, saving final state, etc.

    def is_story_completed(self, story_end_checkpoint: int) -> bool:
        """Check if the user has reached the end of the story."""
        if self.story_progress and self.story_progress.progress >= story_end_checkpoint:
            self.end_session()
            return True
        return False

    def __repr__(self):
        return f"<Session(session_id={self.session_id}, user_id={self.user.user_id}, story_progress={self.story_progress}, session_end={self.session_end})>"
