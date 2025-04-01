import unittest
from validate_user_input import validate_restaurant_finder, validate_historical_places, validate_mystery_guide

class TestValidateUserInput(unittest.TestCase):

    def test_valid_input_restaurant(self):
        user_input = {
            "location": "Paris",
            "budget": "500",
            "theme": "vegan",
            "hotel_address": "123 Paris St"
        }
        result = validate_restaurant_finder(user_input)
        self.assertTrue(result["success"])
        self.assertEqual(result["service_data"]["location"], "Paris")
        self.assertEqual(result["service_data"]["budget"], 500)

    def test_valid_input_historical(self):
        user_input = {
            "location": "Rome",
            "hotel_address": "456 Rome Ave",
            "number_of_people": "4",
            "total_budget": "2000",
            "max_ticket_price": "50"
        }
        result = validate_historical_places(user_input)
        self.assertTrue(result["success"])
        self.assertEqual(result["service_data"]["location"], "Rome")
        self.assertEqual(result["service_data"]["total_budget"], 2000)

    def test_valid_input_mystery(self):
        user_input = {
            "public_transport": "yes",
            "budget": "1000",
            "days_spent": "5",
            "preferences": "castles, museums"
        }
        result = validate_mystery_guide(user_input)
        self.assertTrue(result["success"])
        self.assertEqual(result["service_data"]["public_transport"], "yes")
        self.assertEqual(result["service_data"]["budget"], 1000)

    def test_invalid_service(self):
        user_input = {"location": "Paris", "budget": "-10",}
        result = validate_restaurant_finder(user_input)
        self.assertFalse(result["success"])
        self.assertIn("Budget must be a positive number.", result["errors"])

if __name__ == "__main__":
    unittest.main()
