import json


def requestJson(prompt, json_structure):
    return f"""
    {prompt}

    Do not include any explanations, only provide a RFC8259 compliant JSON response following this format without deviation. In the JSON structure, key should remain constant, the value should tell you expected response in value. Maintain coherence between different key-value pairs.

    {json_structure}
    """


def formatJsonResponse(json_response):
    json_data = json.loads(json_response)
    formatted_text = "\n\n".join([str(value) for value in json_data.values()])
    return formatted_text
