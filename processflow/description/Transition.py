
class Transition:
    def __init__(self, pd, name_from, name_to, options=None):
        self.pd = pd
        self.name_from = name_from
        self.name_to = name_to
        self.options = options or dict()
        if "name" in self.options:
            self.name = self.options["name"]
        else:
            self.name = "%s->%s" % (self.name_from, self.name_to)
        self._changes = None
        self._inputs = None

    def __str__(self):
        return self.name

    @property
    def function_name(self):
        if "name" in self.options:
            return "transition_%s" % self.options["name"]
        return "transition_from_%s_to_%s" % (self.name_from, self.name_to)

    @property
    def state_from(self):
        return self.pd.get_state(self.name_from)

    @property
    def state_to(self):
        return self.pd.get_state(self.name_to)

    @property
    def changes(self):
        if self._changes is None:
            self._changes = list(self.options.get("change", []))
            state = self.state_to
            if state and state != self.state_from:
                for i in state.inputs:
                    contained = False
                    for j in self._changes:
                        if j.startswith(i):
                            contained = True
                            break
                    if not contained:
                        self._changes.append(i)
        return self._changes

    @property
    def inputs(self):
        if self._inputs is None:
            self._inputs = list(self.options.get("in", []))
            state = self.state_from
            if state:
                for i in state.inputs:
                    if i not in self._inputs:
                        self._inputs.append(i)
        return self._inputs

    @property
    def doc(self):
        return self.options.get("doc", "")

    @property
    def python_doc(self):
        return "%sinputs: %s\nchanges: %s" % (
            "%s\n" % self.doc if self.doc else "",
            ", ".join(self.inputs),
            ", ".join(self.changes),
        )
