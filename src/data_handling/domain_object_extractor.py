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

def parse_domain_objects():

    for file in os.scandir(domain_objects_dir):
        with open(file, 'r') as f:
            new_file_name = os.path.basename(f.name).removesuffix(".txt")

            text = f.read()
            split = text.split("associations:\n")
            objects = split[0]
            associations = split[1]

            result_data = ""

            for line in objects.splitlines():
                name = line
                object_json = f"{{\"name\": \"{name}\", \"description\": \"\"}},\n"
                result_data += object_json

            result_data.removesuffix(",")

            result_data += "\nassociations:\n"

            association_pattern = r"(.*?)-(.*)"
            for line in associations.splitlines():
                match = regex.search(association_pattern, line)

                match1 = match.group(1)
                match2 = match.group(2)

                object_json = f"{{\"from\": \"{match1}\", \"to\": \"{match2}\", \"description\": \"\"}},"

                result_data += object_json

            result_data.removesuffix(",")

            print(result_data)


if __name__ == "__main__":
    parse_domain_objects()