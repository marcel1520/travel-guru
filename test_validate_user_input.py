import unittest
from validate_user_input import validate_user_input


class TestUserInputValidation(unittest.TestCase):

    def test_valid_input(self):
        """Test a valid input scenario"""
        user_input = {
            "location": "New York",
            "hotel_address": "123 Broadway St, NY",
            "days_spent": "5"
        }
        result = validate_user_input(user_input)
        self.assertTrue(result["success"])
        self.assertEqual(result["validated_data"]["location"], "New York")
        self.assertEqual(result["validated_data"]["hotel_address"], "123 Broadway St, NY")
        self.assertEqual(result["validated_data"]["days_spent"], 5)

    def test_missing_location(self):
        """Test missing location"""
        user_input = {
            "location": "",
            "hotel_address": "456 Market St, SF",
            "days_spent": "3"
        }
        result = validate_user_input(user_input)
        self.assertFalse(result["success"])
        self.assertIn("Location is required.", result["errors"])

    def test_invalid_hotel_address(self):
        """Test invalid hotel address format"""
        user_input = {
            "location": "London",
            "hotel_address": "123 @ Invalid Street!",
            "days_spent": "2"
        }
        result = validate_user_input(user_input)
        self.assertFalse(result["success"])
        self.assertIn("Invalid hotel address format.", result["errors"])

    def test_non_numeric_days_spent(self):
        """Test non-numeric days spent"""
        user_input = {
            "location": "Tokyo",
            "hotel_address": "789 Shibuya St",
            "days_spent": "three"
        }
        result = validate_user_input(user_input)
        self.assertFalse(result["success"])
        self.assertIn("Days spent must be a positive number.", result["errors"])

    def test_negative_days_spent(self):
        """Test negative days spent"""
        user_input = {
            "location": "Berlin",
            "hotel_address": "",
            "days_spent": "-2"
        }
        result = validate_user_input(user_input)
        self.assertFalse(result["success"])
        self.assertIn("Days spent must be a positive number.", result["errors"])

    def test_zero_days_spent(self):
        """Test zero days spent"""
        user_input = {
            "location": "Paris",
            "hotel_address": "123 Champs-Élysées",
            "days_spent": "0"
        }
        result = validate_user_input(user_input)
        self.assertFalse(result["success"])
        self.assertIn("Days spent must be a positive number.", result["errors"])

    def test_optional_hotel_address(self):
        """Test missing hotel address (should be allowed)"""
        user_input = {
            "location": "Amsterdam",
            "days_spent": "4"
        }
        result = validate_user_input(user_input)
        self.assertTrue(result["success"])
        self.assertEqual(result["validated_data"]["hotel_address"], None)


if __name__ == '__main__':
    unittest.main()
