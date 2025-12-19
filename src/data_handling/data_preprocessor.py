import math
import os

from datasets import Dataset

from Config import Config as Config
import json
import torch

class DataPreprocessor:
    def __init__(self, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.max_length = max_length

    def load_data(self, train_order, test_order, phase, chunked=False):

        match phase:
            case 1:
                directory = Config.Phase_1_Data_Dir
                if not chunked:
                    directory = Config.Phase_1_Whole
                domain_attribute = "object_count"
                factor = 5
            case 2:
                directory = Config.Phase_2_Data_Dir
                if not chunked:
                    directory = Config.Phase_2_Whole
                domain_attribute = "association_count"
                factor = 5
            case 3:
                directory = Config.Phase_3_Data_Dir
                if not chunked:
                    directory = Config.Phase_3_Whole
                domain_attribute = "subdomain_count"
                factor = 1
            case 4:
                directory = Config.Phase_4_Data_Dir
                if not chunked:
                    directory = Config.Phase_4_Whole
                domain_attribute = "bounded_context_count"
                factor = 1

        if not chunked:
            train_data = self.extract_from_json(train_order, directory, phase, max_length=self.max_length)
            train_dataset = Dataset.from_dict(train_data)

            test_data = self.extract_from_json(test_order, directory, phase, max_length=2048)
            test_dataset = Dataset.from_dict(test_data)
        else:
            train_data = self.extract_from_json_chunked(train_order, directory, domain_attribute, factor)
            train_dataset = Dataset.from_dict(train_data)

            test_data = self.extract_from_json_chunked(test_order, directory, domain_attribute, factor)
            test_dataset = Dataset.from_dict(test_data)

        # # train/test with deterministic split
        # split = dataset.train_test_split(train_size=0.8, shuffle=False)
        # return split["train"], split["test"]

        return train_dataset, test_dataset

    def extract_from_json(self, order, sample_dir, phase, max_length):
        directory = sample_dir

        all_input_ids = []
        all_labels = []
        all_attention_masks = []

        token_lengths = []

        for domain in order:
            with open(f"{directory}/p{phase}-conv-{domain.file.name}") as f:
                json_data = json.load(f)

                # Step 1: build full chat text
                full_text = self.tokenizer.apply_chat_template(
                    json_data,
                    tokenize=False,
                    add_generation_prompt=False
                )

            token_length = len(
                self.tokenizer(full_text, add_special_tokens=False)["input_ids"]
            )
            token_lengths.append(token_length)

            # ----------------------------------------------
            # 2. Tokenize entire conversation (truncate here)
            # ----------------------------------------------
            # Step 2: tokenize into dict with input_ids + mask
            tokenized = self.tokenizer(
                full_text,
                padding="max_length",
                truncation=True,
                max_length=max_length,
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

        print(f"\nmax token length: {max(token_lengths)}\navg token length: {sum(token_lengths) / len(token_lengths)}\nnum samples: {len(token_lengths)}")

        return {
            "input_ids": all_input_ids,
            "labels": all_labels,
            "attention_mask": all_attention_masks,
        }

    def extract_from_json_chunked(self, order, chunk_dir, domain_attribute, factor):
        directory = chunk_dir

        all_input_ids = []
        all_labels = []
        all_attention_masks = []

        token_lengths = []

        for domain in order:

            num = math.ceil(getattr(domain, domain_attribute)/factor)

            domain_name = domain.file.name.removesuffix(".json")
            for chunk_num in range(0,num):

                with open(f"{directory}/{domain_name}-c{chunk_num}.json") as f:
                    json_data = json.load(f)

                    # Step 1: build full chat text
                    full_text = self.tokenizer.apply_chat_template(
                        json_data,
                        tokenize=False,
                        add_generation_prompt=False
                    )

                token_length = len(
                    self.tokenizer(full_text, add_special_tokens=False)["input_ids"]
                )
                token_lengths.append(token_length)

                # ----------------------------------------------
                # 2. Tokenize entire conversation (truncate here)
                # ----------------------------------------------
                # Step 2: tokenize into dict with input_ids + mask
                tokenized = self.tokenizer(
                    full_text,
                    padding=False,
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

        print(f"\nmax token length: {max(token_lengths)}\navg token length: {sum(token_lengths) / len(token_lengths)}\nnum samples: {len(token_lengths)}")


        return {
            "input_ids": all_input_ids,
            "labels": all_labels,
            "attention_mask": all_attention_masks,
        }
