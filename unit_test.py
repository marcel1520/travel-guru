import unittest
from unittest.mock import patch, MagicMock
from app import create_conversation_add_participant, send_test_message, process_incoming_message


class TestApp(unittest.TestCase):

    @patch('app.client.conversations.v1.services')
    def test_create_conversation_add_participant(self, mock_services):
        # Mock the conversation creation
        mock_conversation = MagicMock()
        mock_conversation.sid = "12345"
        mock_services.return_value.conversations.create.return_value = mock_conversation

        # Mock the participant addition
        mock_services.return_value.conversations.return_value.participants.create.return_value = MagicMock()

        # Call the function
        conversation_sid = create_conversation_add_participant(
            "test_service_sid", "user_phone", "proxy_phone"
        )

        # Test if the conversation SID is returned correctly
        self.assertEqual(conversation_sid, "12345")
        mock_services.return_value.conversations.create.assert_called_once_with(friendly_name="Travel Guru user_phone")

    @patch('app.client.messages.create')
    def test_send_test_message(self, mock_messages_create):
        # Mock the response from sending a message
        mock_message = MagicMock()
        mock_message.sid = "test_sid"
        mock_messages_create.return_value = mock_message

        # Call the function
        message_sid = send_test_message("whatsapp:+1234567890", "Hello!")

        # Test if the message SID is returned correctly
        self.assertEqual(message_sid, "test_sid")
        mock_messages_create.assert_called_once_with(
            body="Hello!",
            from_="your_twilio_number",  # Use your Twilio number here
            to="whatsapp:+1234567890"
        )

    def test_process_incoming_message(self):
        # Simple test for message processing
        incoming_msg = "Hello"
        from_number = "whatsapp:+1234567890"
        reply_text = process_incoming_message(incoming_msg, from_number)

        # Check if the message is processed correctly
        self.assertEqual(reply_text, "You said: Hello")

    @patch('app.app.run')
    def test_flask_app_run(self, mock_run):
        # Test the Flask server running without actually starting it
        mock_run()
        mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()