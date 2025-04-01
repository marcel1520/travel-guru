import openai
from validate_user_input import validate_user_input

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
                self.user_details["service"] = ["Restaurant Finder", "Tourist Attractions", "Mystery Planning Guide"][
                    int(user_input) - 1]
                self.step = 2

                if user_input == "1":
                    return "Enter your location:"
                elif user_input == "2":
                    return "Enter the location for tourist attractions:"
                elif user_input == "3":
                    return "Enter the city you want to travel to:"

            else:
                return "Invalid choice. Please enter 1, 2, or 3."

        elif self.step == 2:  # Asking for more details
            if self.selected_service == "1":
                self.user_details["location"] = user_input
                self.step = 3
                return "Preferred cuisine?"

            elif self.selected_service == "2":
                self.user_details["location"] = user_input
                self.step = 3
                return "Do you prefer monuments, parks, or viewpoints?"

            elif self.selected_service == "3":
                self.user_details["city"] = user_input
                self.step = 3
                return "How many people are traveling?"

        elif self.step == 3:
            if self.selected_service == "1":
                self.user_details["cuisine"] = user_input
                self.step = 4
                return "Enter your budget:"

            elif self.selected_service == "2":
                self.user_details["preferences"] = user_input
                self.step = 4
                return "Enter your budget:"

            elif self.selected_service == "3":
                self.user_details["people"] = user_input
                self.step = 4
                return "Enter your budget:"

        elif self.step == 4:
            if self.selected_service == "1":
                self.user_details["budget"] = user_input
                self.step = 5

            elif self.selected_service == "2":
                self.user_details["budget"] = user_input
                self.step = 5

            elif self.selected_service == "3":
                self.user_details["budget"] = user_input
                self.step = 5
                return "How many days will you travel?"

        elif self.step == 5 and self.selected_service == "3":
            self.user_details["days"] = user_input
            self.step = 6  # End of conversation

        if self.step == 5 or self.step == 6:  # Final response
            formatted_text = self.format_user_input()
            response = self.fetch_data_from_openai(formatted_text)  # Fetch data from OpenAI API
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

        # Make the request to OpenAI's GPT-3 model
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",  # You can use different models like gpt-3.5-turbo
                prompt=query,
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].text.strip()
        except Exception as e:
            return f"Error fetching data from OpenAI: {str(e)}"


def restart_conversation():
    """Ask the user if they want to start a new conversation."""
    return input("Do you want to start a new trip planning? (yes/no): ").strip().lower() == 'yes'


# Simulate a conversation
def simulate_conversation():
    trip_planner = TripPlanner()

    # Loop for conversation
    while True:
        # Get user input for each step
        if trip_planner.step == 0:
            user_input = input("You: ")
            response = trip_planner.process_message(user_input)

        elif trip_planner.step == 1 or trip_planner.step == 2 or trip_planner.step == 3 or trip_planner.step == 4 or trip_planner.step == 5:
            user_input = input(f"You: ")
            response = trip_planner.process_message(user_input)

        print(f"Bot: {response}")

        if trip_planner.step == 6:  # End of conversation, formatted response
            print(f"\nBot: Here's your trip planning: {response}")
            if not restart_conversation():
                print("\nBot: Thank you! Have a great trip!")
                break
            else:
                print("\nBot: Let's start again!")
                trip_planner = TripPlanner()  # Reset the conversation


simulate_conversation()
