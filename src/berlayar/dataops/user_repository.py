# berlayar/dataops/user_repository.py

import os
from pydantic import ValidationError
from berlayar.schemas.user import UserModel
from berlayar.dataops.interface import UserRepositoryInterface
from berlayar.dataops.interface import StorageInterface

class UserRepository(UserRepositoryInterface):
    def __init__(self, storage: StorageInterface):
        self.storage = storage
        self.user_collection_name = os.getenv('USER_COLLECTION_NAME', 'users')

    def get_user(self, identifier):
        # Fetch user data from the storage based on the identifier asynchronously
        print("Fetching user with identifier:", identifier)
        user_data = self.storage.load_data(self.user_collection_name, identifier)
        if user_data:
            return user_data
        else:
            # If user data is not found, return None
            return None

    def create_user(self, user_data: dict) -> str:
        try:
            # Validate user data with Pydantic model
            user = UserModel(**user_data)
            # Save user data to the specified collection
            user_id = self.storage.save_data(self.user_collection_name, user.dict(exclude_unset=True))
            print("User created successfully:", user_id)
            return user_id
        except ValidationError as e:
            missing_fields = ', '.join([error['loc'][0] for error in e.errors()])
            error_message = f"Missing required fields: {missing_fields}"
            raise ValueError(error_message) from e

    def update_user(self, identifier, user_data):
        # Fetch existing user data from the storage based on the identifier
        existing_user_data = self.storage.load_data(self.user_collection_name, identifier)
        if existing_user_data:
            # Merge existing user data with new user data for update
            updated_user_data = {**existing_user_data, **user_data}
            # Save the updated user data back to the storage
            self.storage.update_data(self.user_collection_name, identifier, updated_user_data)
        else:
            raise ValueError("User not found.")

    def delete_user(self, identifier):
        # Implement logic to delete a user
        # Use the storage object to interact with the database
        pass
