import openai
from validate_user_input import validate_restaurant_finder, validate_historical_places, validate_mystery_guide


class TripPlanner:
    def __init__(self):
        self.user_details = {}
        self.step = 0  # Tracks conversation step
        self.selected_service = ""

    def process_message(self, user_input):
        """Handles conversation flow based on user input."""
        if self.step == 0:  # First message
            if "help" in user_input.lower():
                self.step = 1
                return ("Hey! I can help with your trip. Choose a service:\n"
                        "1. Restaurant Finder\n"
                        "2. Tourist Attractions\n"
                        "3. Mystery Planning Guide\n"
                        "Enter your choice (1/2/3):")

        elif self.step == 1:  # User selects a service
            if user_input in ["1", "2", "3"]:
                self.selected_service = user_input
                self.step = 2
                return self.get_initial_prompt()
            else:
                return "Invalid choice. Please enter 1, 2, or 3."

        elif self.step >= 2:  # Collect user input step by step
            return self.collect_user_input(user_input)

    def get_initial_prompt(self):
        """Returns the initial prompt based on the selected service."""
        prompts = {
            "1": "Enter your location:",
            "2": "Enter the location for tourist attractions:",
            "3": "Enter the city you want to travel to:"
        }
        return prompts[self.selected_service]

    def collect_user_input(self, user_input):
        """Collects and validates user input step by step."""
        steps = {
            "1": ["location", "cuisine", "budget"],
            "2": ["location", "preferences", "budget"],
            "3": ["city", "people", "budget", "days"]
        }

        current_step = len(self.user_details)
        expected_key = steps[self.selected_service][current_step]
        self.user_details[expected_key] = user_input

        if current_step + 1 < len(steps[self.selected_service]):
            return self.get_next_prompt(steps[self.selected_service], current_step + 1)

        return self.validate_and_generate_response()

    def get_next_prompt(self, step_list, step_index):
        """Returns the next question based on the step."""
        prompts = {
            "cuisine": "Preferred cuisine?",
            "budget": "Enter your budget:",
            "preferences": "Do you prefer monuments, parks, or viewpoints?",
            "people": "How many people are traveling?",
            "days": "How many days will you travel?"
        }
        return prompts[step_list[step_index]]

    def validate_and_generate_response(self):
        """Validates user inputs and fetches data from OpenAI API."""
        validation_functions = {
            "1": validate_restaurant_finder,
            "2": validate_historical_places,
            "3": validate_mystery_guide
        }

        validation_result = validation_functions[self.selected_service](self.user_details)

        if not validation_result["success"]:
            return "Error: " + ", ".join(validation_result["errors"])

        formatted_text = self.format_user_input()
        response = self.fetch_data_from_openai(formatted_text)
        return response

    def format_user_input(self):
        """Formats the user input into a structured sentence."""
        if self.selected_service == "1":
            return f"The user is in {self.user_details['location']} and needs a {self.user_details['cuisine']} restaurant with a budget of {self.user_details['budget']}."
        elif self.selected_service == "2":
            return f"The user is in {self.user_details['location']} and prefers {self.user_details['preferences']} with a budget of {self.user_details['budget']}."
        elif self.selected_service == "3":
            return f"The user wants to travel to {self.user_details['city']} for {self.user_details['days']} days with {self.user_details['people']} people and a budget of {self.user_details['budget']}."

    def fetch_data_from_openai(self, query):
        """Fetches data from OpenAI based on user input."""
        openai.api_key = "your-openai-api-key"  # Make sure to use your OpenAI API key

        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=query,
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].text.strip()
        except Exception as e:
            return f"Error fetching data from OpenAI: {str(e)}"


def simulate_conversation():
    trip_planner = TripPlanner()

    while True:
        user_input = input("You: ")
        response = trip_planner.process_message(user_input)
        print(f"Bot: {response}")

        if trip_planner.step == 6:
            print(f"\nBot: Here's your trip planning: {response}")
            break

# Uncomment the next line to run the conversation simulation
simulate_conversation()
