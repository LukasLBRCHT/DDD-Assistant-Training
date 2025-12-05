import json
import math
import os
from Config import Config

data = ["Stories", "Objects", "Associations", "Subdomains", "Bounded Contexts", "Name Changes"]


class Metadata:
    counts = {"Stories": [], "Objects": [], "Associations": [], "Subdomains": [], "Bounded Contexts": [],
              "Name Changes": []}
    domains = []

    def collect(self):
        for file in os.scandir(Config.Task_Data_Dir):
            domain = Domain(file)
            self.domains.append(domain)
            domain.get_metadata()

            self.update_data(domain)

        self.extract_global_metadata()

    def update_data(self, domain):

        self.counts["Stories"].append(domain.story_count)
        self.counts["Objects"].append(domain.object_count)
        self.counts["Associations"].append(domain.association_count)
        self.counts["Subdomains"].append(domain.subdomain_count)
        self.counts["Bounded Contexts"].append(domain.bounded_context_count)
        self.counts["Name Changes"].append(domain.name_change_count)

    def extract_global_metadata(self):

        for key in self.counts.keys():
            print(key + ":")
            list_of_counts = self.counts[key]
            print(f"Smallest amount: {min(list_of_counts)}")
            print(f"Greatest amount: {max(list_of_counts)}")
            print(f"Average amount: {sum(list_of_counts) / len(list_of_counts)}\n")

        print("the ten biggest:")
        ten_biggest = sorted(self.domains, key=lambda domain: domain.story_count)
        ten_biggest = ten_biggest[len(ten_biggest)-10:len(ten_biggest)]
        for entry in ten_biggest:
            print(entry.file.name)

        merged_bcs = list(filter(lambda domain: domain.subdomain_count > domain.bounded_context_count, self.domains))
        print("\nmerged bcs:")
        for entry in merged_bcs:
            print(entry.file.name)

        no_name_changes = list(filter(lambda domain: domain.name_change_count==0, self.domains))
        print("\nno name change:")
        for entry in no_name_changes:
            print(entry.file.name)


class Domain:
    story_count = 0
    object_count = 0
    association_count = 0
    subdomain_count = 0
    bounded_context_count = 0
    name_change_count = 0

    def __init__(self, file):
        self.file = file

    def get_metadata(self):
        with open(self.file, "r") as domain_data:
            json_data = json.loads(domain_data.read())

            self.story_count = len(json_data["domain-information"])
            self.object_count = len(json_data["domain objects"])
            self.association_count = len(json_data["associations"])
            self.subdomain_count = len(json_data["subdomains"])-1
            self.bounded_context_count = len(json_data["bounded contexts"])

            bounded_context_list = json_data["bounded contexts"]

            for bc in bounded_context_list:
                self.name_change_count += len(bounded_context_list[bc]["name changes"])


if __name__ == "__main__":
    md = Metadata()
    md.collect()
