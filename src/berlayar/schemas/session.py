# berlayar/schemas/session.py

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class SessionInput(BaseModel):
    step: Optional[str] = None
    input: Optional[Dict[str, str]] = None

class StorytellingData(BaseModel):  # Added new model to store storytelling data
    segment: str
    user_input: Dict[str, str]

class Session(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    mobile_number: Optional[str] = None
    created_at: datetime = datetime.now()
    ended_at: Optional[datetime] = None
    current_step: Optional[str] = None
    user_inputs: Optional[List[SessionInput]] = []
    story_id: Optional[str] = None  # Added story_id field
    story_progress: Optional[int] = Field(default=0)  # Added story_progress field
    story_data: Optional[List[StorytellingData]] = []  # Added story_data field
    preferences: Dict[str, Any] = Field(default_factory=dict)
    onboarding_complete: Optional[bool] = False
