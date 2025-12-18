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

    def collect(self, do_print=False):
        for file in os.scandir(Config.Task_Data_Dir):
            domain = Domain(file)
            self.domains.append(domain)
            domain.get_metadata()

            self.update_data(domain)

        if do_print:

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

    def get_custom_split(self):

        print("...preparing custom split...")

        self.collect()

        merged_bcs = list(filter(lambda domain: domain.subdomain_count > domain.bounded_context_count, self.domains))
        merged_bcs = sorted(merged_bcs, key=lambda domain: domain.story_count, reverse=True)

        split_bcs = list(filter(lambda domain: domain.subdomain_count < domain.bounded_context_count, self.domains))
        split_bcs = sorted(split_bcs, key=lambda domain: domain.story_count, reverse=True)

        little_name_changes = list(
            filter(lambda domain: domain.name_change_count == 0 or domain.name_change_count == 1, self.domains))
        little_name_changes = sorted(little_name_changes, key=lambda domain: domain.story_count, reverse=True)

        generic_domains = self.domains[91:] + [self.domains[10]]
        generic_domains = sorted(generic_domains, key=lambda domain: domain.story_count, reverse=True)

        all_domains = self.domains.copy()
        all_domains = sorted(all_domains, key=lambda domain: domain.story_count, reverse=True)

        distinct_lists = [split_bcs, merged_bcs, little_name_changes, generic_domains, all_domains]
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

        print("custom split successful")

        return train, test


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
            
            self.object_format_check(json_data["domain objects"])
            self.association_format_check(json_data["associations"])
            self.subdomain_format_check(json_data["subdomains"])
            self.bounded_context_format_check(json_data["bounded contexts"])

            self.story_count = len(json_data["domain-information"])
            self.object_count = len(json_data["domain objects"])
            self.association_count = len(json_data["associations"])
            self.subdomain_count = len(json_data["subdomains"]) - 1
            self.bounded_context_count = len(json_data["bounded contexts"])

            bounded_context_list = json_data["bounded contexts"]

            for bc in bounded_context_list:
                self.name_change_count += len(bounded_context_list[bc]["name changes"])


    def object_format_check(self, objects):

        error = ""

        for obj in objects:

            keys = list(obj.keys())
            if keys[0] != 'name':
                print(keys[0])
                error = True

            if keys[1] != 'description':
                error = True

            if len(keys) > 2:
                if keys[2] != 'attributes':
                    error = True

        if error:
            print(f"Object format error in {self.file}")


    def association_format_check(self, associations):

        error = False

        for asso in associations:

            keys = list(asso.keys())

            if keys[0] != 'from':
                error = True

            if keys[1] != 'to':
                error = True

            if keys[2] != 'description':
                error = True

        if error:
            print(f"Association format error in {self.file}")

    def subdomain_format_check(self, subdomains):
        error = False

        keys = list(subdomains.keys())
        if keys[len(keys)-1] != 'subdomain connections':
            error = True

        for sd in keys[:len(keys)-1]:

            if sd.islower():
                error = True

            inner_keys = list(subdomains[sd].keys())

            if inner_keys[0] != 'objects':
                error = True

        if error:
            print(f"Subdomain format error in {self.file}")

    def bounded_context_format_check(self, bounded_contexts):
        error = False

        keys = list(bounded_contexts.keys())

        for bc in keys:

            if bc.islower():
                error = True

            inner_keys = list(bounded_contexts[bc].keys())

            if inner_keys[0] != 'derived from':
                error = True

            derived_from = bounded_contexts[bc]['derived from']
            if not isinstance(derived_from, list):
                derived_from = [derived_from]

            for str_name in derived_from:
                if 'Subdomain' not in str_name:
                    error = True

            if inner_keys[1] != 'objects':
                error = True

            if inner_keys[2] != 'name changes':
                error = True

        if error:
            print(f"Bounded Context format error in {self.file}")


if __name__ == "__main__":
    md = Metadata()
    md.get_custom_split()
