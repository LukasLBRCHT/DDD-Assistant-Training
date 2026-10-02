from unsloth import FastLanguageModel, get_chat_template
from unsloth.chat_templates import train_on_responses_only
from Config import Config as Config
from data_handling.data_preprocessor import DataPreprocessor
from util.llm_util import load_model_lora
import warnings
from trl import SFTTrainer, SFTConfig

from data_handling.metadata_extraction import Metadata
import os

os.environ["UNSLOTH_VLLM_STANDBY"] = "1"  # increase context length

"""
Loads model and tokenizer from directorey location.
"""
def get_training_model(model_dir=Config.MODEL_3B_DIR):
    max_seq_length = 4096
    lora_rank = 32

    model, tokenizer = load_model_lora(model_dir, max_seq_length, lora_rank)

    tokenizer = get_chat_template(
        tokenizer,
        chat_template="qwen-2.5",
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=lora_rank,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],  # Remove QKVO if out of memory
        lora_alpha=lora_rank*2,
        bias="none",
        use_gradient_checkpointing="unsloth",  # Enable long context finetuning
        random_state=3407,
    )

    return model, tokenizer

"""
Set configuration parameters for lora trainer.
"""
def configure_training_arguments():

    run_name = input("Enter run-name:")

    output_dir = f'../../adapters/{run_name}'

    lora_training_args = SFTConfig(
        output_dir=output_dir,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=1,
        num_train_epochs=3,

        learning_rate=2e-4,
        warmup_ratio=0.05,

        logging_strategy="steps",
        logging_steps=1,
        logging_first_step=True,
        logging_dir="../../res/training_logs",
        report_to="tensorboard",
        log_level="info",

        save_strategy="epoch",
        save_total_limit=3,

        weight_decay=0.01,

        dataset_num_proc=1,

        eval_strategy="steps",
        eval_steps=20,

        fp16=False,
        bf16=True,

        lr_scheduler_type="cosine",
        optim="adamw_torch",

        max_grad_norm=1.0,

        packing=False,
        dataset_text_field="messages"
    )

    return lora_training_args


def initialize_trainer(lora_model, tokenizer, train_args, train_data, eval_data):
    lora_trainer = SFTTrainer(
        model=lora_model,
        processing_class=tokenizer,
        train_dataset=train_data,
        eval_dataset=eval_data,
        args=train_args
    )

    lora_trainer = train_on_responses_only(
        lora_trainer,
        instruction_part="<|im_start|>user\n",
        response_part="<|im_start|>assistant\n",
        num_proc=1
    )

    return lora_trainer

"""
Central training script
"""
if __name__ == "__main__":
    warnings.filterwarnings("ignore", message=".*active_adapter.*")
    warnings.filterwarnings("ignore", message=".*UserWarning: Could not find a config file.*")

    # load model
    model, tokenizer = load_model_lora(Config.MODEL_3B_DIR, 4096, 32)

    preprocessor = DataPreprocessor(tokenizer, max_length=4096)

    md = Metadata()
    train_split, test_split = md.get_custom_split()
    train_data, eval_data, eval_data_list = preprocessor.load_data(train_split, test_split)

    train_args = configure_training_arguments()
    lora_trainer = initialize_trainer(model, tokenizer, train_args, train_data, eval_data)

    print("Starting training...")
    metrics_before = lora_trainer.evaluate()  # get metrics at step 0 (before training)
    print(f"first eval: {metrics_before}")
    lora_trainer.train()
    print("Training done!")

    lora_trainer.save_model()

