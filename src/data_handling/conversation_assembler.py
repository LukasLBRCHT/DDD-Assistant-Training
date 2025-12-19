"""
This class finalizes the training samples.
It extracts the task data and inputs it into example messages.
"""
import json
import os
import random
from util import stnd_msg

# from sample_splitter import split_conversations

task_data_dir = "../../res/task_data"
clean_data_dir = "../../res/clean_data/conversations"


class SampleAssembler:

    def assemble_training_samples(self):
        for file in os.scandir(task_data_dir):
            with open(file, 'r') as f:
                # build a conversation object here
                input_data_for_conversation = f.read()
                conv = Conversation(input_data_for_conversation)
                conv.build_conversation()

                # save training data sample

                conv.save(file.name.removesuffix(".json"))

    def get_conv_metadata(self):

        metadata = []

        for file in os.scandir(task_data_dir):
            with open(file, 'r') as f:
                # build a conversation object here
                input_data_for_conversation = f.read()
                conv = Conversation(input_data_for_conversation, file.name)
                conv.build_conversation_meta()
                metadata.append(conv)

        return metadata


def get_order(subdomains_json):
    keys = list(subdomains_json.keys())
    subdomain_names = keys[:len(subdomains_json) - 1]
    random.shuffle(subdomain_names)
    return subdomain_names


def order_subdomains(subdomains_json, order):
    ordered_subdomains = {}

    for sd in order:
        data = subdomains_json[sd]
        ordered_subdomains[sd] = data

    return ordered_subdomains


def find_contexts(sd, bounded_context_json):
    contexts = []

    for key in list(bounded_context_json.keys()):

        derived = bounded_context_json[key]["derived from"]

        if not isinstance(derived, list):
            derived = [derived]

        for d in derived:
            if sd in d:
                contexts.append((key, bounded_context_json[key]))

    return contexts


def order_bounded_contexts(bounded_context_json, order):
    ordered_bounded_contexts = {}

    for sd in order:

        bcs = find_contexts(sd, bounded_context_json)

        for bc in bcs:
            name = bc[0]
            data = bc[1]
            ordered_bounded_contexts[name] = data

    return ordered_bounded_contexts


class Message:

    def __init__(self, role, prompt, content):
        self.role = role
        self.stnd_msg = prompt
        self.content = content


"""
The conversation class represents one concrete conversation sample which is to be used for training.
It mainly supervises the seven prompts it is made out of.
"""


