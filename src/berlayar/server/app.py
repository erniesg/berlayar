# berlayar/src/berlayar/server/app.py
from fastapi import FastAPI, Request, Form, Depends
from berlayar.adapters.messaging.twilio_whatsapp import TwilioWhatsAppAdapter
from berlayar.handlers.onboarding_handler import OnboardingHandler
from berlayar.dataops.user_repository import UserRepository
from berlayar.dataops.storage.firestore import FirestoreStorage
from berlayar.dataops.session_repository import SessionRepository
import logging
import json
from urllib.parse import parse_qs

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()
adapter = TwilioWhatsAppAdapter()
firestore_storage = FirestoreStorage()
session_repo = SessionRepository(firestore_storage)
user_repo = UserRepository(firestore_storage)
onboarding_handler = OnboardingHandler(session_repo, user_repo, adapter)

@app.post("/webhook")
async def webhook(request: Request):
    if request.headers.get('content-type') == 'application/x-www-form-urlencoded':
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8')  # Decode bytes to string
        data = parse_qs(body_str)  # Parse URL-encoded form data to dict
        # Convert lists to single values, as parse_qs returns a list for each key
        data = {k: v[0] if len(v) == 1 else v for k, v in data.items()}
    else:
        # Fallback to JSON if needed, or handle unsupported content type
        data = await request.json()

    # Extract sender and text_body from the parsed data
    sender = data.get('From')  # Adjust based on the actual structure of your incoming webhook data
    text_body = data.get('Body')  # Adjust based on the actual structure of your incoming webhook data

    # Determine the session_id based on the sender
    session_id = await session_repo.get_session_id_by_mobile_number(sender)
    if not session_id:
        # If there's no session, start a new onboarding process
        session_id = onboarding_handler.start_onboarding(sender)
        # Set the expected next step to 'language_preference'
        session_repo.update_session(session_id, {"current_step": "language_preference"})
        return {"message": "Onboarding started."}

    # Process the message based on the current step
    current_step = session_repo.get_current_step(session_id)
    await onboarding_handler.handle_user_input(session_id, current_step, {"text_body": text_body})

    # Optionally, check if onboarding is complete and call complete_onboarding if it is
    if session_repo.is_onboarding_complete(session_id):
        await onboarding_handler.complete_onboarding(session_id)
        return {"message": "Onboarding completed."}

    return {"message": "User input processed."}
