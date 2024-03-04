from berlayar.schemas.user import UserModel
import logging

class User:
    def __init__(self, storages=None, subdirectory="users"):
        self.storages = storages or []  # Expecting a list of storage instances
        self.subdirectory = subdirectory
        self.logger = logging.getLogger(__name__)

    async def create_user(self, user_data: dict):
        """
        Creates a new user and saves the user data to multiple storage locations.
        """
        try:
            new_user = UserModel(**user_data)
            for storage in self.storages:
                try:
                    await storage.save_data(f"{new_user.user_id}.json", new_user.dict(), subdirectory=self.subdirectory)
                    self.logger.info(f"User data saved to {storage.__class__.__name__}")
                except Exception as e:
                    self.logger.error(f"Failed to save user data to {storage.__class__.__name__}: {e}")
            return new_user
        except Exception as e:
            self.logger.error(f"Failed to create user: {e}")
            return None

    async def get_user_info(self, user_id: str):
        """
        Retrieve user information from the first available storage location.
        """
        for storage in self.storages:
            try:
                user_data = await storage.load_data(f"{user_id}.json", subdirectory=self.subdirectory)
                if user_data:
                    self.logger.info(f"User data retrieved from {storage.__class__.__name__}")
                    return user_data
            except Exception as e:
                self.logger.error(f"Failed to retrieve user data from {storage.__class__.__name__}: {e}")
        return None

    async def update_user(self, user_id: str, updated_data: dict):
        """
        Update user information and save the updated data to multiple storage locations.
        """
        existing_user_data = await self.get_user_info(user_id)
        if existing_user_data:
            # Merge existing data with updated data
            updated_user_data = existing_user_data | updated_data  # Python 3.9+ syntax for dictionaries merge
            for storage in self.storages:
                try:
                    await storage.save_data(f"{user_id}.json", updated_user_data, subdirectory=self.subdirectory)
                    self.logger.info(f"User data updated in {storage.__class__.__name__}")
                except Exception as e:
                    self.logger.error(f"Failed to update user data in {storage.__class__.__name__}: {e}")
            return updated_user_data
        self.logger.error(f"User {user_id} not found for update.")
        return None

# Remove the `info` property and `update_preferences` method if they're not needed, or adjust them similarly.
