import pytest
from unittest.mock import MagicMock
from datetime import datetime
from berlayar.dataops.session_repository import SessionRepository
from berlayar.schemas.session import Session, SessionInput
from unittest.mock import Mock, ANY, patch

@pytest.fixture
def session_repo():
    storage_mock = MagicMock()
    repo = SessionRepository(storage=storage_mock)
    return repo, storage_mock

def test_create_session(session_repo):
    repo, storage_mock = session_repo
    user_id = "uuid123"
    user_mobile = "1234567890"
    session_data = {
        "user_id": user_id,
        "mobile_number": user_mobile,
        "user_inputs": []  # Reflect the updated schema
    }
    mock_session_id = "mock_session_id"
    # Mock save_data to return the mock_session_id
    storage_mock.save_data.return_value = mock_session_id

    # Act
    session_id = repo.create_session(session_data)

    # Assert
    storage_mock.save_data.assert_called_once_with(repo.session_collection_name, ANY)  # Use ANY for the data check
    assert session_id == mock_session_id  # The returned session_id should match the mock_session_id

def test_get_session(session_repo):
    repo, storage_mock = session_repo
    session_id = "mock_session_id"
    mock_session_data = {
        "session_id": session_id,
        "user_id": "uuid123",
        "created_at": datetime.now().isoformat(),
        "user_inputs": []  # Reflect updated schema
    }
    storage_mock.load_data.return_value = mock_session_data

    # Act
    session = repo.get_session(session_id)

    # Assert
    storage_mock.load_data.assert_called_once_with(repo.session_collection_name, session_id)
    assert session.session_id == session_id
    assert session.user_id == "uuid123"
    assert isinstance(session.created_at, datetime)
    assert session.user_inputs == []

def test_update_session(session_repo):
    repo, storage_mock = session_repo
    session_id = "mock_session_id"
    updated_data = {
        "current_step": "language_prompt",
        "user_inputs": [SessionInput(step="language_prompt", input={"language": "en"}).dict()]
    }

    # Act
    repo.update_session(session_id, updated_data)

    # Assert
    storage_mock.update_data.assert_called_once_with(repo.session_collection_name, session_id, updated_data)

def test_complete_onboarding_creates_user_profile(session_repo):
    repo, storage_mock = session_repo
    user_mobile = "1234567890"
    user_id = "uuid123"
    mock_session_id = "mock_session_id"  # Define the mock_session_id

    # Prepare session data
    session_data = {
        "user_id": user_id,
        "mobile_number": user_mobile,
        "user_inputs": []
    }

    # Mock the creation to return a mock session ID
    storage_mock.save_data.return_value = mock_session_id

    # Create session and assert correct call
    session_id = repo.create_session(session_data)
    print("Called update_data during create session with:", storage_mock.update_data.call_args)
    storage_mock.save_data.assert_called_once_with(repo.session_collection_name, ANY)
    assert session_id == mock_session_id  # Validate the session ID

    # Define onboarding steps
    onboarding_steps = [
        {"step": "language_prompt", "input": {"language": "en"}},
        {"step": "name_prompt", "input": {"preferred_name": "John Doe"}},
        {"step": "age_prompt", "input": {"age": "30"}},
        {"step": "country_prompt", "input": {"country": "USA"}}
    ]

    # Iterate over steps to update the session
    for step in onboarding_steps:
        repo.update_session(session_id, {"current_step": step["step"], "user_inputs": [SessionInput(**step).dict()]})
        print("Called update_data with:", storage_mock.update_data.call_args)

    # Verify `update_data` was called the correct number of times
    assert storage_mock.update_data.call_count == len(onboarding_steps) + 1  # +1 for the initial update in create_session
