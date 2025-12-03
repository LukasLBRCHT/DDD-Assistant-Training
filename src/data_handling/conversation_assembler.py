"""
This class finalizes the training samples.
It extracts the task data and inputs it into example messages.
"""
import json
import os
from Config import Config

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from util import stnd_msg

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



"""
The conversation class represents one concrete conversation sample which is to be used for training.
It mainly supervises the seven prompts it is made out of.
"""


class Conversation:

    def __init__(self, input_data):

        json_data = json.loads(input_data)

        self.user_stories = json.dumps({"domain-information": json_data["domain-information"]},indent=2, ensure_ascii=False)
        self.domain_objects = json.dumps({"domain objects": json_data["domain objects"]},indent=2, ensure_ascii=False)
        self.associations = json.dumps({"associations": json_data["associations"]}, indent=2, ensure_ascii=False)
        self.subdomains = json.dumps({"subdomains": json_data["subdomains"]},indent=2, ensure_ascii=False)
        self.bounded_contexts = json.dumps({"bounded contexts": json_data["bounded contexts"]},indent=2, ensure_ascii=False)
        self.other_input_data = ""

        self.messages = []  # supposed to be a json-object

    def build_conversation(self):

        # todo vllt den task state anders repräsentieren, z.B. mit einer variable
        task_state = ""  # und den dann pro turn erweitern

        # build all messages and add them to the list
        system_message = self.build_message("system", stnd_msg.sys_msg(), do_format=False)
        self.messages.append(system_message)

        # turn 1
        user_message_1 = self.build_message("user", stnd_msg.user_turn_1(), content=self.user_stories)
        self.messages.append(user_message_1)
        assistant_message_1 = self.build_message("assistant", stnd_msg.assistant_stories_resp,
                                                 content=self.domain_objects)
        self.messages.append(assistant_message_1)

        # turn 2
        user_message_2 = self.build_message("user", stnd_msg.user_turn_2(), content="")
        self.messages.append(user_message_2)
        assistant_message_2 = self.build_message("assistant", "here are the associations: {}",
                                                 content=self.associations)
        self.messages.append(assistant_message_2)

        # turn 3
        user_message_3 = self.build_message("user", stnd_msg.user_turn_3(), content=self.domain_objects)
        self.messages.append(user_message_3)
        assistant_message_3 = self.build_message("assistant", stnd_msg.assistant_subdomains_resp,
                                                 content=self.subdomains)
        self.messages.append(assistant_message_3)

        # turn 4
        user_message_4 = self.build_message("user", stnd_msg.user_turn_4(), content=self.subdomains)
        self.messages.append(user_message_4)
        assistant_message_4 = self.build_message("assistant", stnd_msg.assistant_bounded_context_resp,
                                                 content=self.bounded_contexts)
        self.messages.append(assistant_message_4)

    def build_message(self, role, blueprint, content=None, do_format=True):

        if not do_format:
            prompt = blueprint
        else:
            prompt = blueprint.format(content)

        return {"role": f"{role}", "content": f"{prompt}"}

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
