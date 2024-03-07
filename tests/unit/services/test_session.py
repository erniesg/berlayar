# Imports
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from berlayar.services.session import Session
from berlayar.services.user import User

# Fixture for session service with adjusted create_session method
@pytest.fixture
def session_service():
    user_service = Mock(spec=User)
    storage_interface = Mock()
    session = Session(user_service=user_service, storage_interface=storage_interface)
    return session

# Fixture for user data
@pytest.fixture
def user_data():
    return {
        "user_id": "12345",
        "preferred_name": "James",
        "age": 30,
        "country": "UK",
        "mobile_number": "123456789",
    }

def test_session_initialization(session_service):
    """Verify that a session is created successfully for a new user."""
    new_session = session_service.create_session(is_anonymous=False)  # Adjusted to use is_anonymous flag

    assert new_session.session_id is not None, "Session ID should be generated"
    assert new_session.created_at <= datetime.now(), "created_at should be set to the current time or before"
    assert new_session.last_accessed <= datetime.now(), "last_accessed should be set to the current time or before"
    assert new_session.expiry_duration == 24, "Expiry duration should be set to 24 hours by default"
    assert new_session.user_id is not None, "user_id should not be None for a new identified session"

def test_anonymous_session_creation(session_service):
    """Verify session creation for an anonymous user."""
    anonymous_session = session_service.create_session(is_anonymous=True)

    assert anonymous_session.session_id is not None, "Session ID should be generated"
    assert anonymous_session.user_id is None, "user_id should be None for an anonymous session"
    assert anonymous_session.created_at <= datetime.now(), "created_at should be set correctly"
    assert anonymous_session.last_accessed <= datetime.now(), "last_accessed should be set correctly"
    assert anonymous_session.expiry_duration == 24, "Expiry duration should be correct"

def test_conversion_to_identified_session(session_service, user_data):
    """Convert an anonymous session to an identified session using a generalized update method."""
    anonymous_session = session_service.create_session(is_anonymous=True)
    updates = {"user_id": user_data["user_id"]}
    identified_session = session_service.update_session(anonymous_session.session_id, updates)

    assert identified_session.user_id == user_data["user_id"], "Session should be associated with the correct user ID"
    assert identified_session.session_id == anonymous_session.session_id, "Session ID should remain unchanged"

def test_retrieval_for_returning_user(session_service, user_data):
    """Ensure an existing session can be retrieved for a returning user."""
    # Simulate creating a session for an existing user
    session_service.user_service.get_user_info.return_value = user_data
    new_session = session_service.create_session(is_anonymous=False, user_data=user_data)

    retrieved_session = session_service.get_session(new_session.session_id)

    assert retrieved_session.session_id == new_session.session_id, "Should retrieve the correct session based on session_id"
    assert retrieved_session.user_id == user_data["mobile_number"], "The retrieved session should have the correct user_id"

def test_session_continuation(session_service):
    """Test that a session continues to be valid over multiple interactions."""
    session = session_service.create_session(is_anonymous=True)  # Create an anonymous session for this test
    initial_last_accessed = session.last_accessed

    # Simulate a user action that updates the session
    session_service.update_session(session.session_id, {"last_accessed": datetime.now()})

    assert session.last_accessed > initial_last_accessed, "last_accessed should be updated to a later time"

def test_session_expiry(session_service):
    """Check that a session expires after the designated time period."""
    session = session_service.create_session(is_anonymous=True)  # Create an anonymous session for simplicity
    # Manually set last_accessed to simulate an old session
    session_service.update_session(session.session_id, {"last_accessed": datetime.now() - timedelta(hours=25)})

    assert session.is_expired(), "Session should be marked as expired after the designated time period"

def test_update_last_accessed(session_service):
    """Verify the update_last_accessed method works as expected."""
    session = session_service.create_session(is_anonymous=True)  # Create an anonymous session for this test
    old_last_accessed = session.last_accessed

    # Simulate a user action that updates the session
    session_service.update_session(session.session_id, {"last_accessed": datetime.now()})

    assert session.last_accessed > old_last_accessed, "last_accessed should be updated to reflect recent activity"

def test_save_session(session_service):
    """Unit test for saving session data."""
    session, storage_interface = session_service

    # Create a sample session
    sample_session = Session(
        session_id="sample_session_id",
        user_id="sample_user_id",
        start_time=datetime(2024, 3, 5, 10, 30),  # Sample start time
        last_accessed=datetime(2024, 3, 5, 11, 30),  # Sample last accessed time
        session_end=True  # Sample session end flag
    )

    # Call save_session function
    session.save_session()

    # Assert that the storage interface's append_data method was called with the correct parameters
    storage_interface.append_data.assert_called_once_with(
        data=sample_session,
        subdir="sessions",  # Specify the subdirectory for sessions
        filename="sessions.jsonl"  # Assuming appending to a JSONL file
    )

    # Additional assertions to verify specific attributes of the session
    appended_sessions = storage_interface.append_data.call_args[1]["data"]
    assert len(appended_sessions) == 1
    assert appended_sessions[0].session_id == "sample_session_id"
    assert appended_sessions[0].user_id == "sample_user_id"
    assert appended_sessions[0].start_time == datetime(2024, 3, 5, 10, 30)
    assert appended_sessions[0].last_accessed == datetime(2024, 3, 5, 11, 30)
    assert appended_sessions[0].session_end is True

def test_session_idempotence_of_update_last_accessed(session_service):
    """Ensure repeated updates to last_accessed without other actions don't affect session state unexpectedly."""
    session = session_service.create_session(is_anonymous=True)  # Create an anonymous session for this test
    session_service.update_session(session.session_id, {"last_accessed": datetime.now()})
    first_update_time = session.last_accessed

    session_service.update_session(session.session_id, {"last_accessed": datetime.now()})
    second_update_time = session.last_accessed

    # Allow for a small difference in time due to execution delay
    assert second_update_time >= first_update_time, "last_accessed should be updated on each call"
    assert (second_update_time - first_update_time).total_seconds() < 1, "Updates to last_accessed should be idempotent within a short timeframe"

def test_invalid_conversion_attempt(session_service, user_data):
    """Attempt to convert an identified session to anonymous and check for errors or unchanged state."""
    session = session_service.create_session(is_anonymous=True)  # Start with an anonymous session
    session_service.update_session(session.session_id, {"user_id": user_data["user_id"]})  # Convert to identified session

    # Attempt to convert back to anonymous (which should not be allowed or should have no effect)
    with pytest.raises(ValueError, match="Invalid attempt to anonymize an identified session"):
        session_service.update_session(session.session_id, {"user_id": None})

    # Alternatively, if your design doesn't raise an error, assert the user_id remains unchanged
    assert session.user_id == user_data["user_id"], "User ID should remain unchanged after invalid conversion attempt"
