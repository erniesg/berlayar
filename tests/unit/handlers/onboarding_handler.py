import unittest
from unittest.mock import MagicMock, Mock, patch, ANY, AsyncMock
from berlayar.dataops.session_repository import SessionRepository
from berlayar.dataops.user_repository import UserRepository
from berlayar.handlers.onboarding_handler import OnboardingHandler
from berlayar.adapters.messaging.interface import MessagingInterface
from berlayar.utils.path import construct_path_from_root
from berlayar.utils.common import sync_wrapper
import json

class TestOnboardingHandler(unittest.IsolatedAsyncioTestCase):
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

    @patch('berlayar.adapters.messaging.twilio_whatsapp.TwilioWhatsAppAdapter', new_callable=AsyncMock)
    @patch('berlayar.dataops.storage.firebase_storage.FirebaseStorage.load_data')
    @patch('berlayar.dataops.user_repository.UserRepository')
    @patch('berlayar.dataops.session_repository.SessionRepository')
    def test_end_to_end_onboarding(self, mock_session_repo, mock_user_repo, mock_load_data, mock_twilio_adapter):
        instructions_file_path = construct_path_from_root("raw_data/instructions.json")
        with open(instructions_file_path, 'r', encoding='utf-8') as file:
            instructions_content = json.load(file)
        mock_load_data.return_value = instructions_content
        print(instructions_content)

        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(instructions_content)
            # Setup the mock messaging service
            messaging_service_mock = mock_twilio_adapter.return_value
            messaging_service_mock.receive_message.side_effect = ["zh", "John", "30", "USA"]
            handler = OnboardingHandler(mock_session_repo, mock_user_repo, mock_twilio_adapter)

            # Mock start_onboarding return value
            mock_user_repo.get_user.return_value = None

            # Call start_onboarding with a new mobile number
            mobile_number = "1234567890"
            session_id = handler.start_onboarding(mobile_number)

            # Verify that load_instructions is called with the correct language parameter
            prompts = handler.load_instructions(language="en")
            self.assertIsNotNone(prompts)  # Assert that prompts are loaded successfully
            self.assertEqual(prompts['welcome_message'], 'Welcome! Please choose your language. 欢迎！请选择您的语言。')  # Example assertion for welcome message

        # Mock user response for language preference
        self.messaging_service_mock.receive_message.return_value = "zh"

        # Call complete_onboarding asynchronously
        handler.complete_onboarding(session_id)
        # Verify that handle_user_input is called with the correct parameters for each prompt
        expected_calls = [
            unittest.mock.call(session_id, "welcome_message", {"language": "zh"}),
            unittest.mock.call(session_id, "name_prompt", {"preferred_name": "John"}),
            unittest.mock.call(session_id, "age_prompt", {"age": "30"}),
            unittest.mock.call(session_id, "country_prompt", {"country": "USA"}),
            unittest.mock.call(session_id, "begin_story", {}),
        ]
        mock_session_repo.handle_user_input.assert_has_calls(expected_calls, any_order=False)

        # Verify that create_user is called with the correct user data
        expected_user_data = {
            "preferred_name": "John",
            "age": 30,
            "country": "USA",
            "mobile_number": mobile_number,
            "preferences": {"language": "zh"}
        }
        mock_user_repo.create_user.assert_called_once_with(expected_user_data)

        # Verify that send_message is called with the "begin_story" prompt
        messaging_service_mock.send_message.assert_called_with(session_id, "Click 'Begin' to start the story.")

        # Ensure that TwilioWhatsAppAdapter is used
        mock_twilio_adapter.assert_called_once()

        # Print the displayed prompts for verification
        print("Displayed prompts:")
        for call in messaging_service_mock.send_message.call_args_list:
            args, _ = call
            session_id, prompt = args
            print(prompt)
