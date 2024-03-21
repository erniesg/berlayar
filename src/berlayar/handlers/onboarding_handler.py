from berlayar.dataops.session_repository import SessionRepository
from berlayar.dataops.user_repository import UserRepository
from berlayar.dataops.storage.firebase_storage import FirebaseStorage  # Import FirebaseStorage
from berlayar.adapters.messaging.interface import MessagingInterface
from berlayar.adapters.messaging.twilio_whatsapp import TwilioWhatsAppAdapter  # Import Twilio WhatsApp adapter
from berlayar.utils.common import sync_wrapper
import os

class OnboardingHandler:
    def __init__(self, session_repo: SessionRepository, user_repo: UserRepository, messaging_service: MessagingInterface, storage=None):
        self.session_repo = session_repo
        self.user_repo = user_repo
        self.messaging_service = messaging_service if messaging_service else TwilioWhatsAppAdapter()
        self.storage = storage if storage else FirebaseStorage()

    def load_instructions(self, language=None):
        # Get the Firebase Storage URL from environment variables
        firebase_storage_url = os.getenv('FIREBASE_STORAGE_URL')
        if not firebase_storage_url:
            raise ValueError("FIREBASE_STORAGE_URL environment variable not set.")

        # Construct the full URL for instructions.json
        instructions_url = f"{firebase_storage_url}/instructions.json"

        # Load instructions from Firebase Storage using the 'storage' attribute
        instructions = self.storage.load_data(instructions_url)

        # Select instructions based on the specified language
        if language:
            if language in instructions:
                return instructions[language]
            else:
                raise ValueError(f"Instructions not available for language '{language}'.")
        else:
            return instructions

    def start_onboarding(self, mobile_number: str) -> str:
        print("Received mobile number:", mobile_number)
        user_data = self.user_repo.get_user(mobile_number)
        print("User data retrieved from repository:", user_data)

        if user_data:
            raise ValueError(f"User with mobile number {mobile_number} already exists.")

        session_id = self.session_repo.create_session({
            "user_id": None,
            "user_inputs": [{"mobile_number": mobile_number}],
        })
        session_id = mobile_number
        print("Created session ID:", session_id)

        return session_id

    def handle_user_input(self, session_id: str, step: str, input_data: dict) -> bool:
        print("Received user input:", input_data)  # Print the input data for debugging
        # Get the session from the repository
        session = self.session_repo.get_session(session_id)

        # Convert session to a dictionary
        session_dict = session.dict()

        print("Original session data:", session_dict)  # Print the original session data for debugging

        # Check if the session exists
        if not session_dict:
            # If session does not exist, create a new session
            session_dict = {"user_inputs": [], "current_step": step}
        else:
            # Ensure that 'user_inputs' key exists in the session dictionary
            if 'user_inputs' not in session_dict:
                session_dict['user_inputs'] = []

        # Add the input data to the session
        session_dict["user_inputs"].append({"step": step, "input": input_data})
        session_dict["current_step"] = step

        print("Updated session data:", session_dict)  # Print the updated session data for debugging

        # Update the session in the repository
        self.session_repo.update_session(session_id, session_dict)  # Ensure await here

        return True

    def complete_onboarding(self, session_id: str) -> str:
        # Load default welcome message in English
        user_inputs = self.session_repo.get_session(session_id)["user_inputs"][0]
        mobile_number = user_inputs.get("mobile_number")
        prompts = self.load_instructions(language="en")
        welcome_message = prompts.get("welcome_message")
        print("Sending welcome message:", welcome_message)

        sync_wrapper(self.messaging_service.send_message, session_id, welcome_message)

        # Listen for user response and update language preference in session
        user_response = sync_wrapper(self.messaging_service.receive_message, session_id)

        language = None

        # Check if the user's response is one of the supported languages
        if user_response.lower() == "en":
            language = "en"
        elif user_response.lower() == "zh":
            language = "zh"
        else:
            # If the user's response is not one of the supported languages, default to English
            sync_wrapper(self.messaging_service.send_message, session_id, "Sorry, we couldn't understand your language preference. Defaulting to English.")
            language = "en"

        # Handle user input for language preference
        self.handle_user_input(session_id, "welcome_message", {"language": language})

        # Load prompts for the selected language
        prompts = self.load_instructions(language=language)

        # Display language-specific prompts and collect user information asynchronously
        user_data = {
            "preferred_name": user_inputs.get("preferred_name"),
            "age": user_inputs.get("age"),
            "country": user_inputs.get("country"),
            "mobile_number": mobile_number,
            "preferences": {"language": language}  # Include language preference in preferences
        }
        for key, field in [("name_prompt", "preferred_name"), ("age_prompt", "age"), ("country_prompt", "country")]:
            prompt = prompts.get(key)
            sync_wrapper(self.messaging_service.send_message, session_id, prompt)

            # Listen for user response and store in user_data
            user_response = sync_wrapper(self.messaging_service.receive_message, session_id)
            user_data[field] = user_response

            # Handle user input for each prompt
            self.handle_user_input(session_id, key, {field: user_response})

        # Call create_user normally since it's not async
        user_id = self.user_repo.create_user(user_data)

        # Display "begin_story" prompt
        begin_story_prompt = prompts.get("begin_story")
        sync_wrapper(self.messaging_service.send_message, session_id, begin_story_prompt)

        # Return user ID with a success message
        return f"User created with ID: {user_id}"
