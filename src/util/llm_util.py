from unsloth import FastLanguageModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from Config import Config

def load_model_basic(model_dir=Config.MODEL_3B_DIR):

    model = AutoModelForCausalLM.from_pretrained(  # loading the model
        model_dir,
        device_map="auto",
        torch_dtype=torch.float16,
    )
    tokenizer = AutoTokenizer.from_pretrained(  # loading the tokenizer of the model
        Config.MODEL_7B_awq_DIR
    )

    return model, tokenizer


def load_model_lora(model_dir, max_seq_length, lora_rank):

    model, tokenizer = FastLanguageModel.from_pretrained(  # loading the model
        model_dir,
        max_seq_length=max_seq_length,
        max_lora_rank=lora_rank,
        gpu_memory_utilization=0.8
    )

    return model, tokenizer


def generate_answer(model, tokenizer, prompt, max_tokens):

    text = tokenizer.apply_chat_template(  # tokenizer is configured
        prompt,
        tokenize=False,
        add_generation_prompt=True,
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)  # input is processed into tokens

    generated_ids = model.generate(  # response generation
        **model_inputs,
        max_new_tokens=max_tokens,
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids
        in zip(model_inputs.input_ids, generated_ids)
    ]  # this makes sure that only  the newly generated tokens remain

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]  # turns tokens into text string

    return response