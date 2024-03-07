import pytest
from unittest.mock import Mock
from datetime import datetime
from berlayar.services.session import Session

@pytest.fixture
def session_service():
    # Mocking user service
    user_service = Mock()

    # Mocking storage interface for local storage
    local_storage_interface = Mock()
    local_storage_interface.save_data.return_value = True

    # Mocking Firestore client
    firestore = Mock()
    firestore.collection.return_value.document.return_value.set.return_value = None

    # Create session service with local storage
    session_local_storage = Session(user_service=user_service, storage_interface=local_storage_interface)

    # Create session service with Firestore
    session_firestore = Session(user_service=user_service, storage_interface=firestore)

    return session_local_storage, session_firestore

def test_integration_save_session_local(session_service):
    """Integration test for saving session data to local storage."""
    session_local_storage = session_service[0]

    # Define a sample session
    sample_session = Session(
        session_id="sample_session_id",
        user_id="sample_user_id",
        start_time=datetime(2024, 3, 5, 10, 30),  # Sample start time
        last_accessed=datetime(2024, 3, 5, 11, 30)  # Sample last accessed time
    )

    # Save session to local storage
    session_local_storage.save_session(sample_session)

    # Retrieve appended session data from the mock storage interface
    appended_sessions = session_local_storage.storage_interface.appended_sessions

    # Assert that the session data was appended correctly
    assert len(appended_sessions) == 1
    assert appended_sessions[0].session_id == "sample_session_id"
    assert appended_sessions[0].user_id == "sample_user_id"
    assert appended_sessions[0].start_time == datetime(2024, 3, 5, 10, 30)
    assert appended_sessions[0].last_accessed == datetime(2024, 3, 5, 11, 30)

def test_integration_save_session_firestore(session_service):
    """Integration test for saving session data to Firestore."""
    session_firestore = session_service[1]

    # Define a sample session
    sample_session = Session(
        session_id="sample_session_id",
        user_id="sample_user_id",
        start_time=datetime(2024, 3, 5, 10, 30),  # Sample start time
        last_accessed=datetime(2024, 3, 5, 11, 30)  # Sample last accessed time
    )

    # Save session to Firestore
    result = session_firestore.save_session(sample_session)

    # Assert that the session was saved successfully
    assert result is True
