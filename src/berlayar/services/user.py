from berlayar.schemas.user import UserModel
import logging

class User:
    def __init__(self, storages=None, subdirectory="users"):
        self.storages = storages or []
        self.subdirectory = subdirectory
        self.logger = logging.getLogger(__name__)  # Define logger attribute

    async def create_user(self, user_data: dict):
        """
        Creates a new user and saves the user data to multiple storage locations.
        """
        try:
            new_user = UserModel(**user_data)
            for storage in self.storages:
                try:
                    storage.save_data(f"{new_user.user_id}.json", new_user.dict(), subdirectory=self.subdirectory)
                except Exception as e:
                    print(f"Failed to save user data to {storage}: {e}")
                    # Log the exception for further analysis
                    self.logger.error(f"Failed to save user data to {storage}: {e}")
            return new_user
        except Exception as e:
            print(f"Failed to create user: {e}")
            # Log the exception for further analysis
            self.logger.error(f"Failed to create user: {e}")
            return None

    def update_preferences(self, user_id: str, new_preferences: dict):
        """
        Updates user preferences and saves the updated preferences to multiple storage locations.
        """
        existing_user_data = self.get_user_info(user_id)
        if existing_user_data:
            updated_preferences = {**existing_user_data.get('preferences', {}), **new_preferences}
            for storage in self.storages:
                try:
                    storage.save_data(f"{self.subdirectory}/{user_id}.json", updated_preferences, subdirectory=self.subdirectory)
                except Exception as e:
                    print(f"Failed to update user preferences in {storage}: {e}")
            return updated_preferences
        return None

    def get_user_info(self, user_id: str):
        """
        Retrieve user information from the first available storage location.
        """
        for storage in self.storages:
            user_data = storage.load_data(f"{self.subdirectory}/{user_id}.json")
            if user_data:
                return user_data
        return None

    @property
    def info(self):
        """
        Retrieve user information from the first available storage location.
        """
        for storage in self.storages:
            user_data = storage.load_data(f"{self.subdirectory}/{self.user_data.user_id}.json")
            if user_data:
                return user_data
        return None

    def update_user(self, user_id: str, updated_data: dict):
        """
        Update user information and save the updated data to multiple storage locations.
        """
        existing_user_data = self.get_user_info(user_id)
        if existing_user_data:
            updated_user_data = {**existing_user_data, **updated_data}
            for storage in self.storages:
                try:
                    storage.save_data(f"{self.subdirectory}/{user_id}.json", updated_user_data, subdirectory=self.subdirectory)
                except Exception as e:
                    print(f"Failed to update user data in {storage}: {e}")
            return updated_user_data
        return None
