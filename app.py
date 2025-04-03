import os
import time
import threading
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

print(ACCOUNT_SID)
print(API_KEY_SID)
print(API_KEY_SECRET)
print(CHAT_SERVICE_SID)

# Create a single Twilio Client instance
client = Client(API_KEY_SID, API_KEY_SECRET, ACCOUNT_SID)


# ------------------------------------------------
# 2) Conversation creation function
# ------------------------------------------------
def create_conversation_add_participant(service_sid, USER_PHONE, PROXY_PHONE):
    """
    Creates a Twilio Conversation and adds the user as a participant.
    Returns the conversation SID.
    """
    conversation = client.conversations \
        .v1 \
        .services(service_sid) \
        .conversations \
        .create(friendly_name=f"Travel Guru {USER_PHONE}")

    try:
        client.conversations \
            .v1 \
            .services(service_sid) \
            .conversations(conversation.sid) \
            .participants \
            .create(
            messaging_binding_address=USER_PHONE,
            messaging_binding_proxy_address=PROXY_PHONE
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
from trip_plan import TripPlanner

conversation_state = {}


def process_incoming_message(incoming_msg, from_number):
    """
    Process the incoming message from the user.
    For now, this function simply echoes the message back.
    """
    if from_number not in conversation_state:
        conversation_state[from_number] = TripPlanner()

    trip_planner = conversation_state[from_number]
    reply_text = trip_planner.process_message(incoming_msg)
    return reply_text if reply_text else "I'm sorry, I didn't understand that."



# Set a lower maximum message length to avoid truncation.
MAX_MSG_LENGTH = 1000  # Adjust as needed


def split_message(text, max_length=MAX_MSG_LENGTH):
    """Splits the text into chunks that do not exceed max_length characters."""
    if len(text) <= max_length:
        return [text]
    chunks = []
    while len(text) > max_length:
        # Attempt to break at a newline for better readability.
        break_point = text.rfind('\n', 0, max_length)
        if break_point == -1:
            break_point = max_length
        chunks.append(text[:break_point])
        text = text[break_point:].lstrip()
    if text:
        chunks.append(text)
    return chunks




# ------------------------------------------------
# 5) Flask route to handle inbound WhatsApp messages
# ------------------------------------------------
@app.route("/whatsapp-inbound", methods=["POST"])
def whatsapp_inbound():
    incoming_msg = request.form.get("Body", "").strip()
    from_number = request.form.get("From", "").strip()
    print("Incoming:", incoming_msg)
    print("From:", from_number)
    response_text = process_incoming_message(incoming_msg, from_number)

    # Split the response into chunks.
    chunks = split_message(response_text)


    # Instead of sending one chunk via the TwiML response,
    # return a minimal message (acknowledgment) and send all chunks using the REST API.
    def send_all_chunks(chunks, to_number):
        for chunk in chunks:
            time.sleep(2)  # Increase delay if necessary
            client.messages.create(
                body=chunk,
                from_=PROXY_PHONE,
                to=to_number
            )

    threading.Thread(target=send_all_chunks, args=(chunks, from_number)).start()


    resp = MessagingResponse()
    resp.message("Processing your itinerary...")


    return str(resp)


@app.route("/")
def home():
    return "Polling bot is running!"


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

    service = client.conversations.v1.services(CHAT_SERVICE_SID)
    existing_conversations = service.conversations.list()

    conversation = next((c for c in existing_conversations if c.friendly_name == f"Travel Guru {USER_PHONE}"), None)

    if conversation:
        print("ℹ️ Reusing existing conversation.")
    else:
        conversation = service.conversations.create(friendly_name=f"Travel Guru {USER_PHONE}")
        print("✅ Created new conversation.")

    participants = conversation.participants.list()
    already_added = any(p.messaging_binding['address'] == USER_PHONE for p in participants)

    if not already_added:
        print(f"Adding participant with address: {USER_PHONE}")
        print(f"Using proxy address: {PROXY_PHONE}")
        conversation.participants.create(
            messaging_binding_address=USER_PHONE,
            messaging_binding_proxy_address=PROXY_PHONE
        )
        print("Participant added to conversation.")
    else:
        print("Participant already exists in the conversation")

    print("Waiting for replies from your WhatsApp")

    last_sid = None

    while True:
        messages = conversation.messages.list()

        if messages:
            last_msg = messages[-1]
            if last_msg.sid != last_sid and last_msg.author == USER_PHONE:
                print("From phone:", last_msg.body)
                incoming_msg = last_msg.body
                from_number = USER_PHONE
                response_text = process_incoming_message(incoming_msg, from_number)
                reply = response_text
                print("From server:", reply)
                # Split reply into chunks and send each chunk using REST API.
                for chunk in split_message(reply):
                    conversation.messages.create(author="system", body=chunk)
                    time.sleep(2)  # Increase delay if necessary
                last_sid = last_msg.sid
        time.sleep(1)

# Start Flask server
app.run(debug=True, host='0.0.0.0', port=5001)
