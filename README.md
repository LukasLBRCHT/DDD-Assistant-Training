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
devised to assess the use of a **Large Language Model** via **Fine-Tuning** for this purpose. The task of the LLM is to create
domain models and divide them into subdomains. One central requirement is the identification of duplicate 
objects across subdomains that therefore need to be addressed in Bounded Contexts.

___
-
## Set-Up
hier vll. tech-stack... Installation

___
-

## Fine-Tuning Specification
... Hyperparameter, Trainins-Ansatz, Ablauf, was für Daten

___
-

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



