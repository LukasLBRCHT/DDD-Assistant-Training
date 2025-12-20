from unsloth import FastLanguageModel
from Config import Config as Config
import time
import torch
from data_handling.data_preprocessor import DataPreprocessor
from util.llm_loading import load_model_lora
import warnings
from trl import SFTTrainer, SFTConfig

from data_handling.metadata_extraction import Metadata
import os

os.environ["UNSLOTH_VLLM_STANDBY"] = "1"  # [NEW] Extra 30% context lengths!

def get_training_model(model_dir=Config.MODEL_3B_DIR):
    max_seq_length = 4096
    lora_rank = 8

    model, tokenizer = load_model_lora(model_dir, max_seq_length, lora_rank)

    model = FastLanguageModel.get_peft_model(
        model,
        r=lora_rank,  # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],  # Remove QKVO if out of memory
        lora_alpha=lora_rank,
        use_gradient_checkpointing="unsloth",  # Enable long context finetuning
        random_state=3407,
    )

    return model, tokenizer


def configure_training_arguments():
    output_dir = f'../../adapters/lora-ddd-agent-training-{str(int(time.time()))}'

    lora_training_args = SFTConfig(
        output_dir=output_dir,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=5,
        #num_train_epochs=2,
        learning_rate=2e-4,
        max_steps=10,
        warmup_steps=1,
        logging_steps=1,
        save_steps=5,
        save_total_limit=2,
        fp16=False,
        bf16=True,
        #gradient_checkpointing=False,  # important for Unsloth stability
        optim="adamw_torch",
        report_to="none",
        packing=False,  # use packing only if data is short
    )

    return lora_training_args


def initialize_trainer(lora_model, tokenizer, train_args, train_data):
    lora_trainer = SFTTrainer(
        model=lora_model,
        processing_class=tokenizer,
        train_dataset=train_data,
        eval_dataset=eval_data,
        args=train_args,
    )

    return lora_trainer


if __name__ == "__main__":
    warnings.filterwarnings("ignore", message=".*active_adapter.*")
    warnings.filterwarnings("ignore", message=".*UserWarning: Could not find a config file.*")

    # load model
    model, tokenizer = get_training_model()

    preprocessor = DataPreprocessor(tokenizer, max_length=4096)

    md = Metadata()
    train_split, test_split = md.get_custom_split()
    train_data, eval_data = preprocessor.load_data(train_split, test_split, 4)

    train_args = configure_training_arguments()
    lora_trainer = initialize_trainer(model, tokenizer, train_args, train_data)

    print("Starting training...")
    lora_trainer.train()
    print("Training done!")
    test_results = lora_trainer.evaluate(
        eval_dataset=eval_data)  # provisorisch, Test-Daten sollten eigentlich separat sein
    # lora_trainer.save_model()
    print(f"Results:\n{test_results}")
