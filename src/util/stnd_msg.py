# Todo vernünftig machen
sys_msg = """Your are a helpful assistant."""
user_initial_req_stories = """Help me extract entities, value objects and associations from these user stories: 
```json\n{}\n```\n"""
assistant_stories_resp = """Here are the domain objects: {}"""
user_subdomains_req = """Now group the domain objects by subdomains. These were the domain objects: {}"""
assistant_subdomains_resp = """Here are the subdomains: {}"""
user_bounded_context_req = """Now identify the bounded contexts. This is the current model state: {}"""
assistant_bounded_context_resp = """Here are the bounded contexts: {}"""
