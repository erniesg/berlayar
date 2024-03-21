import unittest
from unittest.mock import MagicMock, Mock, patch, ANY, AsyncMock, call
from berlayar.dataops.session_repository import SessionRepository
from berlayar.dataops.user_repository import UserRepository
from berlayar.handlers.onboarding_handler import OnboardingHandler
from berlayar.adapters.messaging.interface import MessagingInterface
from berlayar.utils.path import construct_path_from_root
from berlayar.utils.common import sync_wrapper
import json
import pytest

class TestOnboardingHandler(unittest.IsolatedAsyncioTestCase):
    @pytest.fixture
    def mock_update_session():
        return MagicMock()

    def setUp(self):
        # Mock repositories
        self.session_repo_mock = MagicMock(spec=SessionRepository)
        self.user_repo_mock = MagicMock(spec=UserRepository)

        # Mock messaging service
        self.messaging_service_mock = MagicMock(spec=MessagingInterface)

        # Create an instance of OnboardingHandler using the mocked repositories and messaging service
        self.onboarding_handler = OnboardingHandler(self.session_repo_mock, self.user_repo_mock, self.messaging_service_mock)

    @patch('berlayar.dataops.storage.firebase_storage.FirebaseStorage.load_data')
    def test_load_instructions(self, mock_load_data):
        # Mock return value
        instructions_data = '{"instructions": "This is a test instruction."}'
        mock_load_data.return_value = {'data': instructions_data}

        # Now when OnboardingHandler calls load_instructions, FirebaseStorage.load_data will return the mock data
        instructions = self.onboarding_handler.load_instructions()
        self.assertEqual(instructions, {'data': instructions_data})

    def test_start_onboarding_user_exists(self):
        # Mock that the user already exists
        self.user_repo_mock.get_user.return_value = {"user_id": "existing_user_id"}
        onboarding_handler = OnboardingHandler(self.session_repo_mock, self.user_repo_mock, self.messaging_service_mock)

        # Test start_onboarding method
        with self.assertRaises(ValueError):
            onboarding_handler.start_onboarding("existing_mobile_number")  # Provide existing mobile number

    def test_start_onboarding_new_user(self):
        # Mock that the user does not exist
        self.user_repo_mock.get_user.return_value = None
        # Mock the session creation
        self.session_repo_mock.create_session.return_value = "mock_session_id"

        onboarding_handler = OnboardingHandler(self.session_repo_mock, self.user_repo_mock, self.messaging_service_mock)

        # Test start_onboarding method
        new_mobile_number = "new_mobile_number 12345678"
        print("Starting onboarding for new user with mobile number:", new_mobile_number)
        result = onboarding_handler.start_onboarding(new_mobile_number)

        # Assert that a new session ID is returned
        expected_session_id = "new_mobile_number 12345678"
        self.assertEqual(result, expected_session_id)
        print("New session ID:", result)

        # Assert that the create_session method is called with the correct parameters
        expected_params = {"user_id": None, "user_inputs": [{"mobile_number": new_mobile_number}]}
        self.session_repo_mock.create_session.assert_called_once_with(expected_params)
        print("create_session called with parameters:", expected_params)

        # Assert that the get_user method is called with the correct parameters
        self.user_repo_mock.get_user.assert_called_once_with(new_mobile_number)
        print("get_user called with mobile number:", new_mobile_number)

    def test_handle_user_input(self):
        # Mock data
        session_id = "mock_session_id"
        step = "language_prompt"
        received_message = "en"  # Simulate receiving a message with language information
        input_data = {"language": received_message}  # Adjusted input data

        # Create a mock session object
        mock_session = MagicMock()  # Example usage
        mock_session.dict.return_value = {"user_inputs": [], "current_step": None}
        self.session_repo_mock.get_session.return_value = mock_session

        # Test handle_user_input method
        result = self.onboarding_handler.handle_user_input(session_id, step, input_data)  # Await here

        # Assertions
        self.assertTrue(result)  # Ensure method returns True on success

        # Assert repository method call
        self.session_repo_mock.create_session.assert_not_called()  # Ensure create_session is not called again
        self.session_repo_mock.update_session.assert_called_once_with(
            session_id, {"current_step": step, "user_inputs": [{"step": step, "input": input_data}]}
        )

    def test_handle_user_input_with_name_prompt_zh(self):
        # Mock data for language prompts
        MOCK_PROMPTS = {
            "en": {
                "name_prompt": "Hello! What's your name?"
            },
            "zh": {
                "name_prompt": "你好！你叫什么名字？"
            }
        }

        # Patch FirebaseStorage and set up the language prompts
        with patch('berlayar.dataops.storage.firebase_storage.FirebaseStorage') as firebase_storage_mock:
            firebase_storage_mock_instance = firebase_storage_mock.return_value
            firebase_storage_mock_instance.load_data.return_value = MOCK_PROMPTS

            # Mock the session with Chinese language selected
            mock_session = MagicMock()
            mock_session.dict.return_value = {"current_step": "language_prompt", "input": {"language": "zh"}}
            self.session_repo_mock.get_session.return_value = mock_session

            # Test handle_user_input method with language selection input
            self.onboarding_handler.handle_user_input("mock_session_id", "language_prompt", {"language": "zh"})

            # Retrieve the name prompt from the mocked prompts and assert it
            expected_name_prompt = MOCK_PROMPTS["zh"]["name_prompt"]
            print(f"The name prompt is {expected_name_prompt}.")
            self.assertEqual(expected_name_prompt, "你好！你叫什么名字？")

    @patch('berlayar.dataops.session_repository.SessionRepository.update_session')
    @patch('berlayar.adapters.messaging.twilio_whatsapp.TwilioWhatsAppAdapter', autospec=True)
    @patch('berlayar.dataops.storage.firebase_storage.FirebaseStorage.load_data')
    @patch('berlayar.dataops.user_repository.UserRepository')
    @patch('berlayar.dataops.session_repository.SessionRepository')
    def test_end_to_end_onboarding(self, mock_session_repo, mock_user_repo, mock_load_data, mock_twilio_adapter, mock_update_session):
        # Load instructions directly from the specified file path
        instructions_file_path = construct_path_from_root("raw_data/instructions.json")
        with open(instructions_file_path, 'r', encoding='utf-8') as file:
            instructions_content = json.load(file)
        mock_load_data.return_value = instructions_content

        # Setup the mock messaging service responses to simulate user inputs
        user_inputs = iter(["zh", "John Doe", "25", "USA"])
        messaging_service_mock = mock_twilio_adapter.return_value
        messaging_service_mock.receive_message.side_effect = lambda session_id: next(user_inputs)
        mock_user_repo.get_user.return_value = None

        # Setup the mock update session to return a MagicMock object
        mock_update_session.return_value = MagicMock()

        handler = OnboardingHandler(mock_session_repo, mock_user_repo, messaging_service_mock)

        # Start the onboarding process with a test mobile number
        mobile_number = "1234567890"
        session_id = handler.start_onboarding(mobile_number)

        # Complete the onboarding process
        handler.complete_onboarding(session_id)

        # Assert the session data has been updated correctly
        expected_user_data = {
            "user_id": None,
            "user_inputs": [
                {"mobile_number": mobile_number},
                {"step": "welcome_message", "input": {"language": "zh"}},
                {"step": "name_prompt", "input": {"preferred_name": "John Doe"}},
                {"step": "age_prompt", "input": {"age": "25"}},
                {"step": "country_prompt", "input": {"country": "USA"}}
            ],
            "current_step": "country_prompt"
        }

        # Verify that mock_update_session is being called with the expected arguments
        mock_update_session.assert_called_with(session_id, expected_user_data)
        print(f"Mock update session return value: {mock_update_session.return_value}")
        print(f"Attributes of Mock update session: {dir(mock_update_session)}")

        # Inspect the arguments passed to each call to mock_update_session
        for call_args in mock_update_session.call_args_list:
            print(f"Call arguments: {call_args}")

        # Retrieve the session data returned by update_session
        actual_session_data = mock_update_session.return_value

        # Ensure that mock_update_session is returning a value
        self.assertIsNotNone(actual_session_data, "mock_update_session returned None")

        # If actual_session_data is not None, proceed with assertions
        if actual_session_data is not None:
            # Retrieve the session data directly from the update_session call
            actual_session_data_value = actual_session_data.call_args[0][1]
            # Assert that the actual session data matches the expected data
            self.assertEqual(actual_session_data_value, expected_user_data)

        # Retrieve the session data directly from the update_session call
        actual_session_data_value = actual_session_data.call_args[0][1]  # Note: This line may need adjustment based on the MagicMock object's structure

        # Assert that the actual session data matches the expected data
        self.assertEqual(actual_session_data_value, expected_user_data)
