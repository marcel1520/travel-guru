import os
from validate_user_input import validate_restaurant_finder, validate_historical_places, validate_mystery_guide
from dotenv import load_dotenv
from openai import OpenAI

# load the api key from the .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client with the API key from the .env file
client = OpenAI(api_key=api_key)

# Direct system prompts with placeholders; these will be formatted with the collected details.
restaurant_prompt_template = (
    "You are a restaurant recommendation assistant with access to live web search. "
    "The user is in {location} and is looking for a {cuisine} restaurant within a budget of {budget}. "
    "Please perform a web search to find at least three specific sushi restaurants that meet these criteria. "
    "For each restaurant, provide:\n"
    "- The restaurant's name\n"
    "- A brief description including its cuisine style, ambiance, and neighborhood details\n"
    "- An estimate of the average food prices\n"
    "- A clickable link to the restaurant's homepage (or state if not available)\n"
    "Include inline citations for any external sources referenced in your answer. "
    "Present your findings in a clear, detailed, and concise format."
)

tourist_prompt_template = (
    "You are a tourist attractions guide with access to live web search. "
    "The user is in {location} and prefers {preferences} attractions with a budget of {budget}. "
    "Please perform a web search to find at least three specific tourist attractions in this area that match these preferences. "
    "For each attraction, provide:\n"
    "- The attraction's name\n"
    "- A brief description including its key highlights, any entry fees, and opening hours if available\n"
    "- A clickable link to the official website or a page with more information (or state if not available)\n"
    "Include inline citations for any external sources referenced in your answer. "
    "Present your findings in a clear, detailed, and concise format."
)

mystery_prompt_template = (
    "You are a travel planning expert with access to live web search. "
    "The user wants to travel to {city} for {days} days with {people} people and a budget of {budget}. "
    "Please perform a web search to create a detailed, day-by-day mystery itinerary for their trip. "
    "The itinerary should include:\n"
    "- Specific daily recommendations for activities, dining, and sightseeing\n"
    "- Estimated costs for meals, tickets, and other activities for each day\n"
    "- Relevant links to official websites or booking pages for each recommendation (or state if not available)\n"
    "Include inline citations for any external sources referenced in your answer. "
    "Present your itinerary in a clear, engaging, and organized format."
)

def get_response_with_websearch(system_prompt, user_input, user_location=None, context_size="medium"):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    web_search_tool = {
        "type": "web_search_preview",
        "search_context_size": context_size
    }
    if user_location:
        web_search_tool["user_location"] = user_location

    try:
        response = client.responses.create(
            model="gpt-4o",          # Use a model that supports web search
            tools=[{"type": "web_search_preview"}],
            input=messages,
            max_output_tokens=2000,
            temperature=0.7,
            store=False,
            tool_choice="required"
        )
        return response.output_text
    except Exception as e:
        return f"Error fetching data from OpenAI: {str(e)}"


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

        # Check if all expected inputs are already collected.
        if len(self.user_details) >= len(steps[self.selected_service]):
            return self.validate_and_generate_response()


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

        self.reset()

        return response

    def format_user_input(self):
        """Formats the user input into a structured sentence."""
        if self.selected_service == "1":
            return f"The user is in {self.user_details['location']} and needs a {self.user_details['cuisine']} restaurant with a budget of {self.user_details['budget']}."
        elif self.selected_service == "2":
            return f"The user is in {self.user_details['location']} and prefers {self.user_details['preferences']} with a budget of {self.user_details['budget']}."
        elif self.selected_service == "3":
            return f"The user wants to travel to {self.user_details['city']} for {self.user_details['days']} days with {self.user_details['people']} people and a budget of {self.user_details['budget']}."

    def format_system_prompt(self):
        if self.selected_service == "1":
            # Restaurant Finder
            return restaurant_prompt_template.format(
                location=self.user_details['location'],
                cuisine=self.user_details['cuisine'],
                budget=self.user_details['budget']
            )
        elif self.selected_service == "2":
            # Tourist Attractions
            return tourist_prompt_template.format(
                location=self.user_details['location'],
                preferences=self.user_details['preferences'],
                budget=self.user_details['budget']
            )
        elif self.selected_service == "3":
            # Mystery Planning Guide
            return mystery_prompt_template.format(
                city=self.user_details['city'],
                days=self.user_details['days'],
                people=self.user_details['people'],
                budget=self.user_details['budget']
            )


    def fetch_data_from_openai(self, formatted_text):
        # First, generate the formatted system prompt based on the selected service.
        system_prompt = self.format_system_prompt()
        user_input = formatted_text  # Your existing method that aggregates user input

        # Optionally, if you have user location details for refining web search:
        user_location = {
            "type": "approximate",
            "city": self.user_details.get('location') or self.user_details.get('city'),

        }

        response = get_response_with_websearch(
            system_prompt,
            user_input,
            user_location=user_location,
            context_size="medium"  # Choose "low", "medium", or "high" based on your needs
        )
        return response

    def reset(self):
        """Resets the conversation state for a new session."""
        self.user_details = {}
        self.step = 0
        self.selected_service = ""

def simulate_conversation():
    trip_planner = TripPlanner()

    while True:
        user_input = input("You: ")
        response = trip_planner.process_message(user_input)
        print(f"Bot: {response}")

        if trip_planner.step == 6:
            print(f"\nBot: Here's your trip planning: {response}")
            break

#alex
# Uncomment the next line to run the conversation simulation
#simulate_conversation()
