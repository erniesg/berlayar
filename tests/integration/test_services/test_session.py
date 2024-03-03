import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from berlayar.services.session import Session
from berlayar.services.user import User

class TestSessionIntegration(unittest.TestCase):
    def setUp(self):
        # Mock user service and local storage
        self.user_service_mock = MagicMock(spec=User)
        self.local_storage_mock = MagicMock()

    def test_user_creation_and_session_initialization(self):
            # Scenario: Verify that a new user can be created and a session is initialized properly
            user_data = {
                "user_id": "123",
                "mobile_number": "1234567890",
                "language": "English",
                "location": "Test Location",
                "age": 25,
                "preferred_name": "Test User",
                "email": "test@example.com",
                "preferences": None
            }
            self.user_service_mock.create_user.return_value = user_data

            # Initialize session for the new user
            session = Session(user_service=self.user_service_mock, storages=[self.local_storage_mock])

            # Create new user and initialize session
            session.create_or_update_user(user_data)

            # Verify session initialization
            self.assertEqual(session.user, user_data)
            self.assertIsInstance(session.session_id, str)
            self.assertIsInstance(session.start_time, datetime)
            self.assertIsInstance(session.last_accessed, datetime)
            self.assertFalse(session.session_end)

    def test_resume_incomplete_onboarding(self):
        # Scenario: Test the ability to resume a session for an existing user with incomplete onboarding
        existing_user_data = {
            "user_id": "123",
            "mobile_number": "1234567890",
            "language": "English",
            "location": "Test Location",
            "age": 25,
            "preferred_name": "Test User",
            "email": "test@example.com",
            "preferences": None  # Simulating incomplete onboarding
        }
        self.user_service_mock.get_user_info.return_value = existing_user_data

        # Initialize session for the existing user
        session = Session(user_service=self.user_service_mock, storages=[self.local_storage_mock])

        # Simulate session resumption
        session.resume_onboarding()

        # Verify that onboarding flow is initiated
        self.assertTrue(session.onboarding_in_progress)

    def test_resume_completed_onboarding_empty_story_progress(self):
        # Scenario: Test the ability to resume a session for an existing user with completed onboarding but no story progress
        existing_user_data = {
            "user_id": "123",
            "mobile_number": "1234567890",
            "language": "English",
            "location": "Test Location",
            "age": 25,
            "preferred_name": "Test User",
            "email": "test@example.com",
            "preferences": {'some_preference': 'value'}  # Simulating completed onboarding with empty story progress
        }
        self.user_service_mock.get_user_info.return_value = existing_user_data

        # Initialize session for the existing user
        session = Session(user_service=self.user_service_mock, storages=[self.local_storage_mock])

        # Simulate session resumption
        session.resume_onboarding()

        # Verify that storytelling engine is initiated to start a new story
        self.assertTrue(session.storytelling_in_progress)

    def test_resume_completed_onboarding_non_empty_story_progress(self):
        # Scenario: Test the ability to resume a session for an existing user with completed onboarding and non-empty story progress
        existing_user_data = {
            "user_id": "123",
            "mobile_number": "1234567890",
            "language": "English",
            "location": "Test Location",
            "age": 25,
            "preferred_name": "Test User",
            "email": "test@example.com",
            "preferences": {'some_preference': 'value'},
            "story_progress": {'story_id': '123', 'progress': 50}  # Simulating completed onboarding with non-empty story progress
        }
        self.user_service_mock.get_user_info.return_value = existing_user_data

        # Initialize session for the existing user
        session = Session(user_service=self.user_service_mock, storages=[self.local_storage_mock])

        # Simulate session resumption
        session.resume_onboarding()

        # Verify that storytelling engine is initiated to resume the ongoing story
        self.assertTrue(session.storytelling_in_progress)

    def test_session_expiry_handling(self):
        # Scenario: Test the handling of session expiry
        expiry_duration = timedelta(hours=1)
        session = Session(user_service=self.user_service_mock, storages=[self.local_storage_mock], expiry_duration=expiry_duration)

        # Simulate session start
        session.start_time = datetime.now() - timedelta(hours=2)  # Expired session

        # Check session expiry
        session_expired = session.check_session_expiry()

        # Verify that session is properly ended
        self.assertTrue(session_expired)
        self.assertTrue(session.session_end)

    def test_end_session(self):
        # Scenario: Test the ability to manually end a session
        session = Session(user_service=self.user_service_mock, storages=[self.local_storage_mock])

        # End the session manually
        session.end_session()

        # Verify that session is properly ended
        self.assertTrue(session.session_end)

    def test_error_handling(self):
        # Scenario: Test error handling scenarios
        # Simulate user creation failure
        self.user_service_mock.create_user.side_effect = Exception("User creation failed")
        with self.assertRaises(Exception):
            Session(user_service=self.user_service_mock, storages=[self.local_storage_mock])

        # Simulate local storage operation failure
        self.local_storage_mock.save.side_effect = Exception("Storage operation failed")
        session = Session(user_service=self.user_service_mock, storages=[self.local_storage_mock])

        # Simulate session operation
        session.update_last_accessed()

        # Verify error handling
        self.assertTrue(session.error_occurred)

    def test_interaction_with_local_storage(self):
        # Scenario: Test the interaction with local storage for session data persistence
        session = Session(user_service=self.user_service_mock, storages=[self.local_storage_mock])

        # Perform operations that update session data
        session.update_last_accessed()

        # Verify that session data is properly persisted and retrieved from local storage
        self.local_storage_mock.save.assert_called_once()
        self.local_storage_mock.load.assert_called_once()

if __name__ == '__main__':
    unittest.main()
