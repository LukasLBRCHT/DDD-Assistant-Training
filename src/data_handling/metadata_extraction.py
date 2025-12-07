import json
import math
import os
from Config import Config

data = ["Stories", "Objects", "Associations", "Subdomains", "Bounded Contexts", "Name Changes"]


def remove_remaining(current, other):
    for d in current:
        if d in other:
            other.remove(d)

    return other


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

    def get_custom_order(self):

        print("...preparing custom order...")

        self.collect()

        ten_biggest = sorted(self.domains, key=lambda domain: domain.story_count)
        ten_biggest = ten_biggest[len(ten_biggest) - 10:len(ten_biggest)]

        merged_bcs = list(filter(lambda domain: domain.subdomain_count > domain.bounded_context_count, self.domains))

        split_bcs = list(filter(lambda domain: domain.subdomain_count < domain.bounded_context_count, self.domains))

        little_name_changes = list(
            filter(lambda domain: domain.name_change_count == 0 or domain.name_change_count == 1, self.domains))

        generic_domains = self.domains[91:] + [self.domains[10]]

        all_domains = self.domains.copy()
        distinct_lists = [split_bcs, merged_bcs, little_name_changes, generic_domains, ten_biggest, all_domains]
        train = []
        test = []

        for x in range(0, len(distinct_lists)):

            current_list = distinct_lists[x]
            other_lists = distinct_lists[:x] + distinct_lists[x + 1:]

            for o_l in other_lists:
                o_l = remove_remaining(current_list, o_l)  # avoid duplicates

            eighty_pct = round(len(current_list) * 0.8)

            train += current_list[:eighty_pct]
            test += current_list[eighty_pct:]

            if x == 2:
                test.append(train.pop())  # a small correction to get a clean 80|20 split

        print("custom order successful")

        return train + test


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
            self.subdomain_count = len(json_data["subdomains"]) - 1
            self.bounded_context_count = len(json_data["bounded contexts"])

            bounded_context_list = json_data["bounded contexts"]

            for bc in bounded_context_list:
                self.name_change_count += len(bounded_context_list[bc]["name changes"])


if __name__ == "__main__":
    md = Metadata()
    md.get_custom_order()
