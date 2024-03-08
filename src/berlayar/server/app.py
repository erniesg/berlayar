# berlayar/src/berlayar/server/app.py
from fastapi import FastAPI, Request
from berlayar.adapters.messaging.twilio_whatsapp import TwilioWhatsAppAdapter

app = FastAPI()
adapter = TwilioWhatsAppAdapter()

@app.post("/webhook")
async def webhook(request: Request):
    request_body = await request.form()
    request_dict = dict(request_body)

    # Determine if it's a message or media based on the payload
    if "MediaUrl0" in request_dict:
        response = adapter.receive_media(request_dict)
    else:
        response = adapter.receive_message(request_dict)

    # Your logic to respond to the webhook call
    return {"received": True, "data": response}
