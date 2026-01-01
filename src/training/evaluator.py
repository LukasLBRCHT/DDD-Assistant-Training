import json
import os

from util.llm_util import load_model_basic, generate_answer, load_model_finetuned
from data_handling.metadata_extraction import Metadata
from Config import Config

def evaluate(test_split):

    max_tokens = 1024

    for domain in test_split:
        with open(f"{Config.Conversation_Data_Dir}/conv-{domain.file.name}") as f:
            json_conv = json.load(f)
            print(domain.file.name)

            output_text = "Subdomain-Request:\n"

            subdomain_request, expected_response = load_prompt(json_conv, phase=3)
            generated_response = generate_answer(model, tokenizer, subdomain_request, max_tokens)

            output_text += subdomain_request[1]["content"]
            output_text += "\n======================================================================================\n"
            output_text += "Generated Subdomain-Response:\n"
            output_text += generated_response
            output_text += "\n======================================================================================\n"
            output_text += "Expected Response:\n"
            output_text += expected_response["content"]
            output_text += "\n======================================================================================\n"

            bounded_context_request, expected_response = load_prompt(json_conv, phase=4)
            generated_response = generate_answer(model, tokenizer, bounded_context_request, max_tokens)

            output_text += "Bounded-Context-Request:\n"
            output_text += bounded_context_request[1]["content"]
            output_text += "\n======================================================================================\n"
            output_text += "Generated Bounded-Context-Response:\n"
            output_text += generated_response
            output_text += "\n======================================================================================\n"
            output_text += "Expected Response:\n"
            output_text += expected_response["content"]

            file_name = domain.file.name.removesuffix(".json")
            with open(f"../../res/eval_data/eval-{file_name}", "w") as eval_file:
                eval_file.write(output_text)

            return


def load_prompt(json_conv, phase):

    request = [json_conv[0], json_conv[phase*2-1]]
    response = json_conv[phase*2]

    return request, response


if __name__ == "__main__":

    model, tokenizer = load_model_finetuned()
    #todo load weights

    md = Metadata()
    _, test_split = md.get_custom_split()
    evaluate(test_split)



