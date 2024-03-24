from berlayar.dataops.session_repository import SessionRepository
from berlayar.dataops.user_repository import UserRepository
from berlayar.dataops.storage.firebase_storage import FirebaseStorage  # Import FirebaseStorage
from berlayar.adapters.messaging.interface import MessagingInterface
from berlayar.adapters.messaging.twilio_whatsapp import TwilioWhatsAppAdapter  # Import Twilio WhatsApp adapter
from berlayar.utils.common import sync_wrapper
import os
import json
import logging

class OnboardingHandler:
    def __init__(self, session_repo: SessionRepository, user_repo: UserRepository, messaging_service: MessagingInterface, storage=None):
        self.session_repo = session_repo
        self.user_repo = user_repo
        self.messaging_service = messaging_service if messaging_service else TwilioWhatsAppAdapter()
        self.storage = storage if storage else FirebaseStorage()

    def load_instructions(self, language=None):
        logging.debug(f"Loading instructions for language: {language}")

        # Get the Firebase Storage URL from environment variables
        firebase_storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')
        if not firebase_storage_bucket:
            raise ValueError("FIREBASE_STORAGE_BUCKET environment variable not set.")

        # Construct the full URL for instructions.json
        file_name = "instructions.json"

        # Load instructions from Firebase Storage using the 'storage' attribute
        instructions = self.storage.load_data(file_name)
        instructions_data = json.loads(instructions['data'])

        # Select instructions based on the specified language
        if language in instructions_data:
            return instructions_data[language]
        else:
            # If the specified language is not available, default to English
            if 'en' in instructions_data:
                return instructions_data['en']
            else:
                raise ValueError(f"Instructions not available for language '{language}'.")


    def start_onboarding(self, mobile_number: str) -> str:
        logging.info(f"Starting onboarding for mobile number: {mobile_number}")

        print("Received mobile number:", mobile_number)
        user_data = self.user_repo.get_user(mobile_number)
        print("User data retrieved from repository:", user_data)

        if user_data:
            raise ValueError(f"User with mobile number {mobile_number} already exists.")

        initial_step = "onboarding_start"
        initial_input = {"mobile_number": mobile_number}

        # Create the session with the mobile number at the root level and structured user_inputs
        session_id = self.session_repo.create_session({
            "mobile_number": mobile_number,  # Save the mobile number at the root level
            "user_id": None,
            "user_inputs": [{"step": initial_step, "input": initial_input}],
        })
        print("Created session ID:", session_id)

        session_data = self.session_repo.get_session(session_id)
        print("Session data after start_onboarding:", session_data)

        # Send a welcome message with language selection prompt
        welcome_message = "Welcome to our service! Please reply with 'EN' for English or 'ZH' for Chinese."
        self.messaging_service.send_message(mobile_number, welcome_message)

        return session_id

    async def handle_user_input(self, session_id: str, step: str, input_data: dict) -> bool:
        logging.info(f"Handling user input for session ID: {session_id}, step: {step}")
        print(f"Received user input for step: {step} with data: {input_data}")
        # Get the session from the repository
        session = self.session_repo.get_session(session_id)

        if not session:
            print("Session not found")
            raise ValueError("Session not found")

        # Determine the next step based on the current step and input_data
        current_step = getattr(session, 'current_step', 'onboarding_start')
        logging.info(f"Current step before determining next: {current_step}")

        next_step = self.determine_next_step(current_step, input_data)
        logging.info(f"Determined next step: {next_step} based on current step: {current_step} and input data")

        # Update the session with the new input using current_step instead of the step parameter
        if hasattr(session, 'user_inputs') and isinstance(session.user_inputs, list):
            session.user_inputs.append({"step": current_step, "input": input_data})  # Use current_step here
        else:
            logging.error("Session object does not have 'user_inputs' or it's not a list")
            return False

        # Update the session with the language preference if applicable
        if current_step == "language_preference":
            language = input_data.get('text_body', '').lower()
            if language in ['en', 'zh']:
                # Ensure preferences is initialized
                if not hasattr(session, 'preferences'):
                    session.preferences = {}
                # Directly modify the preferences attribute
                session.preferences['language'] = language
            else:
                prompt = "Please reply with 'EN' for English or 'ZH' for Chinese."
                self.messaging_service.send_message(session.mobile_number, prompt)
                return False

        # Update the session with the current step
        session.current_step = next_step
        self.session_repo.update_session(session_id, session)

        # Send the next prompt if applicable
        if next_step:
            # Ensure preferences is initialized and has a 'language' key
            language = getattr(session, 'preferences', {}).get('language', 'en')
            prompt = self.load_instructions(language=language).get(next_step, "Next step not found.")
            self.messaging_service.send_message(session.mobile_number, prompt)

        return True

    def determine_next_step(self, current_step: str, input_data: dict) -> str:
        logging.debug(f"Determining next step from current step: {current_step}")

        # Mapping of current step to the next step
        step_flow = {
            "onboarding_start": "language_preference",
            "language_preference": "name_prompt",
            "name_prompt": "age_prompt",
            "age_prompt": "location_prompt",
            "location_prompt": None  # Indicates the end of the onboarding process
        }

        # Determine the next step based on the current step
        next_step = step_flow.get(current_step)

        # Optionally, handle input_data for more complex flows
        # For example, if input_data should influence what the next step is

        return next_step

    async def complete_onboarding(self, session_id: str) -> str:
        logging.info(f"Completing onboarding for session ID: {session_id}")

        # Retrieve the session object
        session = self.session_repo.get_session(session_id)
        # Access the 'user_inputs' attribute of the session object
        if session and 'user_inputs' in session and session['user_inputs']:
            user_input = session['user_inputs'][-1]  # Get the last user input
            if user_input and 'input' in user_input and 'mobile_number' in user_input['input']:
                mobile_number = user_input['input']['mobile_number']        
            else:
                # Handle the case where the mobile number is not present
                raise ValueError("Mobile number not found in session inputs.")
        else:
            # Handle the case where there are no user inputs
            raise ValueError("No user inputs found in session.")

        # Load prompts for the selected language
        language = session.get('preferences', {}).get('language', 'en')  # Default to English if no language preference is found
        prompts = self.load_instructions(language=language)

        user_data = {
            "mobile_number": mobile_number,
            "preferences": {
                "language": language  # Include the language preference
            }
        }

        # Extract the user data from the collected inputs
        for input_item in session['user_inputs']:
            input_step = input_item.get("step")
            input_value = input_item.get("input")
            if input_step in ["name_prompt", "age_prompt", "location"]:
                # Convert dict_values to a list before subscripting
                user_data[list(input_value.keys())[0]] = list(input_value.values())[0]

        # Call create_user with the collected user data
        user_id = self.user_repo.create_user(user_data)

        # Display "begin_story" prompt
        begin_story_prompt = prompts.get("begin_story")
        self.messaging_service.send_message(mobile_number, begin_story_prompt)  # Corrected call

        # Return user ID with a success message
        return f"User created with ID: {user_id}"