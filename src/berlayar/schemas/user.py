from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import uuid

class UserPreferences(BaseModel):
    image_gen_model: Optional[str]
    language: Optional[str]

class StoryProgress(BaseModel):
    story_id: Optional[str] = None
    progress: Optional[int] = Field(default=0)

class UserModel(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_name: Optional[str] = None
    preferred_name: str = Field(..., min_length=1)
    age: int = Field(..., gt=0)  # Greater than 0
    email: Optional[EmailStr]
    country: str = Field(..., min_length=1)
    mobile_number: str = Field(..., min_length=1)
    preferences: Optional[UserPreferences]
    story_progress: Optional[StoryProgress] = None
