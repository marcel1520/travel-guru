import unittest
import os
from unittest.mock import patch, MagicMock

from app import app, process_incoming_message, create_conversation_add_participant, send_test_message
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()


class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        """Set up the test client."""
        self.app = app.test_client()
        self.app.testing = True
        self.account_sid = os.getenv("ACCOUNT_SID")
        self.api_key_sid = os.getenv("API_KEY_SID")
        self.api_key_secret = os.getenv("API_KEY_SECRET")
        self.chat_service_sid = os.getenv("CHAT_SERVICE_SID")
        self.user_phone = os.getenv("USER_PHONE")
        self.proxy_phone = os.getenv("PROXY_PHONE")
        self.client = Client(self.api_key_sid, self.api_key_secret, self.account_sid)

    def test_home_route(self):
        """Test the home route."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Polling bot is running!")

    def test_whatsapp_inbound(self):
        """Test receiving a WhatsApp message."""
        response = self.app.post('/whatsapp-inbound', data={
            "Body": "Hello",
            "From": self.user_phone
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("I'm sorry, I didn't understand that.", response.data.decode())

    def test_create_conversation(self):
        """Test creating a conversation and adding a participant."""
        conversation_sid = create_conversation_add_participant(
            self.chat_service_sid, self.user_phone, self.proxy_phone
        )
        self.assertIsInstance(conversation_sid, str)

    def test_send_message(self):
        """Test sending a message."""
        message_sid = send_test_message(self.user_phone, "Test message")
        self.assertIsInstance(message_sid, str)

    def test_process_message(self):
        """Test processing an incoming message."""
        response = process_incoming_message("Hello", self.user_phone)
        self.assertIsInstance(response, str)

if __name__ == "__main__":
    unittest.main()
