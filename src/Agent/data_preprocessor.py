import os

from datasets import Dataset

from Config import Config as Config
import json
import torch


# TODO turn raw data into json format so it can be used for training
# tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

class DataPreprocessor:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def load_data(self):

        sorted_data = Dataset.from_dict(self.extract_from_json())
        dataset = Dataset.from_dict({
            "input_ids": [torch.tensor(ids, dtype=torch.long) for ids in sorted_data["input_ids"]],
            "attention_mask": [torch.tensor(mask, dtype=torch.long) for mask in sorted_data["attention_mask"]],
            "labels": [torch.tensor(labels, dtype=torch.long) for labels in sorted_data["labels"]]
        })

        split = dataset.train_test_split(train_size=0.5)
        return split["train"], split["sandbox"]

    def extract_from_json(self):

        directory = Config.Training_Data_Dir
        all_input_ids = []
        all_labels = []
        all_attention_masks = []

        for file in os.scandir(directory):
            with open(file) as f:
                json_data = json.load(f)

                # Step 1: build full chat text
                text = self.tokenizer.apply_chat_template(
                    json_data["messages"],
                    tokenize=False,
                    add_generation_prompt=False
                )

                # Step 2: tokenize into dict with input_ids + mask
                tokens = self.tokenizer(text, return_tensors=None)
                ids = tokens["input_ids"]
                mask = tokens["attention_mask"]

                # Step 3: build labels (mask user/system with -100, keep assistant tokens)
                labels = [-100] * len(ids)  # init all ignored
                pos = 0
                for msg in json_data["messages"]:
                    msg_txt = self.tokenizer.apply_chat_template([msg], tokenize=False)
                    msg_ids = self.tokenizer(msg_txt, add_special_tokens=False)["input_ids"]

                    if msg["role"] == "assistant":
                        labels[pos:pos + len(msg_ids)] = msg_ids  # replace only assistant spans
                    pos += len(msg_ids)

                all_input_ids.append(ids)
                all_labels.append(labels)
                all_attention_masks.append(mask)

        return {
            "input_ids": all_input_ids,
            "attention_mask": all_attention_masks,
            "labels": all_labels
        }
