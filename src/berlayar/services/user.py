# berlayar/src/berlayar/services/user.py
from berlayar.schemas.user import UserModel, UserPreferences

class User:
    def __init__(self, user_data: UserModel, storage=None):
        self.user_data = user_data
        self.storage = storage

    def update_preferences(self, new_preferences: dict):
        # Update only the preferences part of the UserModel
        updated_preferences_model = UserPreferences(**{**self.user_data.preferences.dict(), **new_preferences})
        self.user_data = self.user_data.copy(update={"preferences": updated_preferences_model})

    @property
    def info(self):
        return self.user_data.dict()
