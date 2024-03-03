import pytest
from datetime import datetime, timedelta
from berlayar.services.session import Session
from berlayar.schemas.user import UserModel, UserPreferences

# Fixture for creating a user model instance
@pytest.fixture
def user_model():
    return UserModel(
        preferred_name="Test User",
        age=25,
        email="testuser@example.com",
        location="Test Location",
        mobile_number="123456789",
        preferences=UserPreferences(image_gen_model="DALL·E 3", language="en")
    )

# Fixture for creating a session
@pytest.fixture
def session(user_model):
    return Session(user=user_model)

def test_session_creation(session):
    assert session is not None
    assert session.session_end == False
    assert session.user.preferred_name == "Test User"

def test_update_story_progress(session):
    session.update_story_progress(story_id="story1", progress=1)
    assert session.story_progress.story_id == "story1"
    assert session.story_progress.progress == 1

def test_session_expiry(session):
    # Simulate session expiry by manually adjusting last_accessed time
    session.last_accessed -= timedelta(hours=25)
    assert session.check_session_expiry() == True
    assert session.session_end == True

def test_end_session(session):
    session.end_session()
    assert session.session_end == True

def test_is_story_completed(session):
    session.update_story_progress(story_id="story1", progress=5)
    assert session.is_story_completed(story_end_checkpoint=5) == True
    assert session.session_end == True
