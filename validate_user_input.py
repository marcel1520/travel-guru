def validate_user_input(user_data):
    #to do: clarify how to get user_data from whatsapp
    """
    Validates user input for location, optional hotel address, and days spent in town.

    """
    location = user_data.get("location", "").strip()
    hotel_address = user_data.get("hotel_address", "").strip()
    days_spent = user_data.get("days_spent", "").strip()

    errors = []

    # Validate location
    if not location:
        errors.append("Location is required.")

    # Validate days spent (must be a positive integer)
    if not days_spent.isdigit() or int(days_spent) <= 0:
        errors.append("Days spent must be a positive number.")

    # Validate hotel address (optional, should not contain special characters except commas and dots)
    if hotel_address and not all(c.isalnum() or c.isspace() or c in ",." for c in hotel_address):
        errors.append("Invalid hotel address format.")

    # Return results
    if errors:
        return {"success": False, "errors": errors}

    return {
        "success": True,
        "validated_data": {
            "location": location,
            "hotel_address": hotel_address if hotel_address else None,
            "days_spent": int(days_spent)
        }
    }



