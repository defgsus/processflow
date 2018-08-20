
class State:
    def __init__(self, pd, name, options=None):
        self.pd = pd
        self.name = name
        self.options = options or dict()
        self.outputs = set()

    def __str__(self):
        return self.name

    @property
    def function_name(self):
        return "state_%s" % self.name

    @property
    def doc(self):
        return self.options.get("doc", "")

    @property
    def python_doc(self):
        return "%sinputs: %s" % (
            "%s\n" % self.doc if self.doc else "",
            ", ".join(self.inputs),
        )

    @property
    def inputs(self):
        return self.options.get("in", [])

    @property
    def transitions(self):
        ret = []
        for name_from, name_to in self.pd._transitions:
            if name_from == self.name:
                ret.append(self.pd.get_transition(name_from, name_to))
        return ret

    @property
    def is_user(self):
        return self.options.get("user", False)
