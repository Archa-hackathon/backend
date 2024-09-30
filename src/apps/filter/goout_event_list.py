import json, os


with open(os.path.join(os.path.dirname(__file__), "system_prompt.json"), "r") as file:
    UPCOMING_EVENTS_PROPMT = json.load(file)