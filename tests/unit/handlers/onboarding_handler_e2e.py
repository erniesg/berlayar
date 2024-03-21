import json
import pytest
from unittest.mock import patch, AsyncMock, call
from berlayar.dataops.session_repository import SessionRepository
from berlayar.dataops.user_repository import UserRepository
from berlayar.handlers.onboarding_handler import OnboardingHandler
from berlayar.adapters.messaging.interface import MessagingInterface
from berlayar.utils.path import construct_path_from_root

@pytest.mark.asyncio
@patch('berlayar.dataops.storage.firebase_storage.FirebaseStorage.load_data')
async def test_complete_onboarding(mock_load_data):
    # Mocking session and user repositories
    session_repo_mock = AsyncMock(spec=SessionRepository)
    user_repo_mock = AsyncMock(spec=UserRepository)

    # Mocking the messaging service
    messaging_service_mock = AsyncMock(spec=MessagingInterface)

    # Mocking the loading of instructions
    instructions_file_path = construct_path_from_root("raw_data/instructions.json")
    with open(instructions_file_path, 'r', encoding='utf-8') as file:
        instructions_content = json.load(file)
    mock_load_data.return_value = instructions_content

    # Ensure that get_user returns None to simulate a non-existing user
    user_repo_mock.get_user.return_value = None

    # Initialize the OnboardingHandler with the mocked dependencies
    onboarding_handler = OnboardingHandler(session_repo_mock, user_repo_mock, messaging_service_mock)

    # Start the onboarding process to obtain the session_id
    mobile_number = "1234567890"  # Mobile number to start onboarding
    session_id = await onboarding_handler.start_onboarding(mobile_number)

    # Verify that the session was created correctly
    session_repo_mock.create_session.assert_called_once()

    # Simulate the onboarding process by sending prompts and receiving user responses
    prompts = instructions_content['en']  # Assuming 'en' was selected
    expected_messages = [
        prompts['welcome_message'],
        prompts['name_prompt'],
        prompts['age_prompt'],
        prompts['country_prompt'],
        prompts['begin_story']
    ]
    for i, message in enumerate(expected_messages):
        # Simulate sending a message and receiving user input
        response = simulate_user_input(onboarding_handler, session_id, message, i)
        if i == 0:
            assert response.lower() in ['en', 'zh']
        elif i == 1:
            assert response == "John Doe"
        elif i == 2:
            assert response == "30"
        elif i == 3:
            assert response == "USA"

    # Execute the complete_onboarding process
    await onboarding_handler.complete_onboarding(session_id)

    # Verify that the user was created with the correct data
    user_repo_mock.create_user.assert_called_once_with({
        "preferred_name": "John Doe",
        "age": "30",
        "country": "USA",
        "mobile_number": mobile_number,  # Ensure session ID is used as the mobile number
        "preferences": {"language": "en"}  # Assuming 'en' was selected as the language
    })

    # Verify that the session was updated with the correct data
    expected_session_data = {
        "user_inputs": [
            {"mobile_number": mobile_number},
            {"step": "welcome_message", "input": {"language": "en"}},
            {"step": "name_prompt", "input": {"preferred_name": "John Doe"}},
            {"step": "age_prompt", "input": {"age": "30"}},
            {"step": "country_prompt", "input": {"country": "USA"}}
        ],
        "current_step": "begin_story"
    }
    session_repo_mock.update_session.assert_called_once_with(session_id, expected_session_data)

    # Verify that the correct messages were sent to the user
    assert messaging_service_mock.send_message.call_count == len(expected_messages)
    for i, message in enumerate(expected_messages):
        assert messaging_service_mock.send_message.call_args_list[i] == call(session_id, message)

async def simulate_user_input(onboarding_handler, session_id, message, index):
    """
    Simulates receiving user input based on the prompt message received.
    """
    if index == 0:  # Language prompt
        response = "en"
    elif index == 1:  # Name prompt
        response = "John Doe"
    elif index == 2:  # Age prompt
        response = "30"
    elif index == 3:  # Country prompt
        response = "USA"
    else:
        # Simulate receiving input from the user (assumed to be the begin_story prompt)
        response = "Proceed to begin the story"
    await onboarding_handler.messaging_service.receive_message(session_id, message)
    return response
