from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import uuid

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import uuid

class UserPreferences(BaseModel):
    image_gen_model: Optional[str] = None
    language: Optional[str] = None

class StoryProgress(BaseModel):
    story_id: Optional[str] = None
    progress: Optional[int] = Field(default=0)

class UserModel(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_name: Optional[str] = None
    preferred_name: str
    full_name: Optional[str] = None  # Optional full name
    age: int = Field(gt=0)
    email: Optional[EmailStr] = None
    country: str
    mobile_number: str
    preferences: Optional[UserPreferences] = None
    story_progress: Optional[StoryProgress] = None
