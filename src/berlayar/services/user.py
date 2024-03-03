from berlayar.schemas.user import UserModel

class User:
    def __init__(self, storages=None):
        self.storages = storages or []

    def create_user(self, user_data: dict):
        """
        Creates a new user and saves the user data to multiple storage locations.
        """
        new_user = UserModel(**user_data)
        for storage in self.storages:
            try:
                storage.save_data(f"{new_user.user_id}.json", new_user.dict())
            except Exception as e:
                print(f"Failed to save user data to {storage}: {e}")
        return new_user

    def update_preferences(self, user_id: str, new_preferences: dict):
        """
        Updates user preferences and saves the updated preferences to multiple storage locations.
        """
        existing_user_data = self.get_user_info(user_id)
        if existing_user_data:
            updated_preferences = {**existing_user_data.get('preferences', {}), **new_preferences}
            for storage in self.storages:
                try:
                    storage.save_data(f"{user_id}.json", updated_preferences)  # Updated to use updated_preferences
                except Exception as e:
                    print(f"Failed to update user preferences in {storage}: {e}")
            return updated_preferences  # Return updated_preferences instead of existing_user_data
        return None

    def get_user_info(self, user_id: str):
        """
        Retrieve user information from the first available storage location.
        """
        for storage in self.storages:
            user_data = storage.load_data(f"{user_id}.json")
            if user_data:
                return user_data
        return None

    @property
    def info(self):
        """
        Retrieve user information from the first available storage location.
        """
        for storage in self.storages:
            user_data = storage.load_data(f"{self.user_data.user_id}.json")
            if user_data:
                return user_data
        return None
