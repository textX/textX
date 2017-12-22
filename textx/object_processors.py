class InheritanceProcessor(object):
    def __init__(self,dot_separated_path_to_base_classes, target_attribute_name="_tx_base_entities"):
        self.dot_separated_path_to_base_classes = dot_separated_path_to_base_classes
        self.target_attribute_name = target_attribute_name

    def __call__(self, entitiy):
        from textx.scoping_tools import get_referenced_object_as_list
        base_entities = get_referenced_object_as_list(None, entitiy, self.dot_separated_path_to_base_classes)
        setattr(entitiy, self.target_attribute_name, base_entities)
