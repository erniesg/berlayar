import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from berlayar.services.session import Session

class TestSessionUnit(unittest.TestCase):
    def setUp(self):
        # Mock user service
        self.user_service_mock = MagicMock()
        self.user_service_mock.get_user_info = MagicMock(return_value=None)  # User doesn't exist initially
        self.user_service_mock.create_user = MagicMock(return_value=None)
        self.user_service_mock.update_preferences = MagicMock(return_value=None)

        # Initialize session with mocked user service
        self.session_service = Session(user_service=self.user_service_mock)

        # Mock user data
        self.user_data = {
            "user_id": "123",
            "mobile_number": "1234567890",
            "language": "English",
            "location": "Test Location",
            "age": 25,
            "preferred_name": "Test User",
            "email": "test@example.com",
            "preferences": None
        }

    def test_create_new_user(self):
        # Test new user creation
        self.session_service.create_or_update_user(self.user_data)
        self.user_service_mock.create_user.assert_called_once_with(self.user_data)

    def test_resume_incomplete_onboarding(self):
        # Test resuming incomplete onboarding
        incomplete_user_data = self.user_data.copy()
        incomplete_user_data['preferences'] = None  # Simulating incomplete onboarding
        self.user_service_mock.get_user_info.return_value = incomplete_user_data

        # Call the session method for resuming onboarding
        self.session_service.resume_onboarding()

        # Ensure that update_preferences method is called with user ID and updated preferences
        self.user_service_mock.update_preferences.assert_called_once_with("123", updated_preferences)

    def test_resume_completed_onboarding_empty_story_progress(self):
        # Test resuming completed onboarding with empty story progress
        completed_user_data = self.user_data.copy()
        completed_user_data['preferences'] = {'some_preference': 'value'}  # Simulating completed onboarding
        self.user_service_mock.get_user_info.return_value = completed_user_data

        # Call the session method for resuming onboarding
        self.session_service.resume_onboarding()

        # Ensure that storytelling engine is initiated to start a new story

    def test_resume_completed_onboarding_non_empty_story_progress(self):
        # Test resuming completed onboarding with non-empty story progress
        completed_user_data_with_progress = self.user_data.copy()
        completed_user_data_with_progress['preferences'] = {'some_preference': 'value'}
        completed_user_data_with_progress['story_progress'] = {'story_id': '123', 'progress': 50}
        self.user_service_mock.get_user_info.return_value = completed_user_data_with_progress

        # Call the session method for resuming onboarding
        self.session_service.resume_onboarding()

        # Ensure that storytelling engine is initiated to resume the story

    def test_update_last_accessed(self):
        # Test updating last accessed time
        initial_last_accessed = self.session_service.last_accessed
        self.session_service.update_last_accessed()
        updated_last_accessed = self.session_service.last_accessed

        # Ensure that last accessed time is updated
        self.assertNotEqual(initial_last_accessed, updated_last_accessed)

    def test_check_session_expiry(self):
        # Test session expiry
        self.session_service.last_accessed = datetime.now() - timedelta(hours=25)  # Exceed expiry duration

        # Call the session method to check expiry
        session_expired = self.session_service.check_session_expiry()

        # Ensure that session is expired
        self.assertTrue(session_expired)

    def test_end_session(self):
        # Test ending session
        self.session_service.end_session()

        # Ensure that session_end flag is set to True
        self.assertTrue(self.session_service.session_end)

if __name__ == '__main__':
    unittest.main()
