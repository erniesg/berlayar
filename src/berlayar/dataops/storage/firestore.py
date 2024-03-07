from firebase_admin import credentials, firestore, initialize_app
from berlayar.dataops.interface import StorageInterface
import os
from typing import Dict, Any

class FirestoreStorage(StorageInterface):
    def __init__(self, credential_path: str = None) -> None:
        if not credential_path:
            credential_path = os.getenv('FIREBASE_KEY')
            if not credential_path:
                raise ValueError("Firebase credential path must be provided or set in FIREBASE_KEY environment variable.")
        cred = credentials.Certificate(credential_path)
        initialize_app(cred)
        self.db = firestore.client()

    def save_data(self, collection_name: str, data: Dict[str, Any]) -> str:
        doc_ref = self.db.collection(collection_name).add(data)
        print("Document reference:", doc_ref)
        return doc_ref[1].id

    def load_data(self, collection_name: str, document_id: str) -> Dict[str, Any]:
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}

    def update_data(self, collection_name: str, document_id: str, data: Dict[str, Any]) -> bool:
        self.db.collection(collection_name).document(document_id).update(data)
        return True

    def delete_data(self, collection_name: str, document_id: str) -> bool:
        self.db.collection(collection_name).document(document_id).delete()
        return True
