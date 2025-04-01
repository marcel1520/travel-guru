def validate_restaurant_finder(user_data):
    """
    Validates the input for the restaurant finder service.

    Parameters:
    user_data (dict): A dictionary containing user inputs for the restaurant finder service.

    Returns:
    dict: Contains either validated data or an error message.
    """
    location = user_data.get("location", "").strip()
    budget = user_data.get("budget", "").strip()
    theme = user_data.get("theme", "").strip()
    hotel_address = user_data.get("hotel_address", "").strip()

    errors = []

    # Validate location
    if not location:
        errors.append("Location is required.")

    # Validate budget (must be a positive number)
    if budget and (not budget.isdigit() or int(budget) <= 0):
        errors.append("Budget must be a positive number.")

    # Validate hotel address (should not be empty if provided)
    if hotel_address and len(hotel_address) < 5:
        errors.append("Hotel address must be at least 5 characters long.")

    # Return results
    if errors:
        return {"success": False, "errors": errors}

    service_data = {
        "location": location,
        "budget": int(budget) if budget.isdigit() else None,
        "theme": theme if theme else None,
        "hotel_address": hotel_address
    }

    return {"success": True, "service_data": service_data}


def validate_historical_places(user_data):
    """
    Validates the input for the historical places service.

    Parameters:
    user_data (dict): A dictionary containing user inputs for the historical places service.

    Returns:
    dict: Contains either validated data or an error message.
    """
    location = user_data.get("location", "").strip()
    hotel_address = user_data.get("hotel_address", "").strip()
    num_people = user_data.get("number_of_people", "").strip()
    total_budget = user_data.get("total_budget", "").strip()
    max_ticket_price = user_data.get("max_ticket_price", "").strip()

    errors = []

    # Validate location
    if not location:
        errors.append("Location is required.")

    # Validate hotel address (should not be empty if provided)
    if hotel_address and len(hotel_address) < 5:
        errors.append("Hotel address must be at least 5 characters long.")

    # Validate number of people (must be a positive integer)
    if num_people and (not num_people.isdigit() or int(num_people) <= 0):
        errors.append("Number of people must be a positive number.")

    # Validate total budget (must be a positive number)
    if total_budget and (not total_budget.isdigit() or int(total_budget) <= 0):
        errors.append("Total budget must be a positive number.")

    # Validate max ticket price (must be a positive number)
    if max_ticket_price and (not max_ticket_price.isdigit() or int(max_ticket_price) <= 0):
        errors.append("Max ticket price must be a positive number.")

    # Return results
    if errors:
        return {"success": False, "errors": errors}

    service_data = {
        "location": location,
        "hotel_address": hotel_address,
        "num_people": int(num_people) if num_people.isdigit() else None,
        "total_budget": int(total_budget) if total_budget.isdigit() else None,
        "max_ticket_price": int(max_ticket_price) if max_ticket_price.isdigit() else None
    }

    return {"success": True, "service_data": service_data}


def validate_mystery_guide(user_data):
    """
    Validates the input for the mystery guide service.

    Parameters:
    user_data (dict): A dictionary containing user inputs for the mystery guide service.

    Returns:
    dict: Contains either validated data or an error message.
    """
    public_transport = user_data.get("public_transport", "").strip()
    budget = user_data.get("budget", "").strip()
    days_spent = user_data.get("days_spent", "").strip()
    preferences = user_data.get("preferences", "").strip()

    errors = []

    # Validate public transport (optional, should be 'yes' or 'no')
    if public_transport and public_transport.lower() not in ["yes", "no"]:
        errors.append("Public transport should be 'yes' or 'no'.")

    # Validate budget (must be a positive number)
    if budget and (not budget.isdigit() or int(budget) <= 0):
        errors.append("Budget must be a positive number.")

    # Validate days spent (must be a positive integer)
    if days_spent and (not days_spent.isdigit() or int(days_spent) <= 0):
        errors.append("Days spent must be a positive number.")

    # Return results
    if errors:
        return {"success": False, "errors": errors}

    service_data = {
        "public_transport": public_transport.lower() if public_transport else None,
        "budget": int(budget) if budget.isdigit() else None,
        "days_spent": int(days_spent) if days_spent.isdigit() else None,
        "preferences": preferences if preferences else None
    }

    return {"success": True, "service_data": service_data}