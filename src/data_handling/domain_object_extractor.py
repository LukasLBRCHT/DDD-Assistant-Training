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

def parse_domain_objects(txt):

    text = txt
    split = text.split("\nassociations:\n")
    objects = split[0]
    associations = split[1]

    result_data = ""

    for line in objects.splitlines():
        if not line:
            continue
        name = line
        object_json = f"      {{\"name\": \"{name}\", \"description\": \"\"}},\n"
        result_data += object_json

    result_data.removesuffix(",\n")

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

    result_data.removesuffix(",\n")

    print(result_data)


if __name__ == "__main__":
    plain = """Food Coordinator
Donation Offer

Delivery
-Route
-Food Donation

Weekly Report
-Food Recovery Data

Recovery Driver
Pickup Assignment?
Delivery Confirmation (to Coordinator? and Donor, maybe auch zu den reports)
Issue Report (to Coordinator)

Food Donation
-Food Item

Donor
Recovery Network
-Available Food Items
-Pickup Times
Monthly Report

Distribution Partner
-Daily Capacity
Delivery Log (maybe das zu Reports)
Shortage Report (nochmal genauer benennen)

Community Volunteer
-Completed Hours
Local Events

Government Health Inspector
-Food Recovery Data

associations:
Food Donation-Distribution Partner
Donor-Donation Offer
Donor-Food Donation
Food Coordinator-Donation Offer
Donor-Recovery Network
Distribution Partner-Recovery Network
Volunteer-Food Donation

Food Coordinator-Recovery Network
Food Coordinator-Pickup Assignment
Food Coordinator-Delivery
Food Coordinator-Pickup Assignment
Pickup Assignment-Recovery Driver
Recovery Driver-Delivery
Recovery Driver-Issue Report
Issue Report-Food Coordinator
Distribution Partner-Delivery
Recovery Driver-Delivery Confirmation
Distribution Partner-Delivery Confirmation
Distribution Partner-Delivery Log
Delivery Confirmation-Food Recovery Data
Delivery Log-Food Recovery Data
Distribution Partner-Shortage Report
Shortage Report-Food Coordinator

Donor-Monthly Report
Food Recovery Data-Monthly Report
Food Recovery Data-Weekly Report
Food Coordinator-Weekly Report

Recovery Network-Local Event
Volunteer-Local Event

Government Health Inspector-Food Recovery Data
Government Health Inspector-Evaluation Notice
Evaluation Notice-Food Coordinator"""

    parse_domain_objects(plain)
