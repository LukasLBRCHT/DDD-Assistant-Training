
import os

import regex

from data_handling.domain import Domain_Object, Bounded_Context

domain_objects_dir = "../../res/base_data/domain_objects"
stories_dir = "../../res/base_data/stories"
subtask_format_url = "../util/subtask_format"

ws = " "


def extract_lists(subdomain_objects):
    objects = subdomain_objects.split(",")
    subdomain_objects = ""
    bc_objects = ""
    bc = Bounded_Context()

    for obj in objects:
        plain_strg = obj.strip()
        object_string = f"\"{plain_strg}\","

        if "(" in plain_strg:
            split = plain_strg.split("(")
            original = split[0].strip()
            object_string = f"\"{original}\","
            renaming = split[1].removesuffix(")")

            bc.add_renaming(original, renaming)
            renaming = f"\"{renaming}\","

            bc_objects += renaming
        else:
            bc_objects += object_string

        subdomain_objects += object_string

    bc_name_changes = bc.compress()

    subdomain_objects = subdomain_objects.removesuffix(",")
    bc_objects = bc_objects.removesuffix(",")
    bc_name_changes = bc_name_changes.removesuffix(",")

    return subdomain_objects, bc_objects, bc_name_changes


def extract_objects(objs):
    extracted_objects = ""

    object_list = []
    last_root = None

    for line in objs.splitlines():
        if not line:
            continue
        name = line.strip()
        new_object = Domain_Object(name)

        if not name.startswith("-"):
            last_root = new_object
        else:
            name = name.removeprefix("-")
            new_object.set_name(name)

            skip = name.startswith("(")
            if skip:
                name = name.removeprefix("(")
                name = name.removesuffix(")")

            last_root.add_attribute(name)

            if skip:
                continue

        object_list.append(new_object)

    for obj in object_list:

        attributes_string = ""
        if obj.object_attributes:
            attributes_string += ", \"attributes\": ["
            for attr in obj.object_attributes:
                attributes_string += f"\"{attr}\","
            attributes_string = attributes_string.removesuffix(",")
            attributes_string += "]"


        object_json = f"      {{\"name\": \"{obj.object_name}\", \"description\": \"\"{attributes_string}}},\n"
        extracted_objects += object_json

    extracted_objects = extracted_objects.removesuffix(",\n")

    return extracted_objects


def extract_subd_n_bc(subdomains):
    extracted_subdomains = ""
    extracted_bounded_contexts = ""

    subdomain_pattern = r"(.*?):(.*)"
    for line in subdomains.splitlines():

        if not line:
            continue

        match = regex.search(subdomain_pattern, line)

        subdomain_name = match.group(1)
        subdomain_objects = match.group(2)

        subdomain_objects, bc_objects, name_changes = extract_lists(subdomain_objects)

        object_json_subdomain = f"{ws * 6}\"{subdomain_name}\": {{\n{ws * 10}\"objects\" : [{subdomain_objects}]\n{ws * 6}}},\n"
        object_json_bounded_context = f"{ws * 6}\"{subdomain_name}\": {{\n{ws * 10}\"derived from\": \"{subdomain_name} Subdomain\",\n{ws * 10}\"objects\" : [{bc_objects}],\n{ws * 10}\"name changes\" : [{name_changes}]\n{ws * 6}}},\n"

        extracted_subdomains += object_json_subdomain
        extracted_bounded_contexts += object_json_bounded_context

    return extracted_subdomains, extracted_bounded_contexts

def parse_domain_objects(txt):

    text = txt
    split = text.split("\nnext:\n")
    objects = split[0]
    associations = split[1]
    subdomains = split[2]
    subdomain_connections = split[3]

    extracted_objects = extract_objects(objects)

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

    connection_list = ""

    for line in subdomain_connections.splitlines():
        if not line:
            continue

        connection_list += f"\"{line}\","

    connection_list = connection_list.removesuffix(",")
    connections_json = f"\"subdomain connections\": [{connection_list}]"

    extracted_associations = extracted_associations.removesuffix(",\n")

    extracted_subdomains, extracted_bounded_contexts = extract_subd_n_bc(subdomains)

    extracted_subdomains = extracted_subdomains.removesuffix(",\n")
    extracted_bounded_contexts = extracted_bounded_contexts.removesuffix(",\n")

    return extracted_objects,extracted_associations,extracted_subdomains,extracted_bounded_contexts, connections_json

def create_json(stories, obj, asso, sub, bc, con):
    with open(subtask_format_url, 'r') as format_file:
        subtask_format = format_file.read()

    json_data = subtask_format.format(stories, obj, asso, sub, con, bc)

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

    current_number = "90"

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

    objects, associations, subdomains, bounded_contexts, connections = parse_domain_objects(plain)

    json_data = create_json(stories, objects, associations, subdomains, bounded_contexts, connections)

    with open(f"../../res/task_data//{file_name}.json", "w") as json_file:
        json_file.write(json_data)
