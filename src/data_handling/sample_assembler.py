"""
This class finalizes the training samples.
It extracts the task data and inputs it into example messages.
"""
import json
import os
from util import stnd_msg

task_data_dir = "../../res/task_data"
clean_data_dir = "../../res/clean_data"


class SampleAssembler:

    def assemble_training_samples(self):
        count = 1

        for file in os.scandir(task_data_dir):
            if not file.is_dir():
                with open(file, 'r') as f:
                    # build a conversation object here
                    input_data_for_conversation = f.read()
                    conv = Conversation(input_data_for_conversation)
                    conv.build_conversation()

                    # save training data sample

                    conv.save(count)

                    count += 1


"""
The conversation class represents one concrete conversation sample which is to be used for training.
It mainly supervises the seven prompts it is made out of.
"""


class Conversation:

    def __init__(self, input_data):

        json_data = json.loads(input_data)

        self.user_stories = json.dumps({"domain-information": json_data["domain-information"]},indent=2, ensure_ascii=False).replace('"','\\"')
        self.domain_objects = json.dumps(json_data["domain-objects"])
        self.subdomains = json.dumps(json_data["subdomains"])
        self.bounded_contexts = json.dumps(json_data["bounded-contexts"])
        self.other_input_data = ""

        self.messages = []  # supposed to be a json-object

    def build_conversation(self):

        # todo vllt den task state anders repräsentieren, z.B. mit einer variable
        task_state = ""  # und den dann pro turn erweitern

        # build all messages and add them to the list
        system_message = self.build_message("system", stnd_msg.sys_msg, do_format=False)
        self.messages.append(system_message)

        # turn 1
        user_message_1 = self.build_message("user", stnd_msg.user_initial_req_stories, content=self.user_stories)
        self.messages.append(user_message_1)
        assistant_message_1 = self.build_message("assistant", stnd_msg.assistant_stories_resp,
                                                 content=self.domain_objects)
        self.messages.append(assistant_message_1)

        # turn 2
        user_message_2 = self.build_message("user", stnd_msg.user_subdomains_req, content=self.domain_objects)
        self.messages.append(user_message_2)
        assistant_message_2 = self.build_message("assistant", stnd_msg.assistant_subdomains_resp,
                                                 content=self.subdomains)
        self.messages.append(assistant_message_2)

        # turn 3
        user_message_3 = self.build_message("user", stnd_msg.user_bounded_context_req, content=self.subdomains)
        self.messages.append(user_message_3)
        assistant_message_3 = self.build_message("assistant", stnd_msg.assistant_bounded_context_resp,
                                                 content=self.bounded_contexts)
        self.messages.append(assistant_message_3)

    def build_message(self, role, blueprint, content=None, do_format=True):

        if not do_format:
            prompt = blueprint
        else:
            prompt = blueprint.format(content)

        return {"role": f"{role}", "content": f"{prompt}"}

    def save(self, num):

        conversation = self.json_format()

        # make json file and save to clean data
        with open(f"../../res/clean_data/conversation{num}.json", "w") as conversation_file:
            conversation_file.write(conversation)

    def json_format(self):

        messages_in_json = ""
        # for message in self.messages:
        #     messages_in_json += '\n    ' + message + ","



        messages_in_json = messages_in_json.removesuffix(",")

        conv_in_json = f"""{{
  "messages": {json.dumps(self.messages, indent=2)}
  }}"""
        print(json.dumps(self.messages))
        return conv_in_json


if __name__ == "__main__":
    assembler = SampleAssembler()
    assembler.assemble_training_samples()
