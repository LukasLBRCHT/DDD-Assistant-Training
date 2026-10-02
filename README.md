# Research: Adaptation of a Large Language Model for domain modeling with Bounded Contexts
___
___

## Introduction
A thorough requirements analysis forms the basis for a precise application of functional requirements. 
**Domain-Driven-Design** is an established method in this regard. DDD suggests designing a **domain model** that
precisely captures real world relations and that is supposed to be utilized in all phases of development
to ensure compliance with domain structures. **Bounded Contexts** are used to subdivide the model and to 
ensure each object is modeled correctly.

To make DDD more accessible and provide a possibility to facilitate the domain modeling process, I have 
devised to assess the use of a **Large Language Model** via **local Fine-Tuning** for this purpose. The task of the LLM is to create
domain models and divide them into subdomains. One central requirement is the identification of duplicate 
objects across subdomains that therefore need to be addressed in Bounded Contexts.

___

## Setup 

### Prerequisites
- Conda/Miniconda installed
- CUDA-capable GPU (tested on RTX 3060, 12GB VRAM)
  - CUDA UMD Version: 13.3
- Python 3.11.14 (as specified in `unsloth-env.yml`)


### 1. Clone and set up environment
```console
conda env create -f unsloth-env.yml
conda activate unsloth_env
```

### 2. Download the base model
Download [Qwen2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), set target directory to `<project-directory-root>/models/qwen2.5-3b`

### 3. Run training
```console
cd src/training
python trainer.py
```
Training takes approximately 1.5 h on the tested hardware. Checkpoints are saved to `/adapters`.
___


## Fine-Tuning Specification
To account for limited hardware, a parameter-efficient fine-tuninng was conducted.
By utilizing Low-Rank Adaptation the number of trainable parameters was reduced.
Additionally, the application of the **unsloth**-framework lowered VRAM requirements.

### Hyperparameters

| Hyperparameter       | Value              |
|----------------------|--------------------|
| trainable parameters | 59,867,136 (1.90%) |
| number of samples    | 400                |
| precision            | bf16               |
| total steps          | 480                |
| Learning-Rate        | 2e-4               |
| LoRA-Rank            | 32                 |
| LoRA-Alpha           | 64                 |


### Training data acquisition
Most of the domain information the training data was based on was generated with the help of generative AI.
The domain objects as well as the other concepts were modeled manually. `/res/task_data` contains the data 
for each modeling step. `/res/clean_data` contains ready-for-training
samples in the form of example conversations, which contain the task data.

___


## Evaluation

The base model and the fine-tuned model were compared by manually assessing the output quality according 
to DDD-standards.
The model was given unseen data and asked to create domain models with bounded contexts. 
The results were then judged by...
- Recall: How many of the expected objects were generated?
- Precision: How many of the generated objects adhere to DDD principles?
- Unification (for Bounded Contexts): How many duplicate objects were recognized and taken care of?


### Results
- Recall: fine-tuned model outperformed base model
by 14% for objects and 37% for associations between objects
- Precision: increased by ~30% for both objects (80%) and associations (59%)
- Unification: fine-tuned model recognizes ~2.35 times as many duplicates as before (26% to 61% increase)
  - after fine-tuning the model handles ~50% of duplicate objects in bounded contexts, a 10x increase 
to base model performance (~5%)

### Research Limitations
The validity of the research results is limited due the manual, subjective evaluation.
All outputs were judged based on personal understanding of DDD principles.
As an outlook, to really assess model performance, it would have to be tested and applied in real
world problems and domains and reviewed by respective domain experts.



