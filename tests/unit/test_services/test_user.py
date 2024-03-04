import pytest
from berlayar.schemas.user import UserModel, UserPreferences
from berlayar.services.user import User
from berlayar.dataops.storage.local import LocalStorage

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

@pytest.fixture
def sample_user_data():
    return {
        "preferred_name": "John Doe",
        "age": 30,
        "email": "john.doe@example.com",
        "location": "Earth",
        "mobile_number": "1234567890",
        "preferences": UserPreferences(image_gen_model="DALL·E 3", language="en").dict()
    }

@pytest.fixture
def sample_local_storage():
    return LocalStorage()

@pytest.mark.asyncio
async def test_create_user_with_valid_data(sample_user_model, sample_local_storage):
    user = User([sample_local_storage])
    created_user = await user.create_user(sample_user_model.dict())
    assert created_user.preferred_name == sample_user_model.preferred_name
    assert created_user.age == sample_user_model.age
    assert created_user.email == sample_user_model.email
    assert created_user.location == sample_user_model.location
    assert created_user.mobile_number == sample_user_model.mobile_number
    assert created_user.preferences == sample_user_model.preferences

@pytest.mark.asyncio
async def test_update_user_preferences(sample_user_data, sample_local_storage):
    user = User([sample_local_storage])
    created_user = await user.create_user(sample_user_data)
    new_preferences = {"image_gen_model": "SDXL (Local)", "language": "fr"}
    updated_preferences = await user.update_preferences(created_user.user_id, new_preferences)
    assert updated_preferences['image_gen_model'] == "SDXL (Local)"
    assert updated_preferences['language'] == "fr"

@pytest.mark.asyncio
async def test_retrieve_user_info(sample_user_data, sample_local_storage):
    user = User([sample_local_storage])
    created_user = await user.create_user(sample_user_data)
    retrieved_user_info = await user.get_user_info(created_user.user_id)
    assert retrieved_user_info["preferred_name"] == sample_user_data["preferred_name"]
    assert retrieved_user_info["age"] == sample_user_data["age"]
    assert retrieved_user_info["email"] == sample_user_data["email"]
    assert retrieved_user_info["location"] == sample_user_data["location"]
    assert retrieved_user_info["mobile_number"] == sample_user_data["mobile_number"]
    assert retrieved_user_info["preferences"] == sample_user_data["preferences"]

def test_invalid_user_data_raises_error():
    with pytest.raises(ValueError):
        UserModel(preferred_name="", age=30)  # This should raise an error due to missing required fields
