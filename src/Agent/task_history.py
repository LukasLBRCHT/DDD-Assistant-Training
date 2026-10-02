from util.json_parser import parse_json

"""
This class stores the state of the subtasks during the process of domain modeling.
"""


class Task_History():

    def __init__(self):
        self.tasks = dict()

    """
    The task history is updated by analyzing an input-string 'entry', which is supposed to be an llm-answer
    """
    def update(self, entry):

        json_matches = parse_json(entry)  # retrieve information about subtask contained in llm answer
        if len(json_matches) == 0:
            return

        for match in json_matches:
            key = match[0]
            value = match[1]

            self.tasks[key] = value

    def compress(self):

        if len(self.tasks) == 0:
            return "No subtask progress yet"

        return str(self.tasks)
