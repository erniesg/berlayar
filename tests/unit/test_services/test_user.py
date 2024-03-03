# berlayar/tests/unit/test_services/user.py
import pytest
from berlayar.schemas.user import UserModel, UserPreferences
from berlayar.services.user import User

# Fixture for user data
@pytest.fixture
def sample_user_model():
    return UserModel(
        preferred_name="John Doe",
        age=30,
        email="john.doe@example.com",
        location="Earth",
        mobile_number="1234567890",
        preferences=UserPreferences(image_gen_model="DALL·E 3", language="en")
    )

def test_create_user_with_valid_data(sample_user_model):
    user = User(sample_user_model)
    assert user.info["preferred_name"] == sample_user_model.preferred_name
    assert user.info["age"] == sample_user_model.age
    assert user.info["email"] == sample_user_model.email
    assert user.info["location"] == sample_user_model.location
    assert user.info["mobile_number"] == sample_user_model.mobile_number
    assert user.info["preferences"] == sample_user_model.preferences.dict()

def test_update_user_preferences(sample_user_model):
    user = User(sample_user_model)
    new_preferences = {"image_gen_model": "SDXL (Local)", "language": "fr"}
    user.update_preferences(new_preferences)
    assert user.info["preferences"]["image_gen_model"] == "SDXL (Local)"
    assert user.info["preferences"]["language"] == "fr"

def test_required_fields_not_empty(sample_user_model):
    # Pydantic itself handles validation, so here we test Pydantic's validation indirectly
    with pytest.raises(ValueError):
        UserModel(preferred_name="", age=0)  # This should raise an error due to invalid data

def test_retrieve_user_info(sample_user_model):
    user = User(sample_user_model)
    user_info = user.info  # Act: Retrieve user information

    # Assert: Verify all user information is correctly retrieved
    assert user_info["preferred_name"] == sample_user_model.preferred_name
    assert user_info["age"] == sample_user_model.age
    assert user_info["email"] == sample_user_model.email
    assert user_info["location"] == sample_user_model.location
    assert user_info["mobile_number"] == sample_user_model.mobile_number
    assert user_info["preferences"] == sample_user_model.preferences.dict()
