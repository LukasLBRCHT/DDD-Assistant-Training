import os

from datasets import Dataset

from Config import Config as Config
import json
import torch

class DataPreprocessor:
    def __init__(self, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.max_length = max_length

    def load_data(self, train_order, test_order):
        train_data = self.extract_from_json(train_order)
        train_dataset = Dataset.from_dict(train_data)

        test_data = self.extract_from_json(test_order)
        test_dataset = Dataset.from_dict(test_data)

        # # train/test with deterministic split
        # split = dataset.train_test_split(train_size=0.8, shuffle=False)
        # return split["train"], split["test"]

        return test_dataset, test_dataset

    def extract_from_json(self, order):
        directory = Config.Conversation_Phase_1_Data_Dir

        all_input_ids = []
        all_labels = []
        all_attention_masks = []

        token_lengths = []

        for domain in order:
            with open(f"{directory}/p1-conv-{domain.file.name}") as f:
                json_data = json.load(f)

                # Step 1: build full chat text
                full_text = self.tokenizer.apply_chat_template(
                    json_data,
                    tokenize=False,
                    add_generation_prompt=False
                )

            token_lengths.append(len(full_text))

            # ----------------------------------------------
            # 2. Tokenize entire conversation (truncate here)
            # ----------------------------------------------
            # Step 2: tokenize into dict with input_ids + mask
            tokenized = self.tokenizer(
                full_text,
                padding="max_length",
                truncation=True,
                max_length=self.max_length,
                return_tensors=None
            )

            ids = tokenized["input_ids"]
            mask = tokenized["attention_mask"]
            seq_len = len(ids)

            # ---------------------------------------------------
            # 3. Build label mask (assistant tokens only, others -100)
            # ---------------------------------------------------
            # Step 3: build labels (mask user/system with -100, keep assistant tokens)

            labels = [-100] * seq_len
            pos = 0  # tracks offset in the full tokenized text

            for msg in json_data:
                # tokenize this message **without** adding BOS/EOS
                msg_text = self.tokenizer.apply_chat_template(
                    [msg],
                    tokenize=False
                )
                msg_ids = self.tokenizer(msg_text, add_special_tokens=False)["input_ids"]
                msg_len = len(msg_ids)

                start = pos
                end = pos + msg_len

                if msg["role"] == "assistant":
                    # only write inside bounds
                    for i in range(start, min(end, seq_len)):
                        labels[i] = msg_ids[i - start]

                pos = end

                # If pos already exceeds seq_len → remaining msgs are truncated anyway
                if pos >= seq_len:
                    break

            # append example
            all_input_ids.append(ids)
            all_labels.append(labels)
            all_attention_masks.append(mask)

        print(max(token_lengths), sum(token_lengths) / len(token_lengths))

        return {
            "input_ids": all_input_ids,
            "labels": all_labels,
            "attention_mask": all_attention_masks,
        }
