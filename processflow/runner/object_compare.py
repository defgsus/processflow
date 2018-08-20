try:
    from django.db.models.manager import Manager
    USE_DJANGO = True
except ImportError:
    pass


def deep_copy(object):
    """
    Make a deep copy of any value/object, returning nested dicts
    :param object: Any type of object,
           especially: single value, tuples/lists, dicts, classes, Django model instances
    :return: single value or dict of values/dicts
    """
    from .ProcessRunnerContext import _FunctionContext

    # return single value
    if object is None:
        return None
    if isinstance(object, (int, str, float, bool)):
        return object

    # return list of deep copies
    if isinstance(object, list):
        return [deep_copy(o) for o in object]
    if isinstance(object, tuple):
        return tuple(deep_copy(o) for o in object)
    if isinstance(object, set):
        return set(deep_copy(o) for o in object)

    # return dict of deep copies

    if isinstance(object, dict):
        keys = object.keys()
        _get = lambda k: object[k]
    elif isinstance(object, _FunctionContext):
        keys = list(dir(object))
        keys.remove("state")
        _get = lambda k: getattr(object, k)
    else:
        keys = dir(object)
        _get = lambda k: getattr(object, k)

    ret = dict()

    for key in keys:
        try:
            if key.startswith("_"):
                continue
        except AttributeError:
            pass
        try:
            value = _get(key)
        except AttributeError:
            continue

        if USE_DJANGO:
            if isinstance(value, Manager):
                value = set(v[0] for v in value.values_list("pk"))

        if callable(value):
            continue

        ret[key] = deep_copy(value)

    return ret


def get_difference(A, B):
    """
    Compare two dicts and return the differences per key in the hierarchy.
    e.g. given input:
        A = {"main": {"sub: 1}}
        B = {"main": {"sub: 2}, "foo": "bar"}
    the result would be
        {"main.sub": [1, 2], "foo": [None, "bar"]}

    :param A: dict
    :param B: dict
    :return: dict
    """
    diff = dict()

    def _compare(A, B, key, prefix):
        prefix_key = ".".join((prefix, key)) if prefix else key
        if key not in A:
            diff[prefix_key] = [None, B[key]]
            return
        if key not in B:
            diff[prefix_key] = [A[key], None]
            return
        a, b = A[key], B[key]
        if a != b:
            if type(a) == type(b):
                if isinstance(a, dict):
                    for key in set(a.keys()) | set(b.keys()):
                        _compare(a, b, key, prefix_key)
                    return
            diff[prefix_key] = [a, b]

    for key in set(A.keys()) | set(B.keys()):
        _compare(A, B, key, "")

    return diff


def subtract_valid_changes(diff, valid_changes):
    """
    Remove any valid changes from diff (as gotten from get_difference())
    `valid_changes` is a list of strings with format like:
        'variable', 'object.*', 'object.variable', 'object.*.sub.another'
    :param diff: dict with changes from get_difference()
    :param valid_changes: list of str,
    :return: new dict, containing all changes in `diff` that are not valid according to `valid_changes`
    """
    def _convert(key):
        seq = tuple(key.split("."))
        # reduce trailing .*.* to .*
        while len(seq) > 1 and seq[-2:] == ("*", "*"):
            seq = seq[:-1]
        return seq
    valid = set(_convert(c) for c in valid_changes)

    ret = dict()
    for key in diff:
        sequence = key.split(".")
        if not sequence:
            raise ValueError("Empty key in diff")

        match = False

        sub_valid = valid
        for sub_key in sequence:

            if ("*",) in sub_valid or (sub_key,) in sub_valid or (sub_key, "*") in sub_valid:
                match = True
                break

            sub_valid = set(c[1:] for c in sub_valid if c[0] == sub_key or c[0] == "*")

        if match:
            continue

        ret[key] = diff[key]
    return ret


if __name__ == "__main__":

    class SomeClass:
        def __init__(self, sub=True):
            self.field1 = "So"
            self.field2 = "Anders"
            if sub:
                self.field3 = SomeClass(sub=False)

    print(deep_copy(1))
    print(deep_copy([1, 2, 3]))
    print(deep_copy({"bla": "bla", "blub": {"bla": "blub"}}))
    print(deep_copy(SomeClass()))


