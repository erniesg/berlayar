from berlayar.dataops.session_repository import SessionRepository
from berlayar.dataops.user_repository import UserRepository
from berlayar.dataops.storage.firebase_storage import FirebaseStorage  # Import FirebaseStorage
import os

class OnboardingHandler:
    def __init__(self, session_repo: SessionRepository, user_repo: UserRepository, storage=None):
        self.session_repo = session_repo
        self.user_repo = user_repo
        self.storage = storage if storage else FirebaseStorage()

    def load_instructions(self) -> dict:
        # Get the Firebase Storage URL from environment variables
        firebase_storage_url = os.getenv('FIREBASE_STORAGE_URL')
        if not firebase_storage_url:
            raise ValueError("FIREBASE_STORAGE_URL environment variable not set.")

        # Construct the full URL for instructions.json
        instructions_url = f"{firebase_storage_url}/instructions.json"

        # Load instructions from Firebase Storage using the 'storage' attribute
        instructions = self.storage.load_data(instructions_url)
        return instructions

    def start_onboarding(self, mobile_number: str) -> str:
        # Check if the user with the given mobile number exists
        print("Received mobile number:", mobile_number)
        user_data = self.user_repo.get_user(mobile_number)
        print("User data retrieved from repository:", user_data)

        if user_data:
            # User already exists, handle accordingly
            # You can raise an exception or return a message indicating that the user already exists
            raise ValueError("User with mobile number {} already exists.".format(mobile_number))

        # User does not exist, create a new session for onboarding
        session_id = self.session_repo.create_session({
            "user_id": None,
            "user_inputs": [{"mobile_number": mobile_number}],
        })
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
        self.session_repo.update_session(session_id, session_dict)

        return True

    def complete_onboarding(self, session_id: str) -> str:
        # Complete the onboarding process and create a new user
        pass