class Conversation:

    def __init__(self, input_data, name=None):

        json_data = json.loads(input_data)

        self.user_stories = json.dumps({"domain-information": json_data["domain-information"]}, indent=2,
                                       ensure_ascii=False)
        self.domain_objects = json.dumps({"domain objects": json_data["domain objects"]}, indent=2, ensure_ascii=False)
        self.associations = json.dumps({"associations": json_data["associations"]}, indent=2, ensure_ascii=False)

        order = get_order(json_data["subdomains"])
        self.subdomains = json.dumps({"subdomains": json_data["subdomains"]}, indent=2,
                                     ensure_ascii=False)
        self.bounded_contexts = json.dumps(
            {"bounded contexts": json_data["bounded contexts"]}, indent=2,
            ensure_ascii=False)
        self.other_input_data = ""

        self.name = name
        self.messages = []  # supposed to be a json-object
        self.sys_msg = None
        self.user_msgs = []
        self.llm_msgs = []

    def build_conversation(self):

        # build all messages and add them to the list
        system_message = self.build_message("system", stnd_msg.sys_msg(), do_format=False)
        self.messages.append(system_message)

        # turn 1
        user_message_1 = self.build_message("user", stnd_msg.user_turn_1(), content=self.user_stories)
        self.messages.append(user_message_1)
        assistant_message_1 = self.build_message("assistant", stnd_msg.llm_turn_1(),
                                                 content=self.domain_objects)
        self.messages.append(assistant_message_1)

        # turn 2
        user_message_2 = self.build_message("user", stnd_msg.user_turn_2(), content=self.domain_objects)
        self.messages.append(user_message_2)
        assistant_message_2 = self.build_message("assistant", stnd_msg.llm_turn_2(),
                                                 content=self.associations)
        self.messages.append(assistant_message_2)

        # turn 3

        base_content = [self.domain_objects, self.associations]

        user_message_3 = self.build_message("user", stnd_msg.user_turn_3(), content=base_content)
        self.messages.append(user_message_3)
        assistant_message_3 = self.build_message("assistant", stnd_msg.llm_turn_3(),
                                                 content=self.subdomains)
        self.messages.append(assistant_message_3)

        # turn 4

        base_content = [self.domain_objects, self.subdomains]

        user_message_4 = self.build_message("user", stnd_msg.user_turn_4(), content=base_content)
        self.messages.append(user_message_4)
        assistant_message_4 = self.build_message("assistant", stnd_msg.llm_turn_4(),
                                                 content=self.bounded_contexts)
        self.messages.append(assistant_message_4)

    def build_conversation_meta(self):

        # build all messages and add them to the list
        system_message = self.build_message("system", stnd_msg.sys_msg(), do_format=False)
        self.sys_msg = system_message

        # turn 1
        user_message_1 = self.build_message("user", stnd_msg.user_turn_1(), content=self.user_stories)
        self.user_msgs.append(user_message_1)
        assistant_message_1 = self.build_message_meta("assistant", stnd_msg.llm_turn_1(),
                                                      content=self.domain_objects)
        self.llm_msgs.append(assistant_message_1)

        # turn 2
        user_message_2 = self.build_message("user", stnd_msg.user_turn_2(), content=self.domain_objects)
        self.user_msgs.append(user_message_2)
        assistant_message_2 = self.build_message_meta("assistant", stnd_msg.llm_turn_2(),
                                                      content=self.associations)
        self.llm_msgs.append(assistant_message_2)

        # turn 3

        base_content = [self.domain_objects, self.associations]

        user_message_3 = self.build_message("user", stnd_msg.user_turn_3(), content=base_content)
        self.user_msgs.append(user_message_3)
        assistant_message_3 = self.build_message_meta("assistant", stnd_msg.llm_turn_3(),
                                                      content=self.subdomains)
        self.llm_msgs.append(assistant_message_3)

        # turn 4

        base_content = [self.domain_objects, self.subdomains]

        user_message_4 = self.build_message("user", stnd_msg.user_turn_4(), content=base_content)
        self.user_msgs.append(user_message_4)
        assistant_message_4 = self.build_message_meta("assistant", stnd_msg.llm_turn_4(),
                                                      content=self.bounded_contexts)
        self.llm_msgs.append(assistant_message_4)

    def build_message(self, role, blueprint, content=None, do_format=True):

        if not do_format:
            prompt = blueprint
        else:

            if isinstance(content, list):

                merge = ""
                for base_data in content:
                    merge += base_data
                    merge += "\n```\n```json\n"
                merge = merge.removesuffix("\n```\n```json\n")

                prompt = blueprint.format(merge)

            else:
                prompt = blueprint.format(content)

        return {"role": f"{role}", "content": f"{prompt}"}

    def build_message_meta(selfrole, role, blueprint, content=None):

        if isinstance(content, list):

            merge = ""
            for base_data in content:
                merge += base_data
                merge += "\n```\n```json\n"
            merge = merge.removesuffix("\n```\n```json\n")

            content = merge

        msg = Message(role, blueprint, content)

        return msg

    def save(self, name):

        conversation = self.messages

        # make json file and save to clean data
        with open(f"../../res/clean_data/conversations/conv-{name}.json", "w") as conversation_file:
            conversation_file.write(json.dumps(conversation, indent=2))

    def json_format(self):

        messages_in_json = ""
        # for message in self.messages:
        #     messages_in_json += '\n    ' + message + ","

        messages_in_json = messages_in_json.removesuffix(",")

        conv_in_json = f"""{{
  "messages": {json.dumps(self.messages, indent=2)}
  }}"""

        return conv_in_json


if __name__ == "__main__":
    assembler = SampleAssembler()
    assembler.assemble_training_samples()

    # split_conversations()
