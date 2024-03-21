import logging

import azure.functions as func

# allowed = ['Legal', 'Politics', 'Finance', 'Health', 'Public Safety', 'Religion & Belief', 'War & Conflict']
age_restricted = {
    "12+": ["Death, Harm & Tragedy"],
    "16+": ["Firearms & Weapons", "Profanity", "Sexual", "Toxic"],
}
banned = ["Illicit Drugs", "Insult", "Derogatory"]
safe_search = ["Toxic", "Sexual", "Violent", "Death, Harm & Tragedy"]


def main(req: func.HttpRequest) -> func.HttpResponse:
    
    # Extract required parameters from payload body
    try:
        req_body = req.get_json()
        categories = req_body.get("moderation_categories")
        age = req_body.get("profile").get("age")
        safe_search_toggle = req_body.get("profile").get("safe_search", False)
    except:
        return func.HttpResponse(
            "The request body is missing required fields 'moderation_categories' or 'profile'.",
            status_code=400,
        )

    # # Log all relevant categories
    # for cat in categories:
    #     if cat["confidence"] > 0.5:
    #         logging.info(cat)

    # Create response message
    message = 'Valid - Text content is suitable for viewing'
    for cat in categories:
        if cat["confidence"] <= 0.7:
            continue
        if cat["name"] in banned:
            message = f'Invalid - Text contains content that has been banned ({cat["name"]})'
        elif safe_search_toggle and cat["name"] in safe_search:
            message = f'Invalid - Text contains content unsuitable for safe search ({cat["name"]})'
        elif age < 16 and cat["name"] in age_restricted["16+"]:
            message = f'Invalid - Text contains content unsuitable for persons under 16 years old ({cat["name"]})'
        elif age < 12 and cat["name"] in age_restricted["12+"]:
            message = f'Invalid - Text contains content unsuitable for persons under 12 years old ({cat["name"]})'

    return func.HttpResponse(message)
