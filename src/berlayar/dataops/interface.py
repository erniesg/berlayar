# berlayar/dataops/interface.py

from abc import ABC, abstractmethod

class UserRepositoryInterface(ABC):
    @abstractmethod
    def get_user(self, identifier):
        pass

    @abstractmethod
    def create_user(self, user_data):
        pass

    @abstractmethod
    def update_user(self, identifier, user_data):
        pass

    @abstractmethod
    def delete_user(self, identifier):
        pass

class StorageInterface(ABC):
    @abstractmethod
    def save_data(self, data):
        pass

    @abstractmethod
    def load_data(self, identifier):
        pass

    @abstractmethod
    def update_data(self, identifier, data):
        pass

    @abstractmethod
    def delete_data(self, identifier):
        pass

class SessionRepositoryInterface(ABC):
    @abstractmethod
    def create_session(self, session_data):
        pass

    @abstractmethod
    def update_session(self, session_id, session_data):
        pass

    @abstractmethod
    def get_session(self, session_id):
        pass

    @abstractmethod
    def delete_session(self, session_id):
        pass
