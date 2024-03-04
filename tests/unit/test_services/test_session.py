import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, call  # Import 'call' here
from berlayar.services.session import Session
from berlayar.schemas.user import UserModel

class TestSessionUnit(unittest.TestCase):
    def setUp(self):
        # Mock user service
        self.user_service_mock = MagicMock()
        self.user_service_mock.get_user_info = MagicMock(return_value=None)  # User doesn't exist initially
        self.user_service_mock.create_user = MagicMock(return_value=None)
        self.user_service_mock.update_preferences = MagicMock(return_value=None)

        # Initialize session with mocked user service
        self.session_service = Session(user_service=self.user_service_mock)

        # Define user_data as an instance attribute
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

        # Mock user creation to return a UserModel instance
        self.mock_user_model = UserModel(**self.user_data)
        self.user_service_mock.create_user.return_value = self.mock_user_model

        # Mocking _load_instructions_from_gcs to return predefined instructions
        self.mocked_instructions = {
            "en": {
                "welcome_message": "Welcome! Please choose your language. 欢迎！请选择您的语言。",
                "name_prompt": "Hello! What's your name?",
                "age_prompt": "How old are you?",
                "location_prompt": "Where are you located?",
                "begin_story": "Click 'Begin' to start the story."
            }
        }

    def test_session_initialization(self):
        # Test session initialization
        self.assertIsNotNone(self.session_service.user_service)
        self.assertIsNotNone(self.session_service.session_id)
        self.assertIsInstance(self.session_service.start_time, datetime)
        self.assertIsInstance(self.session_service.last_accessed, datetime)
        self.assertFalse(self.session_service.session_end)
        self.assertIsInstance(self.session_service.expiry_duration, timedelta)

    def test_send_message_to_user(self):
        # Test sending a message to user
        user_id = "123"
        message = "Test message"
        self.assertIsNone(self.session_service._send_message_to_user(user_id, message))  # Assuming message sending function returns None

    def test_load_instructions_from_gcs(self):
        # Test loading instructions from GCS
        instructions = self.session_service._load_instructions_from_gcs()
        self.assertIsNotNone(instructions)
        self.assertIsInstance(instructions, dict)

    def test_create_new_user(self):
        # Mock the return value of create_user to be a UserModel object
        created_user_model = UserModel(**self.user_data)  # Assuming UserModel accepts user data as kwargs
        self.user_service_mock.create_user = MagicMock(return_value=created_user_model)

        # Test new user creation
        created_user = self.session_service.create_or_update_user(self.user_data)
        self.assertEqual(created_user, created_user_model)

    def test_language_selection(self):
        # Test language selection
        created_user = self.session_service.create_or_update_user(self.user_data)

        # Verify the `create_user` method was called correctly with the provided user data
        self.user_service_mock.create_user.assert_called_once_with(self.user_data)

        print("Created user:", created_user)
        self.assertIsNotNone(created_user, "User creation failed")

        # Assuming that user_data now includes the 'user_id' of the created user
        # And assuming process_user_response updates user preferences internally
        language_response = "en"
        updated_user_data = self.user_data.copy()
        updated_user_data['language'] = language_response  # Update the language preference in user data

        # Simulate language selection by calling process_user_response
        self.session_service.process_user_response(language_response, updated_user_data)

        # Assuming 'update_user' is the method that gets called internally to update the user's language preference
        # Verify that 'update_user' was called with the correct parameters
        # This assumes that 'user_id' is part of the 'updated_user_data' or is otherwise accessible
        self.user_service_mock.update_user.assert_called_once_with(updated_user_data['user_id'], updated_user_data)

        # If 'update_preferences' specifically is used instead of 'update_user', then you would check like this:
        # expected_preferences = {"language": "en"}
        # self.user_service_mock.update_preferences.assert_called_once_with(created_user.user_id, expected_preferences)

    def test_onboarding_messages(self):
        # Mocking _load_instructions_from_gcs to return predefined instructions
        self.session_service._load_instructions_from_gcs = MagicMock(return_value=self.mocked_instructions["en"])

        # Mock `_send_message_to_user` to intercept and test message sending
        self.session_service._send_message_to_user = MagicMock()

        # Simulate user creation, which should trigger the welcome message
        self.session_service.create_or_update_user(self.user_data)

        # Assuming the welcome message is sent as part of user creation
        welcome_message = self.mocked_instructions["en"]["welcome_message"]

        # Now, simulate the user responding with their language preference, leading to onboarding messages
        language_response = "en"
        self.session_service.process_user_response(language_response, self.user_data)

        # Expected onboarding messages following the language selection
        expected_messages = [
            "Hello! What's your name?",
            "How old are you?",
            "Where are you located?"
        ]

        # Verify that _send_message_to_user was called for the welcome message and each expected onboarding message
        calls = [call(self.user_data["user_id"], welcome_message)] + [call(self.user_data["user_id"], msg) for msg in expected_messages]
        self.session_service._send_message_to_user.assert_has_calls(calls, any_order=True)

    def test_onboarding_completion(self):
        # Test completion of onboarding, assuming user_data includes 'user_id'
        self.session_service.create_or_update_user(self.user_data)

        # Mock the get_user_info method to return the updated user data as if the user has been found and created
        self.user_service_mock.get_user_info.return_value = self.user_data

        # Simulate user selecting a language by directly manipulating the user_data (as process_user_response would)
        language_response = "en"
        updated_user_data = self.user_data.copy()
        updated_user_data['language'] = language_response  # Simulate updating the language in the user data

        # Call process_user_response to simulate responding to the language selection prompt
        # Note: Corrected to match the method signature process_user_response(response: str, user_data: dict)
        self.session_service.process_user_response(language_response, updated_user_data)

        # Simulate user providing responses to onboarding prompts
        # Here we directly update updated_user_data to reflect these changes, as would be done by subsequent calls to process_user_response
        updated_user_data.update({
            "preferred_name": "Test User",
            "age": 25,  # Assuming the process converts the age response to an integer
            "location": "Test Location",
        })

        # Assuming that the process_user_response method or a similar method internally calls update_user to save these changes
        # Verify that update_user was called with the expected updated user data
        # This assertion assumes that the user_service's update_user method is called with the user_id and the updated_user_data
        self.user_service_mock.update_user.assert_called_once_with(self.user_data["user_id"], updated_user_data)

        # If your logic specifically involves updating preferences and there's a separate method for it, adjust accordingly
        # For example, if there's an update_preferences method that's called instead of update_user, you would assert its call like this:
        # expected_preferences = {"language": "en", ...other preferences...}
        # self.user_service_mock.update_preferences.assert_called_once_with(self.user_data["user_id"], expected_preferences)

    def test_resume_incomplete_onboarding(self):
        # Test resuming incomplete onboarding
        incomplete_user_data = self.user_data.copy()
        incomplete_user_data['preferences'] = None  # Simulating incomplete onboarding
        self.user_service_mock.get_user_info.return_value = incomplete_user_data

        # Call the session method for resuming onboarding
        self.assertIsNone(self.session_service.resume_onboarding())

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
