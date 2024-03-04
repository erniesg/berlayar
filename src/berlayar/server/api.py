from fastapi import APIRouter, HTTPException, Depends
from berlayar.schemas.user import UserModel
from berlayar.services.user import User
from berlayar.services.session import Session
from berlayar.utils.load_keys import load_environment_variables

router = APIRouter()

# Load environment variables
load_environment_variables()

# Initialize User and Session services
user_service = User()
session_service = Session(user_service)

@router.post("/users/", response_model=UserModel, status_code=201)
async def create_user(user_data: dict):
    """
    Endpoint to create a new user.
    """
    # Extract mobile_number from user_id
    user_id = user_data.get("user_id", "")
    mobile_number = user_id.split(":")[-1]  # Extract the number after "whatsapp:"

    # Populate user data with mobile_number and initialize other fields with blank values
    user_data["mobile_number"] = mobile_number
    user_data.setdefault("preferred_name", "")
    user_data.setdefault("age", "")
    user_data.setdefault("email", "")
    user_data.setdefault("location", "")
    user_data.setdefault("preferences", {})

    # Create the user
    user = user_service.create_user(user_data)
    if user:
        return user
    else:
        raise HTTPException(status_code=400, detail="Failed to create user.")

@router.post("/sessions/", status_code=201)
async def create_session(user_data: dict):
    """
    Endpoint to create a new session for a user.
    """
    session = session_service.create_session(user_data)
    if session:
        return {"message": "Session created successfully."}
    else:
        raise HTTPException(status_code=400, detail="Failed to create session.")
