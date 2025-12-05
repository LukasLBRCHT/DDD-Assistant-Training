"""
This class finalizes the training samples.
It extracts the task data and inputs it into example messages.
"""
import json
import os
from Config import Config


# Todo Aufteilung nach Kategorien


def phase_1_split(conv, name):

    phase_1_data = conv[0:5]
    dumped_phase_1 = json.dumps(phase_1_data, indent=2, ensure_ascii=False)

    with open(f"../../res/clean_data/conv_phase_1/p1-{name}","w") as output_file:
        output_file.write(dumped_phase_1)


def phase_2_split(conv, name):
    phase_2_data = [conv[0]] + conv[5:7]
    dumped_phase_2 = json.dumps(phase_2_data, indent=2, ensure_ascii=False)

    with open(f"../../res/clean_data/conv_phase_2/p2-{name}", "w") as output_file:
        output_file.write(dumped_phase_2)


def phase_3_split(conv, name):
    phase_3_data = [conv[0]] + conv[7:9]
    dumped_phase_3 = json.dumps(phase_3_data, indent=2, ensure_ascii=False)

    with open(f"../../res/clean_data/conv_phase_3/p3-{name}", "w") as output_file:
        output_file.write(dumped_phase_3)


def split_conversations():

    # todo metadata checks for smarter splitting

    for conv in os.scandir(Config.Conversation_Data_Dir):

        with open(conv) as conv_file:
            json_conv = json.loads(conv_file.read())

        phase_1_split(json_conv, conv.name)
        phase_2_split(json_conv, conv.name)
        phase_3_split(json_conv, conv.name)


if __name__ == "__main__":
    split_conversations()
