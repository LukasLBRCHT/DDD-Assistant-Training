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
stories_dir = "../../res/base_data/stories"
subtask_format_url = "../util/subtask_format_2"

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

    extracted_objects = ""

    for line in objects.splitlines():
        if not line:
            continue
        name = line.strip()
        object_json = f"      {{\"name\": \"{name}\", \"description\": \"\"}},\n"
        extracted_objects += object_json

    extracted_objects = extracted_objects.removesuffix(",\n")

    #result_data += "\nassociations:\n"

    extracted_associations = ""
    association_pattern = r"(.*?)-(.*)"
    for line in associations.splitlines():

        if not line:
            continue

        match = regex.search(association_pattern, line)

        match1 = match.group(1)
        match2 = match.group(2)

        object_json = f"      {{\"from\": \"{match1}\", \"to\": \"{match2}\", \"description\": \"\"}},\n"

        extracted_associations += object_json

    extracted_associations = extracted_associations.removesuffix(",\n")
    #result_data += "\n\nsubdomains:\n"

    extracted_subdomains = ""
    extracted_bounded_contexts = ""

    subdomain_pattern = r"(.*?):(.*)"
    for line in subdomains.splitlines():

        if not line:
            continue

        match = regex.search(subdomain_pattern, line)

        subdomain_name = match.group(1)
        subdomain_objects = match.group(2)

        subdomain_objects = format_correction(subdomain_objects)

        object_json_subdomain = f"{ws*6}\"{subdomain_name}\": {{\n{ws*10}\"objects\" : [{subdomain_objects}]\n{ws*6}}},\n"
        object_json_bounded_context = f"{ws*6}\"{subdomain_name}\": {{\n{ws*10}\"derived from\": \"{subdomain_name} Subdomain\",\n{ws*10}\"objects\" : [{subdomain_objects}],\n{ws*10}\"name changes\" : []\n{ws*6}}},\n"

        extracted_subdomains += object_json_subdomain
        extracted_bounded_contexts += object_json_bounded_context

    extracted_subdomains = extracted_subdomains.removesuffix(",\n")
    extracted_bounded_contexts = extracted_bounded_contexts.removesuffix(",\n")

    return extracted_objects,extracted_associations,extracted_subdomains,extracted_bounded_contexts

def create_json(stories, obj, asso, sub, bc):
    with open(subtask_format_url, 'r') as format_file:
        subtask_format = format_file.read()

    json_data = subtask_format.format(stories, obj, asso, sub, bc)

    return json_data

def load_stories(text):
    # go over lines, add every one into a list
    stories = "["

    for line in text.splitlines():

        if line.strip() == "":
            continue

        line = line.replace('"', '\\"')
        stories += f'\t"{line.strip()}",\n'
    stories = stories.removesuffix(",\n")
    stories += "\n]"

    return stories

if __name__ == "__main__":

    current_number = "33"

    file_name = ""
    stories = """"""
    for file in os.scandir(stories_dir):
        if file.name.startswith(current_number):
            file_name = file.name

    with open(f"../../res/base_data/stories/{file_name}") as f:
        stories = f.read()

    stories = load_stories(stories)

    plain = """"""
    objects_file = f"../../res/base_data/domain_objects/{file_name}"
    # for file in os.scandir(domain_objects_dir):
    #     if file.name.startswith(current_number):
    #         objects_file = file.name

    with open(objects_file) as f:
        plain = f.read()

    objects, associations, subdomains, bounded_contexts = parse_domain_objects(plain)

    json_data = create_json(stories, objects, associations, subdomains, bounded_contexts)

    with open(f"../../res/task_data/perm/{file_name}.json", "w") as json_file:
        json_file.write(json_data)
