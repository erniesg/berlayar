# berlayar/dataops/session_repository.py

import os
from berlayar.dataops.interface import StorageInterface, SessionRepositoryInterface
from berlayar.schemas.session import Session
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SessionRepository(SessionRepositoryInterface):
    def __init__(self, storage: StorageInterface):
        self.storage = storage
        self.session_collection_name = os.getenv('SESSION_COLLECTION_NAME', 'sessions')

    def create_session(self, session_data: dict) -> str:
        logging.debug("[create_session] Initial session data: %s", session_data)

        # Exclude the session_id during initial creation as it's not known yet
        session_data.pop("session_id", None)

        # Ensure the mobile number is included at the root level of session_data
        # This assumes 'mobile_number' is already part of session_data passed to this method
        if 'user_inputs' in session_data:
            for input_item in session_data['user_inputs']:
                if 'input' in input_item and 'mobile_number' in input_item['input']:
                    # Move the mobile number to the root level of session_data
                    session_data['mobile_number'] = input_item['input']['mobile_number']
                    break  # Assuming only one mobile number entry is present

        # Create a Session object from the session_data
        session = Session(**session_data)

        # Save the session data to Firestore and obtain the document ID
        doc_id = self.storage.save_data(self.session_collection_name, session.dict())
        logging.debug("[create_session] Session saved. Document ID: %s", doc_id)

        # Optionally update the Firestore document with the session_id if needed
        self.storage.update_data(self.session_collection_name, doc_id, {"session_id": doc_id})
        logging.debug("[create_session] Session ID updated in Firestore document.")

        return doc_id

    def update_session(self, session_id: str, session_data: dict):
        logging.debug(f"[update_session] Updating session with ID: {session_id}, Session data to update: {session_data}")
        session_data = session_data.dict() if hasattr(session_data, 'dict') else session_data

        self.storage.update_data(self.session_collection_name, session_id, session_data)
        logging.debug("[update_session] Session update completed.")
        return session_data

    def get_session(self, session_id: str) -> Session:
        logging.debug(f"[get_session] Retrieving session with ID: {session_id}")
        session_data = self.storage.load_data(self.session_collection_name, session_id)
        if session_data:
            logging.debug(f"[get_session] Session data found: {session_data}")
            return Session(**session_data)
        else:
            logging.error(f"[get_session] No session found with ID: {session_id}")
            raise ValueError(f"No session found with ID: {session_id}")

    def delete_session(self, session_id: str):
        logging.debug(f"[delete_session] Deleting session with ID: {session_id}")
        self.storage.delete_data(self.session_collection_name, session_id)
        logging.debug("[delete_session] Session deletion completed.")

    async def get_session_id_by_mobile_number(self, mobile_number: str) -> Optional[str]:
        logging.debug(f"[get_session_id_by_mobile_number] Retrieving session ID for mobile number: {mobile_number}")

        def _query_sync():
            logging.debug(f"[get_session_id_by_mobile_number] Querying Firestore for mobile number: {mobile_number}")
            sessions_ref = self.storage.db.collection(self.session_collection_name)
            query = sessions_ref.where('mobile_number', '==', mobile_number).limit(1)
            results = query.stream()
            for doc in results:
                logging.debug(f"[get_session_id_by_mobile_number] Found session with ID: {doc.id} for mobile number: {mobile_number}")
                return doc.id
            logging.debug(f"[get_session_id_by_mobile_number] No session found for the given mobile number: {mobile_number}")
            return None

        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, _query_sync)
            return result

    def get_current_step(self, session_id: str) -> str:
        logging.debug(f"[get_current_step] Determining current step for session ID: {session_id}")
        session = self.get_session(session_id)
        if session and session.user_inputs:
            # Access the 'step' attribute of the last SessionInput object in the list
            return session.user_inputs[-1].step
        else:
            logging.info(f"[get_current_step] No current step found for session ID: {session_id}")
            return None

    def is_onboarding_complete(self, session_id: str) -> bool:
        logging.debug(f"[is_onboarding_complete] Checking if onboarding is complete for session ID: {session_id}")
        session = self.get_session(session_id)
        if session and session.user_inputs:
            # Collect all steps from user inputs
            completed_steps = {input.step for input in session.user_inputs}
            # Define the set of required steps for onboarding to be considered complete
            required_steps = {"language_preference", "name_prompt", "age_prompt", "location_prompt"}
            
            # Check if all required steps are present in the completed steps
            if required_steps.issubset(completed_steps):
                logging.debug("[is_onboarding_complete] Onboarding is complete.")
                return True

        logging.debug("[is_onboarding_complete] Onboarding is not complete.")
        return False
