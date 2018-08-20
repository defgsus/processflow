import sys

from .State import State
from .Transition import Transition


class ProcessDescription(object):

    def __init__(self, transitions=None):
        self._transition_dict = None
        self._states = dict()
        self._transitions = dict()
        if transitions:
            self.set_transitions(transitions)

    def is_ready(self):
        return bool(self._states)

    @property
    def transition_dict(self):
        return self._transition_dict

    def states(self):
        return list(self._states.values())

    def transitions(self):
        return list(self._transitions.values())

    def has_state(self, name):
        return name in self._states

    def has_transition(self, name_from, name_to):
        return (name_from, name_to) in self._transitions

    def get_state(self, name):
        return self._states[name]

    def get_transition(self, name_from, name_to):
        return self._transitions[(name_from, name_to)]

    def set_transitions(self, transitions):
        self._transition_dict = transitions
        self._states = dict()
        self._transitions = dict()
        options = {s[1:]: self._transition_dict[s] for s in self._transition_dict if s.startswith("$")}
        for state_name in sorted(self._transition_dict):
            if state_name.startswith("$"):
                continue

            def _add_state(name):
                self.verify_state_name(name)
                if name not in self._states:
                    s = State(self, name)
                    for i in s.inputs:
                        if i.startswith("transition") or i.startswith("state"):
                            raise ValueError("input names must not start with 'state' or 'transition', "
                                             "in state %s" % name)
                    for key in options:
                        if key in ("in", "change"):
                            s.options[key] = options[key]
                    self._states[name] = s

            _add_state(state_name)
            state = self._states[state_name]

            trans = transitions[state_name]
            trans_options = {s[1:]: trans[s] for s in trans if s.startswith("$")}
            trans = {s: trans[s] for s in trans if not s.startswith("$")}
            for key in trans_options:
                if key in state.options:
                    A, B = trans_options[key], state.options[key]
                    if A != B:
                        if all(isinstance(x, (list, tuple)) for x in (A, B)):
                            for x in B:
                                if x not in A:
                                    A.append(x)

                        else:
                            raise ValueError("option %s:%s redefined as %s for state %s" % (
                                key, state.options[key], options[key], state_name
                            ))
                state.options[key] = trans_options[key]

            for other_state_name in sorted(trans):
                _add_state(other_state_name)

                state.outputs.add(other_state_name)
                key = (state_name, other_state_name)
                if key in self._transitions:
                    pass
                else:
                    transition = trans[other_state_name]
                    options = {k[1:]: transition[k] for k in transition if k.startswith("$")}
                    if options.get("name"):
                        self.verify_state_name(options["name"])
                    t = Transition(
                        self, state_name, other_state_name,
                        options=options,
                    )
                    for exist in self._transitions.values():
                        if t.name == exist.name:
                            raise ValueError("Duplicate name '%s' given to transition '%s->%s'" % (
                                t.name, state_name, other_state_name,
                            ))
                    self._transitions[key] = t

    def verify_state_name(self, name):
        if not isinstance(name, str):
            raise ValueError("Name is no str, it is %s" % type(name))
        if not name:
            raise ValueError("No state name given")
        if name.startswith("transition_") or name.startswith("state_"):
            raise ValueError("state names must not start with 'state_' or 'transition_'")
        if name[0].isdigit():
            raise ValueError("state names must not start with a digit")
        if name[0] == "_":
            raise ValueError("state names must not start with an underscore")
        for c in name:
            if not (c.isalnum() or c == "_"):
                raise ValueError("state names must only contain letters, digits and underscore")

    def dump(self, fp=None):
        fp = fp or sys.stdout

        fp.write("States: %s\n" % ", ".join(sorted(self._states)))
        fp.write("Trans : %s\n" % ", ".join("->".join(t) for t in sorted(self._transitions)))

    def _render(self, renderer, fp):
        if isinstance(fp, str):
            with open(fp, "w") as f:
                renderer.render(f)
        else:
            renderer.render(fp)

    def render_code(self, fp=None):
        from ..renderer import CodeRenderer
        self._render(CodeRenderer(self), fp)

    def render_graphviz(self, fp=None, format="png"):
        from ..renderer import GraphvizRenderer
        renderer = GraphvizRenderer(self)
        if format in ("dot",):
            self._render(renderer, fp)
        else:
            if not isinstance(fp, str):
                raise ValueError("For image files, 'fp' must be a filename")
            renderer.run_graphviz(fp, format)