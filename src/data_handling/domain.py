
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
