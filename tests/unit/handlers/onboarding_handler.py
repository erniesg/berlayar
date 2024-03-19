import unittest
from unittest.mock import MagicMock, patch, ANY
from berlayar.dataops.session_repository import SessionRepository
from berlayar.dataops.user_repository import UserRepository
from berlayar.handlers.onboarding_handler import OnboardingHandler

class TestOnboardingHandler(unittest.TestCase):
    def setUp(self):
        # Mock repositories
        self.session_repo_mock = MagicMock(spec=SessionRepository)
        self.user_repo_mock = MagicMock(spec=UserRepository)

        # Create an instance of OnboardingHandler using the mocked repositories
        self.onboarding_handler = OnboardingHandler(self.session_repo_mock, self.user_repo_mock)

    def test_load_instructions(self):
        # Mock data for FirebaseStorage load_data method
        instructions_data = '{"instructions": "This is a test instruction."}'
        mocked_storage = MagicMock()
        mocked_storage.load_data.return_value = {'data': instructions_data}

        # Create an instance of OnboardingHandler using the mocked storage
        onboarding_handler = OnboardingHandler(self.session_repo_mock, self.user_repo_mock, storage=mocked_storage)

        # Call the load_instructions method
        instructions = onboarding_handler.load_instructions()

        # Assertions
        self.assertEqual(instructions, {'data': instructions_data})

    def test_start_onboarding_user_exists(self):
        # Mock that the user already exists
        self.user_repo_mock.get_user.return_value = {"user_id": "existing_user_id"}
        onboarding_handler = OnboardingHandler(self.session_repo_mock, self.user_repo_mock)

        # Test start_onboarding method
        with self.assertRaises(ValueError):
            onboarding_handler.start_onboarding("existing_mobile_number")  # Provide existing mobile number

    def test_start_onboarding_new_user(self):
        # Mock that the user does not exist
        self.user_repo_mock.get_user.return_value = None
        # Mock the session creation
        self.session_repo_mock.create_session.return_value = "mock_session_id"

        onboarding_handler = OnboardingHandler(self.session_repo_mock, self.user_repo_mock)

        # Test start_onboarding method
        new_mobile_number = "new_mobile_number 12345678"
        print("Starting onboarding for new user with mobile number:", new_mobile_number)
        result = onboarding_handler.start_onboarding(new_mobile_number)

        # Assert that a new session ID is returned
        expected_session_id = "mock_session_id"
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
        mock_session = MagicMock()
        mock_session.dict.return_value = {"user_inputs": [], "current_step": None}
        self.session_repo_mock.get_session.return_value = mock_session

        # Test handle_user_input method
        result = self.onboarding_handler.handle_user_input(session_id, step, input_data)

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

    def test_complete_onboarding(self):
        # Mock data
        session_id = "mock_session_id"
        user_id = "mock_user_id"

        # Mock the session returned by the repository
        mock_session = MagicMock(spec="Session")
        mock_session.user_id = None  # Simulate a session without a user ID
        self.session_repo_mock.get_session.return_value = mock_session

        # Mock the user data extracted from the session
        user_data = {
            "preferred_name": "John Doe",
            "mobile_number": "1234567890",
            "age": 30,
            "country": "USA"
        }

        # Test complete_onboarding method
        result = self.onboarding_handler.complete_onboarding(session_id)

        # Assert repository method calls
        self.session_repo_mock.get_session.assert_called_once_with(session_id)
        self.user_repo_mock.create_user.assert_called_once_with(
            preferred_name=user_data["preferred_name"],
            mobile_number=user_data["mobile_number"],
            age=user_data["age"],
            country=user_data["country"]
        )

        # Assert result
        self.assertEqual(result, user_id)

if __name__ == "__main__":
    unittest.main()
