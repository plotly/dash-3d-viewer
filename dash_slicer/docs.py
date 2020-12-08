import os
import inspect

import dash_slicer

HERE = os.path.dirname(os.path.abspath(__file__))


def dedent(text):
    """Dedent a docstring, removing leading whitespace."""
    lines = text.lstrip().splitlines()
    min_indent = 9999
    for i in range(1, len(lines)):
        line1 = lines[i]
        line2 = line1.lstrip()
        if line2:
            indent = len(lines[i]) - len(lines[i].lstrip())
            min_indent = min(min_indent, indent)
    if min_indent > 16:
        min_indent = 0
    for i in range(1, len(lines)):
        lines[i] = lines[i][min_indent:]
    return "\n".join(lines)


def get_reference_docs():
    """Create reference documentation from the source code.
    A bit like Sphinx autodoc, but using Markdown, and more basic.
    Returns a str in Markdown format.

    Note that this function is used to build the Dash Slicer chapter
    in the Dash docs.
    """

    methods = []
    props = []

    sig = str(inspect.signature(dash_slicer.VolumeSlicer.__init__)).replace("self, ", "")
    doc = f"**class `VolumeSlicer{sig}`**"
    doc += "\n\n" + dedent(dash_slicer.VolumeSlicer.__doc__)
    methods.append(doc)

    for name in dir(dash_slicer.VolumeSlicer):
        val = getattr(dash_slicer.VolumeSlicer, name)

        if name.startswith("_") or not hasattr(val, "__doc__"):
            pass
        elif callable(val):
            # Method
            sig = str(inspect.signature(val)).replace("self, ", "")
            doc = f"**method `VolumeSlicer.{name}{sig}`**"
            doc += "\n\n" + dedent(val.__doc__)
            methods.append(doc)
        else:
            # Property
            doc = f"**property `VolumeSlicer.{name}`**"
            try:
                doc += " " + val.fget.__annotations__["return"].__name__
            except (AttributeError, KeyError):
                pass
            doc += ": " + dedent(val.__doc__)
            props.append(doc)

    parts = []
    parts.append("### The VolumeSlicer class")
    parts += methods
    parts += props
    parts.append(dash_slicer.slicer.__doc__)
    return "\n\n".join(parts)


def write_reference_docs():
    """Write the reference docs to the README."""
    header = "## Reference"
    filename = os.path.join(os.path.dirname(HERE), "README.md")
    assert os.path.isfile(filename), "README.md not found"
    with open(filename, "rt", encoding="utf-8") as f:
        text = f.read()
    text, _, _ = text.partition(header)
    text = text.rstrip() + "\n\n\n" + header + "\n\n" + get_reference_docs()
    with open(filename, "wt", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    write_reference_docs()
