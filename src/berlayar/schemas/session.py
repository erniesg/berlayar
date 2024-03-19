# berlayar/schemas/session.py

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class SessionInput(BaseModel):
    step: str
    input: Dict[str, str]

class StorytellingData(BaseModel):  # Added new model to store storytelling data
    segment: str
    user_input: Dict[str, str]

class Session(BaseModel):
    session_id: Optional[str] = None
    user_id: str
    created_at: datetime = datetime.now()
    ended_at: Optional[datetime] = None
    current_step: Optional[str] = None
    user_inputs: Optional[List[SessionInput]] = []
    story_id: Optional[str] = None  # Added story_id field
    story_progress: Optional[int] = Field(default=0)  # Added story_progress field
    story_data: Optional[List[StorytellingData]] = []  # Added story_data field
