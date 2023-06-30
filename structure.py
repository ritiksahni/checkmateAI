import json


def requestJson(prompt, json_structure):
    return f"""
    {prompt}

    Do not include any explanations, only provide a RFC8259 compliant JSON response following this format without deviation.

    {json_structure}
    """


def formatJsonResponse(json_response):
    json_data = json.loads(json_response)
    text = "{feedback}\n\n{relevant_insights}\n\nHere's a question for you: {question}\n\n{ending_note}"
    formatted_text = text.format(
        feedback=json_data["feedback"],
        question=json_data["question"],
        relevant_insights=json_data["relevant_insights"],
        ending_note=json_data["ending_note"],
    )
    return formatted_text


def structure():
    initial_structure = {
        "feedback": "Some thoughts on the transcribed video",
        "question": "Question to ponder about",
        "relevant_insights": "Insights around the concept of the video",
        "ending_note": "Ending section of the message",
    }

    return json.dumps(initial_structure)
