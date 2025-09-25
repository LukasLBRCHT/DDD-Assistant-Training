from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
import torch
import Config
from peft import get_peft_config, get_peft_model, LoraConfig, TaskType
import time
from datasets import Dataset

def load_lora_model():
    model = AutoModelForCausalLM.from_pretrained(  # loading the model
        Config.MODEL_7B_DIR,
        device_map="auto",
        torch_dtype=torch.float16,
    )
    model = model.to("cuda")

    peft_config = LoraConfig(task_type=TaskType.CAUSAL_LM, inference_mode=False, r=32, lora_alpha=16, lora_dropout=0.1,
                             target_modules=[
                                 "q_proj", "k_proj", "v_proj", "o_proj",
                                 "gate_proj", "up_proj", "down_proj"]
                             )  # created LoRA-Config for Finetuning

    lora_model = get_peft_model(model, peft_config)  # applied LoRA config to the model
    tokenizer = AutoTokenizer.from_pretrained(  # loading the tokenizer of the model
        Config.MODEL_7B_DIR
    )
    
    return lora_model, tokenizer


def load_custom_dataset():  # TODO: aus Datei laden

    list_of_train_texts = ["aadf", "adadsf", "adasdf"]
    list_of_eval_texts = ["aadf", "adadsf", "adasdf"]

    train_dataset = Dataset.from_dict({"text": list_of_train_texts})
    eval_dataset = Dataset.from_dict({"text": list_of_eval_texts})

    return train_dataset, eval_dataset


def configure_training_arguments():
    output_dir = f'./lora-ddd-agent-training-{str(int(time.time()))}'

    # TODO: hyperparameter bestimmen
    lora_training_args = TrainingArguments(
        output_dir=output_dir,
        warmup_steps=2,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        max_steps=1000,
        learning_rate=2e-4,
        optim="paged_adamw_8bit",
        logging_steps=25,
        logging_dir="./logs",
        save_strategy="steps",
        save_steps=25,
        eval_strategy="steps",
        eval_steps=25,
        do_eval=True,
        gradient_checkpointing=True,
        report_to="none",
        overwrite_output_dir=False,
        group_by_length=True,
    )

    return lora_training_args


def initialize_trainer(lora_model, tokenizer, train_args, train_data, eval_data):
    lora_model.config.use_cache = False

    lora_trainer = Trainer(
        model=lora_model,
        train_dataset=train_data,
        eval_dataset=eval_data,
        args=train_args,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )

    return lora_trainer


if __name__ == "__main__":
    # load model
    model, tokenizer = load_lora_model()
    
    train_data, eval_data = load_custom_dataset()

    train_args = configure_training_arguments()

    lora_trainer = initialize_trainer(model, tokenizer, train_args, train_data, eval_data)

    # lora_trainer.train()
    # lora_trainer.save_model()
