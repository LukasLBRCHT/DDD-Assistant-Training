# Todo
"""
stell dir vor du schreibst in eine datei:

object1
object2
associations:
object1-object2

und dann macht das skript daraus:
"domain objects": [
      {"name": "object1", "description": ""}
      {"name": "object2", "description": ""}
    ],
  "associations": [
      {"from": "object1", "to": "object2", "description": ""},
    ]
"""
import os

import regex

domain_objects_dir = "../../res/base_data/domain_objects"

ws = " "


def format_correction(subdomain_objects):
    objects = subdomain_objects.split(",")
    final_string = ""
    for obj in objects:
        object_string = f"\"{obj.strip()}\","
        final_string += object_string
    final_string = final_string.removesuffix(",")

    return final_string

def parse_domain_objects(txt):

    text = txt
    split = text.split("\nnext:\n")
    objects = split[0]
    associations = split[1]
    subdomains = split[2]

    result_data = ""

    for line in objects.splitlines():
        if not line:
            continue
        name = line
        object_json = f"      {{\"name\": \"{name}\", \"description\": \"\"}},\n"
        result_data += object_json

    result_data = result_data.removesuffix(",\n")

    result_data += "\nassociations:\n"

    association_pattern = r"(.*?)-(.*)"
    for line in associations.splitlines():

        if not line:
            continue

        match = regex.search(association_pattern, line)

        match1 = match.group(1)
        match2 = match.group(2)

        object_json = f"      {{\"from\": \"{match1}\", \"to\": \"{match2}\", \"description\": \"\"}},\n"

        result_data += object_json

    result_data = result_data.removesuffix(",\n")
    result_data += "\n\nsubdomains:\n"

    subdomain_pattern = r"(.*?):(.*)"
    bounded_contexts = "\n\nbounded contexts:\n"
    for line in subdomains.splitlines():

        if not line:
            continue

        match = regex.search(subdomain_pattern, line)

        subdomain_name = match.group(1)
        subdomain_objects = match.group(2)

        subdomain_objects = format_correction(subdomain_objects)

        object_json_subdomain = f"{ws*6}\"{subdomain_name}\": {{\n{ws*10}\"objects\" : [{subdomain_objects}]\n{ws*6}}},\n"
        object_json_bounded_context = f"{ws*6}\"{subdomain_name}\": {{\n{ws*10}\"derived from\": \"{subdomain_name} Subdomain\",\n{ws*10}\"objects\" : [{subdomain_objects}],\n{ws*10}\"name changes\" : []\n{ws*6}}},\n"

        result_data += object_json_subdomain
        bounded_contexts += object_json_bounded_context

    print(result_data.removesuffix(","))
    print(bounded_contexts.removesuffix(","))


if __name__ == "__main__":
    plain = """"""

    parse_domain_objects(plain)
