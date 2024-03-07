from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class SessionModel(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the session.")
    user_id: Optional[str] = Field(None, description="Unique identifier for the user, if identified. None for anonymous sessions.")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the session was created.")
    last_accessed: datetime = Field(default_factory=datetime.now, description="Timestamp for the last activity in the session.")
    expiry_duration: Optional[int] = Field(24, description="Duration in hours after which the session is considered expired.")

    class Config:
        anystr_strip_whitespace = True
        validate_assignment = True
        orm_mode = True

    def update_last_accessed(self):
        """Updates the last_accessed field to the current datetime."""
        self.last_accessed = datetime.now()

    def is_expired(self) -> bool:
        """Determines if the session has expired based on the expiry_duration."""
        return (datetime.now() - self.last_accessed).total_seconds() > self.expiry_duration * 3600

    def extend_expiry(self, hours: int):
        """Extends the session's expiry duration."""
        self.expiry_duration += hours
