from datasets import Dataset

from Config import Config as Config
import json


class DataPreprocessor:
    def __init__(self, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.max_length = max_length

    def load_data(self, train_order, test_order):

        train_data = self.extract_conversations(train_order)
        train_dataset = Dataset.from_list(train_data)

        test_data = self.extract_conversations(test_order)
        test_dataset = Dataset.from_list(test_data)

        test_dataset_list = []

        for phase_idx in range(4):
            part = test_dataset.select(range(phase_idx, len(test_dataset), 4))
            test_dataset_list.append(part)

        return train_dataset, test_dataset, test_dataset_list

    def extract_conversations(self, order):

        directory = Config.Phase_Data_Dir_temp

        data = []

        token_lengths = []

        for domain in order:

            for phase in range(1, 5):
                with open(f"{directory}{phase}/p{phase}-conv-{domain.file.name}") as f:
                    json_data = json.load(f)

                full_text = self.tokenizer.apply_chat_template(
                    json_data,
                    tokenize=False,
                    add_generation_prompt=False
                )

                token_length = len(
                    self.tokenizer(full_text, add_special_tokens=False)["input_ids"]
                )
                token_lengths.append(token_length)

                data.append({"messages": full_text})

        print(f"\nmax token length: {max(token_lengths)}\navg token length: {sum(token_lengths) / len(token_lengths)}\nnum samples: {len(token_lengths)}")

        return data
