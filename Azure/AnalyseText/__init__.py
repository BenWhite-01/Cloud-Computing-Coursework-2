import logging

import azure.functions as func
import requests


def main(req: func.HttpRequest) -> func.HttpResponse:

    # Extract required parameters from payload body
    try:
        req_body = req.get_json()
        text = req_body.get("text")
        profile = req_body.get("profile")
    except:
        return func.HttpResponse(
            "The request body is missing required fields 'text' or 'profile'.",
            status_code=400,
        )

    if not text or type(text) != str:
        return func.HttpResponse(
            "Invalid or missing value for 'text' in request body", status_code=400
        )
    if not profile["age"] or profile["age"] < 0 or profile["age"] > 120:
        return func.HttpResponse(
            "Invalid or missing value for 'profile.age' in request body",
            status_code=400,
        )

    print('breakpoint 1')

    # Send a POST request to the Google Text Moderation API
    payload = { # Construct the payload for the Google Text Moderation API
        "document": {
            "content": text,
            "type": "PLAIN_TEXT",
            "languageCode": "en",
        }
    }
    try:
        response = requests.post(
            "https://language.googleapis.com/v2/documents:moderateText?key=AIzaSyBmC8WB1lkOKlE4qy-lNt5PYPWrEfscLJI",
            json=payload,
            timeout=10
        )
        if response.status_code != 200:
            return func.HttpResponse(
                "Failed to analyze text for moderation. Please try again later.",
                status_code=500,
            )
        moderation_categories = response.json()["moderationCategories"]
    except Exception as e:
        print('Connection error: ' + e)
        return func.HttpResponse(
            "Error retrieving result from TextModeration API",
            status_code=500
        )

    # Call next azure function
    response = requests.post(
        "https://postmoderation.azurewebsites.net/api/DetermineResponse?code=3TlhycMfeIgFXrz-u13JHWC8UvCBt42myA3KXUtGsZYcAzFu-U4QRQ==",
        json={"moderation_categories": moderation_categories, "profile": profile},
        timeout=10
    )
    if response.status_code != 200 or response.text == None:
        return func.HttpResponse(
            "Failed to determine response. Please try again later.", status_code=500
        )

    return func.HttpResponse(response.text)
