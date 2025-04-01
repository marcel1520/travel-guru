import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)


ACCOUNT_SID = os.getenv("ACCOUNT_SID")
API_KEY_SID = os.getenv("API_KEY_SID")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
CHAT_SERVICE_SID = os.getenv("CHAT_SERVICE_SID")
USER_PHONE = os.getenv("USER_PHONE")
PROXY_PHONE = os.getenv("PROXY_PHONE")

# Create a single Twilio Client instance
client = Client(API_KEY_SID, API_KEY_SECRET, account_sid=ACCOUNT_SID)

# ------------------------------------------------
# 2) Conversation creation function
# ------------------------------------------------
def create_conversation_add_participant(service_sid, user_phone, proxy_phone):
    """
    Creates a Twilio Conversation and adds the user as a participant.
    Returns the conversation SID.
    """
    conversation = client.conversations \
                         .v1 \
                         .services(service_sid) \
                         .conversations \
                         .create(friendly_name=f"Travel Guru {user_phone}")

    try:
        client.conversations \
            .v1 \
            .services(service_sid) \
            .conversations(conversation.sid) \
            .participants \
            .create(
            messaging_binding_address=user_phone,
            messaging_binding_proxy_address=proxy_phone
        )
    except Exception as e:
        # Check if the error is due to a duplicate binding (HTTP 409)
        if "A binding for this participant and proxy address already exists" in str(e):
            print("Participant binding already exists, skipping addition.")
        else:
            # Re-raise the exception if it's a different error
            raise e

    return conversation.sid

# ------------------------------------------------
# 3) Test function to send a manual WhatsApp message
# ------------------------------------------------
def send_test_message(to_number, message):
    """
    Sends a test WhatsApp message using Twilio's Messaging API.
    """
    sent_message = client.messages.create(
        body=message,
        from_=PROXY_PHONE,  # Use your Twilio WhatsApp number
        to=to_number
    )
    return sent_message.sid

# ------------------------------------------------
# 4) Message processing logic
# ------------------------------------------------
def process_incoming_message(incoming_msg, from_number):
    """
    Process the incoming message from the user.
    For now, this function simply echoes the message back.
    """
    reply_text = f"You said: {incoming_msg}"
    return reply_text

# ------------------------------------------------
# 5) Flask route to handle inbound WhatsApp messages
# ------------------------------------------------
@app.route("/whatsapp-inbound", methods=["POST"])
def whatsapp_inbound():
    incoming_msg = request.form.get("Body", "").strip()
    from_number = request.form.get("From", "").strip()

    response_text = process_incoming_message(incoming_msg, from_number)

    # Build TwiML response
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

# ------------------------------------------------
# 6) Main execution: test the connection and start Flask
# ------------------------------------------------
if __name__ == "__main__":
    # Create the conversation and add participant
    conversation_id = create_conversation_add_participant(
        CHAT_SERVICE_SID,
        USER_PHONE,
        PROXY_PHONE
    )
    print(f"Conversation created with ID: {conversation_id}")

    # Send a manual test message
    test_sid = send_test_message(USER_PHONE, "Hello from Travel Guru test!")
    print(f"Test message sent with SID: {test_sid}")

    # Start Flask server
    app.run(debug=True)