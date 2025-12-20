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
