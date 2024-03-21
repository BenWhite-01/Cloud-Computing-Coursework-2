import json

age_restricted = {
    "12+": ["Death, Harm & Tragedy"],
    "16+": ["Firearms & Weapons", "Profanity", "Sexual", "Toxic"],
}
banned = ["Illicit Drugs", "Insult", "Derogatory"]
safe_search = ["Toxic", "Sexual", "Violent", "Death, Harm & Tragedy"]

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    # Extract required parameters from payload body
    try:
        req_body = json.loads(req)
        categories = req_body.get("moderation_categories")
        age = req_body.get("profile").get("age")
        safe_search_toggle = req_body.get("profile").get("safe_search", False)
    except:
        return http_response("The request body is missing required fields 'moderation_categories' or 'profile'.", 200)

    # Create response message
    message = 'Valid - Text content is suitable for viewing'
    for cat in categories:
        if cat["confidence"] <= 0.7:
            continue
        if cat["name"] in banned:
            message = "Invalid - Text contains content that has been banned (" + cat["name"] + ")"
        elif safe_search_toggle and cat["name"] in safe_search:
            message = "Invalid - Text contains content unsuitable for safe search (" + cat["name"] + ")"
        elif age < 16 and cat["name"] in age_restricted["16+"]:
            message = "Invalid - Text contains content unsuitable for persons under 16 years old (" + cat["name"] + ")"
        elif age < 12 and cat["name"] in age_restricted["12+"]:
            message = "Invalid - Text contains content unsuitable for persons under 12 years old (" + cat["name"] + ")"

    return http_response(message, 200)

def http_response(message, code):
    return json.dumps({"status": code, "body": message})
