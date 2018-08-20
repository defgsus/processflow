import sys


class CodeRenderer:

    def __init__(self, process_description):
        self.pd = process_description

    def render(self, fp=None):
        fp = fp or sys.stdout
        self.render_variables(fp)
        self.render_state_functions(fp)
        self.render_transition_functions(fp)

    def render_variables(self, fp=None):
        fp = fp or sys.stdout

        fp.write("""
TRANSITIONS = %(transitions)s
\n""" % {
            "transitions": repr(self.pd.transition_dict)
        })

    def render_state_functions(self, fp=None):
        fp = fp or sys.stdout

        functions = []

        for state in self.pd._states.values():
            code = 'def %s(context):\n    """\n%s\n    """\n' % (
                state.function_name,
                "\n".join("    %s" % line for line in state.python_doc.split("\n")),
            )
            if not state.outputs:
                code += "    pass\n"
            else:
                returns = []
                for other_state_name in sorted(state.outputs):
                    returns.append("    return context.state.%s\n" % (
                        other_state_name,
                    ))
                if len(returns) == 1:
                    code += returns[0]
                elif len(returns) >= 2:
                    for i, line in enumerate(returns):
                        if i == 0:
                            code += "    if 1:\n"
                        elif i == len(returns)-1:
                            code += "    else:\n"
                        else:
                            code += "    elif %s:\n" % (i+1)
                        code += "    " + line
            functions.append(code)

        fp.write("\n\n# STATES #\n\n")
        fp.write("\n\n".join(sorted(functions)))

    def render_transition_functions(self, fp=None):
        fp = fp or sys.stdout

        functions = []
        for state_name, other_state_name in self.pd._transitions:
            state = self.pd.get_state(state_name)
            trans = self.pd.get_transition(state_name, other_state_name)
            code = 'def %s(context):\n    """\n%s\n    """\n    pass\n' % (
                trans.function_name,
                "\n".join("    %s" % line for line in trans.python_doc.split("\n")),
            )
            functions.append(code)

        fp.write("\n\n# TRANSITIONS #\n\n")
        fp.write("\n\n".join(sorted(functions)))