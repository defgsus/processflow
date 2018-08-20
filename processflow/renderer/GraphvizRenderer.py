import sys


class GraphvizRenderer:

    def __init__(self, process_descriptor):
        self.pd = process_descriptor

    def run_graphviz(self, filename, format):
        import subprocess, tempfile, os, uuid
        dot_filename = os.path.join(tempfile.gettempdir(), "%s.dot" % uuid.uuid4())
        with open(dot_filename, "wt") as fp:
            self.render(fp)
        subprocess.call(["dot", "-T%s" % format.lower(), dot_filename, "-o%s" % filename])
        os.remove(dot_filename)

    def render(self, fp=None):
        fp = fp or sys.stdout

        fp.write("digraph {\n")
        fp.write("\tstartType=regular;\n")

        self.render_graph(self.pd, fp=fp)

        fp.write("}\n")

    def render_graph(self, pd, fp=None):
        fp = fp or sys.stdout

        for state in sorted(pd.states(), key=lambda s: s.name):

            hue = round(((sum(ord(s) for s in state.name) % 13) / 13) % 1., 2)
            sat = 0.2

            attrs = {
                "color": '"%s %s, .9"' % (hue, sat),
                "style": "filled",
                "shape": "ellipse",
            }
            if state.is_user:
                attrs["shape"] = "rect"

            fp.write("\t%s [%s]\n" % (
                self.get_graph_id(state.name),
                ", ".join("%s=%s" % (key, attrs[key]) for key in attrs),
            ))

        for transition in sorted(pd.transitions(), key=lambda t: str(t)):
            attrs = {
                "color": "black",
            }
            label = ""
            if transition.doc:
                label = "%s" % transition.doc
            if transition.changes:
                label += "\n[%s]" % ", ".join(sorted(transition.changes))
            if label:
                attrs["label"] = '"%s"' % self.auto_break(label, 17)
            fp.write("\t%s -> %s%s\n" % (
                self.get_graph_id(transition.name_from),
                self.get_graph_id(transition.name_to),
                " [%s]" % ", ".join("%s=%s" % (key, attrs[key]) for key in attrs) if attrs else "",
            ))

    def get_graph_id(self, name):
        return '"%s"' % name

    @staticmethod
    def auto_break(string, max_length):
        sequence = string.split()
        ret = []
        runlen = 0
        for i, s in enumerate(sequence):
            ret.append(s)
            runlen += len(s)
            if runlen >= max_length or (i+1 < len(sequence) and runlen + len(sequence[i+1]) >= max_length):
                ret[-1] += "\n"
                runlen = 0
                continue
        return " ".join(ret)
