"""
The purpose of a Conversation_History instance is to store a set of previous messages.
"""


class Conversation_History:

    def __init__(self):
        self.first_system_prompt = None
        self.last_system_prompt = None
        self.conversation_messages = []


    def set_first_system_prompt(self, prompt):
        self.first_system_prompt = prompt

    def set_last_system_prompt(self, prompt):
        self.last_system_prompt = prompt

    def add_conversation_prompt(self, prompt, role):

        if role == "system":
            if not self.first_system_prompt:
                self.first_system_prompt = prompt
            else:
                self.last_system_prompt = prompt
        else:
            message = {"role": role, "content": prompt}
            self.conversation_messages.append(message)
            if len(self.conversation_messages) > 6:
                self.conversation_messages.pop(0)

    def is_empty(self):
        return len(self.compress()) == 0

    """
    Summarize all the messages into one list and return it.
    """

    def compress(self, tokenizer=None):
        history = []
        if self.first_system_prompt: history.append(self.first_system_prompt)
        if self.last_system_prompt: history.append(self.last_system_prompt)
        if self.conversation_messages: history.append(self.conversation_messages)
        text = history
        if tokenizer:
            text = tokenizer.apply_chat_template(
                history,
                tokenize=False,
            )
        return text
