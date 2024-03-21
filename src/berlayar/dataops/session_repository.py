# berlayar/dataops/session_repository.py

import os
from abc import ABC, abstractmethod
from berlayar.dataops.interface import StorageInterface, SessionRepositoryInterface
from berlayar.schemas.session import Session

class SessionRepository(SessionRepositoryInterface):
    def __init__(self, storage: StorageInterface):
        self.storage = storage
        self.session_collection_name = os.getenv('SESSION_COLLECTION_NAME', 'sessions')

    def create_session(self, session_data: dict) -> str:
        # Exclude the session_id during initial creation as it's not known yet
        session_data.pop("session_id", None)  # Ensure session_id is not in dict

        # Create a Session object from the session_data
        session = Session(**session_data)

        # Save the session data to Firestore and obtain the document ID
        doc_id = self.storage.save_data(self.session_collection_name, session.dict())

        # Optionally update the Firestore document with the session_id if needed
        self.storage.update_data(self.session_collection_name, doc_id, {"session_id": doc_id})

        return doc_id

    def update_session(self, session_id: str, session_data: dict):
        print("Updating session with ID:", session_id)
        print("Session data to update:", session_data)
        self.storage.update_data(self.session_collection_name, session_id, session_data)
        return session_data  # Return the updated session data

    def get_session(self, session_id: str) -> Session:
        # Retrieve session data from Firestore using the session_id
        session_data = self.storage.load_data(self.session_collection_name, session_id)

        # Check if session_data is not empty
        if session_data:
            # Convert the retrieved data into a Session model instance
            session = Session(**session_data)
            return session
        else:
            # Handle the case where no session is found for the given session_id
            raise ValueError(f"No session found with ID: {session_id}")

    def delete_session(self, session_id: str):
        pass
