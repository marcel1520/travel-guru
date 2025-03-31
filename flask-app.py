import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse


app = Flask(__name__)

@app.route("/whatsapp-inbound", methods=["POST"])
def whatsapp_inbound():
    incoming_msg = request.form.get("Body", "").strip()
    from_number = request.form.get("From", "").strip()

    response_text = process_incoming_message(incoming_msg, from_number)

    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)