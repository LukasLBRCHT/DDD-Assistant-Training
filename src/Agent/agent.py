from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import Config
import textwrap

local_dir = "../../models/qwen2.5-3b-awq/base"
model_name = "Qwen/Qwen2.5-7B-Instruct-AWQ"

def loadModel():
    model = AutoModelForCausalLM.from_pretrained(  # loading the model
        Config.MODEL_DIR,
        device_map="auto",
        torch_dtype=torch.float16,
    )
    model = model.to("cuda")
    tokenizer = AutoTokenizer.from_pretrained(  # loading the tokenizer of the model
        Config.MODEL_DIR
    )

    return model, tokenizer


def generate_answer(model, tokenizer, messages):

    text = tokenizer.apply_chat_template(  # tokenizer is configured
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)  # input is processed into tokens

    generated_ids = model.generate(  # response generation
        **model_inputs,
        max_new_tokens=512,
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids
        in zip(model_inputs.input_ids, generated_ids)
    ]  # this makes sure that only  the newly generated tokens remain

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]  # turns tokens into text string

    return response


def printResponse(response, prettyPrint=False):

    if prettyPrint: print("Assistant: " + "\n".join(textwrap.wrap(response, width=100, break_long_words=False)))
    else: print("Assistant: "+response)


if __name__ == "__main__":
    pass
    # load model
    model, tokenizer = loadModel()

    first_message = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."}
        ]
    prompt = [{"role": "user", "content": input("User: ")}]
    first_message.append(prompt)
    response = generate_answer(model, tokenizer, first_message)

    printResponse(response)

    while True:     # input loop for prompts
        prompt = input("User: ")
        if (prompt=="end"): break
        message = [{"role": "user", "content": prompt}]
        response = generate_answer(model, tokenizer, message)
        printResponse(response)

    print("Assistant: Bye.")
