# Research: Adaptation of a Large Language Model for domain modeling with Bounded Contexts
___

Setup

## Introduction
A thorough requirements analysis forms the basis for a precise application of technical solutions. 
**Domain-Driven Design** is an established method in this regard. DDD suggests designing a **domain model** that
precisely captures real-world relations and that is intended to be used in all phases of development
to keep the implementation consistent with the domain. **Bounded Contexts** are used to subdivide the model and to 
ensure each object is modeled correctly.

To make DDD more accessible and facilitate the domain modeling process, I set out 
to assess the use of a **Large Language Model** via **local Fine-Tuning** for this purpose. This repository
contains the training code and training data for that process. The task of the LLM is to create
domain models and divide them into subdomains. One central requirement is the identification of duplicate 
objects across subdomains that therefore need to be addressed through Bounded Contexts. 

### What is the model trained to do specifically?
1. Process domain information and identify **Domain Objects**
2. Connect Domain Objects using **Associations**
3. Divide the Domain Objects into **Subdomains**, based on the Domain Objects and Associations
4. Identify **Bounded Contexts**
> Subdomains as well as Bounded Contexts are represented as lists of Domain Objects


## Setup 

### Prerequisites
- Conda/Miniconda installed
- CUDA-capable GPU (tested on RTX 3060, 12GB VRAM)
  - CUDA Version: 13.3
- Python 3.11.14 (as specified in `unsloth-env.yml`)


### 1. Clone and set up environment
```console
conda env create -f unsloth-env.yml
conda activate unsloth_env
```

### 2. Download the base model
Download [Qwen2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct), and place in following directory: `<project-directory-root>/models/qwen2.5-3b`

Expected contents: `config.json`, `tokenizer.json`, model weights (`.safetensors`), etc..

> Note: automated download wasn't working reliably during development, so this step is manual for now.


### 3. Run training
```console
cd src/training
python trainer.py
```
Training takes approximately 1.5 h on the tested hardware. Checkpoints are saved to `/adapters`.



## Fine-Tuning Specification
To account for limited hardware, a parameter-efficient fine-tuning was conducted.
By utilizing Low-Rank Adaptation (LoRA), the number of trainable parameters was reduced.
Additionally, using the **unsloth** framework lowered VRAM requirements.

### Hyperparameters

| Hyperparameter       | Value              |
|----------------------|--------------------|
| Trainable Parameters | 59,867,136 (1.90%) |
| Number of Samples    | 400                |
| Precision            | bf16               |
| Total Steps          | 480                |
| Learning Rate        | 2e-4               |
| LoRA-Rank            | 32                 |
| LoRA-Alpha           | 64                 |


### Training data acquisition
Most of the domain information that formed the basis for the training data was generated with the help of generative AI.
The domain objects as well as the other concepts were modeled manually. `/res/task_data` contains the data 
for each modeling step. `/res/clean_data` contains ready-for-training
samples in the form of example conversations, which contain the task data.

### Training data structure
Each example conversation that is used to train the model follows the same structure. On the user turn,
the LLM is tasked with extract/model certain information. The model should then return the
requested data on the assistant turn. The next user turn presents results acquired by the model in the
previous step and asks it to further process them. This cycle repeats until the model has constructed
Bounded Contexts. Due to context window length, such a conversation is divided into the four steps mentioned in the introduction (also meaning four 
training samples).
 
In `/res/clean_data` you can see one directory per modeling step, each containing the respective conversation parts.




## Evaluation

The base model and the fine-tuned model were compared by manually assessing the output quality according 
to DDD standards.
The model was given unseen data and asked to create domain models with bounded contexts. 
The results were then judged according to the following metrics:
- Recall: How many of the expected objects were generated?
- Precision: How many of the generated objects adhere to DDD principles?
- Unification (for Bounded Contexts): How many duplicate objects were recognized and resolved?


### Results
- Recall: fine-tuned model outperformed base model
by 14 percentage points for objects and 37 percentage points for associations between objects
- Precision: increased by ~30 percentage points for both objects (reaching 80%) and associations (reaching 59%)
- Unification: fine-tuned model recognizes ~2.35 times as many duplicates as before (26% to 61% increase)
  - after fine-tuning the model handles ~50% of duplicate objects in bounded contexts, a 10x increase 
to base model performance (~5%)

### Research Limitations
The validity of the research results is limited due to the manual, subjective evaluation.
All outputs were judged based on personal understanding of DDD principles.
As an outlook, to really assess model performance, it would have to be tested and applied in real-world 
problems and domains and reviewed by respective domain experts.



