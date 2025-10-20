"""
This class finalizes the training samples.
It extracts the task data and inputs it into example messages.
"""
import os

task_data_dir = "../../res/task_data"
clean_data_dir = "../../res/clean_data"


class SampleAssembler:

    def assemble_training_samples(self):
        for file in os.scandir(task_data_dir):
            with open(file, 'r') as f:
                # build a conversation object here
                input_data_for_conversation = "get from file and other sources"
                conv = Conversation(input_data_for_conversation)
                conv.build_conversation()


"""
The conversation class represents one concrete conversation sample which is to be used for training.
It mainly supervises the seven prompts it is made out of.
"""


class Conversation:

    def __init__(self, input_data):
        self.user_stories = input_data
        self.entities = input_data
        self.value_objects = input_data
        self.associations = input_data
        self.subdomains = input_data
        self.bounded_contexts = input_data
        self.other_input_data = input_data

        self.messages = []  # supposed to be a json-object

    def build_conversation(self):
        # build all messages and add them to the list
        system_message = self.build_message("system", "system_prompt_PLACEHOLDER")
        self.messages.append(system_message)

        # turn 1
        user_message_1 = self.build_message("user", "content_including_stories_PLACEHOLDER")
        self.messages.append(user_message_1)
        assistant_message_1 = self.build_message("assistant", "content_including_objects_PLACEHOLDER")
        self.messages.append(assistant_message_1)

        # turn 2
        user_message_2 = self.build_message("user", "content_including_task_state_PLACEHOLDER")
        self.messages.append(user_message_2)
        assistant_message_2 = self.build_message("assistant", "content_including_subdomains_PLACEHOLDER")
        self.messages.append(assistant_message_2)

        # turn 3
        user_message_3 = self.build_message("user", "content_including_task_state_PLACEHOLDER")
        self.messages.append(user_message_3)
        assistant_message_3 = self.build_message("assistant", "content_including_contexts_PLACEHOLDER")
        self.messages.append(assistant_message_3)

    def build_message(self, role, some_content):
        return f"{role}: {some_content}"

    def save_conversation(self):
        # make json file and save to clean data
        pass
