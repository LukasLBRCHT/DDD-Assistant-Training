from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, \
    DataCollatorForLanguageModeling
import torch
from Config import Config as Config
from peft import LoraConfig, TaskType
import time
from data_handling.data_preprocessor import DataPreprocessor
from data_handling.metadata_extraction import Metadata


def load_lora_model():

    model = AutoModelForCausalLM.from_pretrained(  # loading the model
        Config.MODEL_3B_DIR,
        device_map="auto",
        torch_dtype=torch.float16,
    )

    peft_config = LoraConfig(task_type=TaskType.CAUSAL_LM, inference_mode=False, r=32, lora_alpha=16, lora_dropout=0.1,
                             target_modules=[
                                 "q_proj", "k_proj", "v_proj", "o_proj",
                                 "gate_proj"]
                             )

    # target_modules = [
    #     "q_proj", "k_proj", "v_proj", "o_proj",
    #     "gate_proj", "up_proj", "down_proj"]

    model.add_adapter(peft_config)
    # applied LoRA config to the model
    tokenizer = AutoTokenizer.from_pretrained(  # loading the tokenizer of the model
        Config.MODEL_3B_DIR
    )

    return model, tokenizer


def configure_training_arguments():
    output_dir = f'../../adapters/lora-ddd-agent-training-{str(int(time.time()))}'

    # TODO: hyperparameter bestimmen
    lora_training_args = TrainingArguments(
        output_dir=output_dir,
        warmup_steps=0,  # 2
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,  # 50
        max_steps=5,
        learning_rate=2e-4,
        optim="paged_adamw_8bit",
        logging_steps=1,  # 25
        logging_dir="./logs",
        save_strategy="steps",
        save_steps=1,  # 25
        eval_strategy="no", # steps
        #eval_steps=1,  # 25
        do_eval=False,
        gradient_checkpointing=False, # True
        report_to="none",
        overwrite_output_dir=False,
        group_by_length=True,
        label_names=["labels"],
        fp16=True
    )

    return lora_training_args


def initialize_trainer(lora_model, tokenizer, train_args, train_data, eval_data):
    lora_model.config.use_cache = False

    lora_trainer = Trainer(
        model=lora_model,
        train_dataset=train_data,
        eval_dataset=eval_data,
        args=train_args,
        data_collator=DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
            pad_to_multiple_of=8
        ),
    )

    return lora_trainer


if __name__ == "__main__":
    # load model
    model, tokenizer = load_lora_model()

    preprocessor = DataPreprocessor(tokenizer)

    md = Metadata()
    order = md.get_custom_order()
    train_data, eval_data = preprocessor.load_data(order)

    train_args = configure_training_arguments()
    lora_trainer = initialize_trainer(model, tokenizer, train_args, train_data, eval_data)

    print("Starting training...")
    lora_trainer.train()
    print("Training done!")
    test_results = lora_trainer.evaluate(train_data)  # provisorisch, Test-Daten sollten eigentlich separat sein
    # lora_trainer.save_model()
    print(f"Results:\n{test_results}")
