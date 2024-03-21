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
        print("[create_session] Initial session data:", session_data)

        # Exclude the session_id during initial creation as it's not known yet
        session_data.pop("session_id", None)  # Ensure session_id is not in dict

        # Create a Session object from the session_data
        session = Session(**session_data)

        # Save the session data to Firestore and obtain the document ID
        doc_id = self.storage.save_data(self.session_collection_name, session.dict())
        print("[create_session] Session saved. Document ID:", doc_id)

        # Optionally update the Firestore document with the session_id if needed
        self.storage.update_data(self.session_collection_name, doc_id, {"session_id": doc_id})
        print("[create_session] Session ID updated in Firestore document.")

        return doc_id

    def update_session(self, session_id: str, session_data: dict):
        print(f"[update_session] Updating session with ID: {session_id}")
        print(f"[update_session] Session data to update: {session_data}")
        self.storage.update_data(self.session_collection_name, session_id, session_data)
        print("[update_session] Session update completed.")
        return session_data

    def get_session(self, session_id: str) -> Session:
        print(f"[get_session] Retrieving session with ID: {session_id}")
        session_data = self.storage.load_data(self.session_collection_name, session_id)
        if session_data:
            print(f"[get_session] Session data found: {session_data}")
            session = Session(**session_data)
            return session
        else:
            print(f"[get_session] No session found with ID: {session_id}")
            raise ValueError(f"No session found with ID: {session_id}")


    def delete_session(self, session_id: str):
        pass
