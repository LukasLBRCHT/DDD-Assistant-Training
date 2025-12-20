import warnings

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from Config import Config as Config
import textwrap
from Agent.conversation_history import Conversation_History
from Agent.task_history import Task_History
from util.llm_util import load_model_basic

local_dir = "../../models/qwen2.5-3b-awq/base"
model_name = "Qwen/Qwen2.5-7B-Instruct-AWQ"


def generate_answer(model, tokenizer, prompt):
    text = tokenizer.apply_chat_template(  # tokenizer is configured
        prompt,
        tokenize=False,
        add_generation_prompt=True,
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)  # input is processed into tokens

    generated_ids = model.generate(  # response generation
        **model_inputs,
        max_new_tokens=512 * 3,
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids
        in zip(model_inputs.input_ids, generated_ids)
    ]  # this makes sure that only  the newly generated tokens remain

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]  # turns tokens into text string

    return response


def printResponse(response, prettyPrint=False):
    if prettyPrint:
        print("Assistant: " + "\n".join(textwrap.wrap(response, width=100, break_long_words=False)))
    else:
        print("Assistant: \033[34m" + response + "\033[0m")


def get_prompt():
    prompt = ""
    print("User:", end=" ")

    while True:  # input ends with two returns
        line = input()
        if line:
            prompt += line
        else:
            break

    return prompt


if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    # load model
    model, tokenizer = load_model_basic()

    history = Conversation_History()
    task_state = Task_History()

    messages = []

    # first_message = {"role": "system", "content": "You are DDD-Agent. Your main task is to be an assistant that helps "
    #                                               "with domain modeling according to Domain Driven Design. (Your workflow is "
    #                                               "1. Identify domain objects (Entities, Value Ojects, Associations)"
    #                                               "2. Define Subdomains by assigning each object to a specific Subdomain"
    #                                               "3. Assign the subdomains to Bounded Context and then define their associations"
    #                                               "via Context Mapping.)"
    #                                              "Introduce yourself to the user first."}
    first_message = [{"role": "system", "content": Config.SYS_TEST_PROMPT}]

    response = generate_answer(model, tokenizer, first_message)
    history.add_conversation_prompt(first_message, "system")

    printResponse(response)

    while True:  # input loop for prompts

        prompt = get_prompt()

        if prompt == "end": break
        prompt_with_history = f"""
        # Conversation-History-Context:(
        {history.compress(tokenizer)})
        
        # State of Subtasks:({task_state.compress()})
        
        # Current user request:
        {prompt}
        """

        message = [{"role": "user", "content": prompt_with_history}]
        #print(f"whole prompt: {prompt_with_history}")
        print("... processing ...")
        response = generate_answer(model, tokenizer, message)
        printResponse(response)

        history.add_conversation_prompt(prompt, "user")
        history.add_conversation_prompt(response, "assistant")
        task_state.update(prompt)
        task_state.update(response)
        # print(f"\n\ntask-state:{task_state.compress()}\n\n")

    print("Assistant: Bye.")
