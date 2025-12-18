"""
This class finalizes the training samples.
It extracts the task data and inputs it into example messages.
"""
import json
import os
from Config import Config
from conversation_assembler import SampleAssembler, Conversation, Message


def phase_1_split(conv, name):
    phase_1_data = conv[0:5]
    dumped_phase_1 = json.dumps(phase_1_data, indent=2, ensure_ascii=False)

    with open(f"../../res/clean_data/conv_phase_1/p1-{name}", "w") as output_file:
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
    for conv in os.scandir(Config.Conversation_Data_Dir):
        with open(conv) as conv_file:
            json_conv = json.loads(conv_file.read())

        phase_1_split(json_conv, conv.name)
        phase_2_split(json_conv, conv.name)
        phase_3_split(json_conv, conv.name)


def chunk_json_data(json_entries, chunk_size):
    current = 0
    chunks = []
    print(len(json_entries))

    if isinstance(json_entries, list):

        for i in range(0, len(json_entries), chunk_size):
            chunks.append(json_entries[i:i + chunk_size])

    else:
        for key in json_entries.keys():
            chunks.append({key: json_entries[key]})

    return chunks


def chunked_split(conv, phase, json_id, chunk_size):
    # prepare sys message and user query as always the same
    conversation = []

    conversation.append(conv.sys_msg)
    conversation.append(conv.user_msgs[phase - 1])
    llm_answer = conv.llm_msgs[phase - 1]

    # divide list entries
    # get it from json loads
    json_entries = json.loads(getattr(conv, json_id.replace(' ', '_')))[json_id]

    chunks = chunk_json_data(json_entries, chunk_size)
    chunk_num = 0

    for c in chunks:
        new_conv = conversation.copy()

        # pack json data into correct string
        json_chunk = json.dumps({json_id: c}, indent=2)

        print("chunk: " + json_chunk)

        answer_prompt = llm_answer.stnd_msg.format(json_chunk)

        message = {"role": f"{llm_answer.role}", "content": f"{answer_prompt}"}
        new_conv.append(message)

        file_name = conv.name.removesuffix(".json")
        with open(f"../../res/chunked_data/phase_{phase}/{file_name}-c{chunk_num}.json", "w") as conversation_file:
            conversation_file.write(json.dumps(new_conv, indent=2))

        chunk_num += 1


def split_conversations_meta(conv_metas):
    for conv in conv_metas:
        chunked_split(conv, 1, "domain objects", 5)
        chunked_split(conv, 2, "associations", 5)
        chunked_split(conv, 3, "subdomains", 1)
        chunked_split(conv, 4, "bounded contexts", 1)


if __name__ == "__main__":
    # get conversation data
    # split into steps, chunk data within each step
    assembler = SampleAssembler()
    conv_metas = assembler.get_conv_metadata()

    split_conversations_meta(conv_metas)
