import re
import json

def parse_json(text):

    results = [] #  string list

    json_pattern = r'```json(.*?)```'
    matches = re.findall(json_pattern, text, flags=re.DOTALL)  # DOTALL to ignore newline in json structure

    for match in matches:
        results.append(string_to_key_value_pair(match))
    return results

def string_to_key_value_pair(json_text):

    json_data = json.loads(json_text)
    first_key = next(iter(json_data))

    return first_key, json_text