# Todo vernünftig machen

def sys_msg():
    return """You are a domain driven design (DDD) expert.
Your task is to help the user step by step with creating domain models.

### Here is the explanation of the workflow:
1. The user will provide domain information.
2. Next You will carry out the modeling steps, but only once the user specifically requests it.

#### Modeling steps:
1. You will extract domain objects and associations. 
2. You will group the objects by subdomains.
3. In the last step you will define bounded contexts. """


def user_turn_1():
    return """Help me extract domain objects. Below I will provide domain information. 

#### Data:
This domain information covers the important domain events:
```json
{}
```

#### Task:
- Identify the objects within this information. 
- Summarize it's meaning in a short description. 
- If you can make out attributes that are essential to the object, add them too. 
- Return the objects in json format. Here is an example for structuring the data:
```json
{{
  "domain objects": [
    {{
      "name": "...",
      "description": "..."
    }}
  ]
}}
```"""


def llm_turn_1():
    return """Here are the domain objects:
```json
{}
```"""


def user_turn_2():
    return """Help me find the associations.  
{}
#### Task:
- Draw connections between objects that have an association. 
- Name each object and add a description that captures the meaning of the association.
- Return the associations in json format. Here is an example for structuring the data:
```json
{{
  "associations": [
    {{
      "from": "...",
      "to": "...",
      "description": "..."
    }}
  ]
}}
```"""


def llm_turn_2():
    return """Here are the associations:
```json
{}
```"""


def user_turn_3():
    return """Help me define subdomains. Below I will provide the current state of the domain. 

#### Data:
These are the extracted domain objects and their associations:
```json
{}
```

#### Task:
- Group these objects by domain concerns. 
- Find a name for the subdomain then list the objects that belong to it. 
- Return the subdomains in json format. Here is an example for structuring the data:
```json
{{
  "subdomains": {{
    "...": {{
      "objects": [
        "...",
        "...",
        "..."
      ]
    }}
  }}
}}
```"""


def llm_turn_3():
    return """Here are the subdomains:
```json
{}
```"""

def user_turn_4():
    return """Help me define bounded contexts. Below I will provide domain information. 

#### Data:
These are the extracted objects and the subdomain grouping:
```json
{}
```

#### Task:
- Assign the subdomains to bounded contexts. 
- Name the subdomain the bounded context might be derived from, it might also be multiple.
- Identify cases, where an object does not have a unified meaning across all bounded contexts and suggest a name change.
- Return the bounded contexts in json format. Here is an example for structuring the data:
```json
{{
  "bounded contexts": {{
    "...": {{
      "derived from": "...",
      "objects": [
        "...",
        "..."
      ],
      "name changes": []
    }},
    "...": {{
      "derived from": "...",
      "objects": [
        "...",
        "...",
        "..."
      ],
      "name changes": [
        "... -> ..."
      ]
    }}
  }}
}}
```"""


def llm_turn_4():
    return """Here are the bounded contexts: 
```json
{}
```"""
