import unittest
from unittest.mock import MagicMock, patch, call
from berlayar.handlers.onboarding_handler import OnboardingHandler

class TestCompleteOnboardingFlow(unittest.TestCase):
    @patch('berlayar.dataops.session_repository.SessionRepository.update_session')
    @patch('berlayar.adapters.messaging.twilio_whatsapp.TwilioWhatsAppAdapter', autospec=True)
    @patch('berlayar.dataops.storage.firebase_storage.FirebaseStorage.load_data')
    @patch('berlayar.dataops.user_repository.UserRepository')
    @patch('berlayar.dataops.session_repository.SessionRepository')
    def test_end_to_end_onboarding(self, mock_session_repo, mock_user_repo, mock_load_data, mock_twilio_adapter, mock_update_session):
        # Load data for language prompts
        mock_load_data.return_value = {
            "en": {
                "welcome_message": "Welcome!",
                "name_prompt": "What's your name?",
                "age_prompt": "How old are you?",
                "country_prompt": "What's your country?"
            },
            "zh": {
                "welcome_message": "欢迎!",
                "name_prompt": "你叫什么名字？",
                "age_prompt": "你多大了？",
                "country_prompt": "你的国家是？"
            }
        }
        # Simulate user input for each step

        # Simulate session data storage
        session_data = {}
        def update_session_mock(session_id, data):
            session_data[session_id] = data
        mock_session_repo.return_value.update_session.side_effect = update_session_mock
        # Mock the get_session method to return a session with the expected user_inputs
        def get_session_mock(session_id):
            return session_data.get(session_id, {"user_inputs": [{"mobile_number": "1234567890"}], "current_step": "language"})
        mock_session_repo.return_value.get_session.side_effect = get_session_mock
        # Simulate user repository behavior
        mock_user_repo.return_value.get_user.return_value = None
        mock_user_repo.return_value.create_user.return_value = "user_id_mock"

        # Replace the above line with a mock that has a `load_data` method, like so:
        mock_storage = MagicMock()
        mock_storage.load_data = MagicMock(return_value=mock_load_data.return_value)
        onboarding_handler = OnboardingHandler(mock_session_repo.return_value, mock_user_repo.return_value, mock_twilio_adapter.return_value, mock_storage)
        # Simulate receiving initial message "hi" which should trigger the start of onboarding
        mobile_number = "1234567890"
        received_message = {"mobile_number": mobile_number, "message": "hi"}
        mock_twilio_adapter.return_value.receive_message(received_message)
        session_id = onboarding_handler.start_onboarding(mobile_number)
        user_id = onboarding_handler.complete_onboarding(session_id)
        user_responses = ["zh", "John Doe", "25", "USA"]
        user_responses_iter = iter(user_responses)
        mock_twilio_adapter.return_value.receive_message.side_effect = lambda _: next(user_responses_iter)

        # Simulate receiving messages through the messaging service and handling user input
        step_names = ["language", "name_prompt", "age_prompt", "country_prompt"]
        for step, response in zip(step_names, user_responses):
            received_message = {"mobile_number": mobile_number, "message": response}
            mock_twilio_adapter.return_value.receive_message(received_message)
            input_data = {"message": response}  # Construct the input_data dictionary
            onboarding_handler.handle_user_input(session_id, step, input_data)
                # Assert that the user was created
        self.assertEqual(user_id, "User created with ID: user_id_mock")

if __name__ == '__main__':
    unittest.main()