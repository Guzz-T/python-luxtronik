import inspect
import luxtronik.datatypes as datatypes

# A dictionary of sets containing data types.
# Entries within the same set are functionally equivalent to the user
# and can be substituted transparently. For example, when the scaling of raw values changes.
# Because they are interchangeable, duplicate names are permitted within the same set.
class TypesOfSameKind:

    class_dict = {}
    for name, cls in inspect.getmembers(datatypes, inspect.isclass):
        if cls.__module__ == datatypes.__name__:
            if cls.datatype_class is not None and cls.datatype_unit is not None:
                unit_dict = class_dict.setdefault(cls.datatype_class, {})
                type_set = unit_dict.setdefault(cls.datatype_unit, set())
                type_set.add(cls)

    @classmethod
    def match(cls, a, b):
        unit_dict = cls.class_dict.get(a.datatype_class, None)
        if unit_dict is None:
            return False
        type_set = unit_dict.get(a.datatype_unit, None)
        if type_set is None:
            return
        return b in type_set
