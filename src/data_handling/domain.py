
class Domain_Object:
    object_name = None
    object_attributes = []

    def __init__(self, name):
        self.object_name = name
        self.object_attributes = []

    def add_attribute(self, attr):
        self.object_attributes.append(attr)

    def set_name(self, name):
        self.object_name = name

class Bounded_Context:

    def __init__(self):
        self.meanings = dict()

    def add_renaming(self, former, current):
        self.meanings[former] = current

    def compress(self):

        if not self.meanings:
            return ""

        name_changes = ""
        for original in self.meanings.keys():
            change = f"\"{original} -> {self.meanings[original]}\","
            name_changes += change

        name_changes = name_changes.removesuffix(",")

        return name_changes
