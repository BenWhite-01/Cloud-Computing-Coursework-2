import requests
import json


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    # Extract required parameters from payload body
    try:
        req_body = json.loads(req)
        text = str(req_body.get("text"))
        profile = req_body.get("profile")
    except:
        return http_response(
            "The request body is missing required fields 'text' or 'profile'.", 400
        )

    if not text:
        return http_response("Invalid or missing value for 'text' in request body", 400)
    if not profile["age"] or profile["age"] < 0 or profile["age"] > 120:
        return http_response(
            "Invalid or missing value for 'profile.age' in request body", 400
        )

    # Send a POST request to the Google Text Moderation API
    response = requests.post(
        "https://language.googleapis.com/v2/documents:moderateText?key=AIzaSyBmC8WB1lkOKlE4qy-lNt5PYPWrEfscLJI",
        json = {
            "document": {
                "content": text,
                "type": "PLAIN_TEXT",
                "languageCode": "en"
            }
        }
    )
    if response.status_code != 200:
        return http_response(
            "Failed to analyze text for moderation. Please try again later.", 500
        )

    moderation_categories = response.json()["moderationCategories"]

    # Call next azure function
    response = requests.post(
        "http://20.90.210.50:8080/function/determine-response",
        json = {
            "moderation_categories": moderation_categories,
            "profile": profile
        }
    )
    if response.status_code != 200:
        return http_response(
            "Failed to determine response. Please try again later.", 500
        )

    # Return response from function 'DetermineResponse()'
    try:
        result = response.json()
        if result["status"] == 200:
            return result["body"]
        else:
            return http_response(
                "Failed to determine response. Please try again later.", 500
            )
    except:
        return http_response(
            "Failed to determine response. Please try again later.", 500
        )

def http_response(message, code):
    return json.dumps({"status": code, "body": message})
