# -*- coding: utf-8 -*-
"""
Drives export_components.py without a human at the canvas.

Run by Rhino itself (see generate_docs.sh), NOT by system python:

    "/Applications/Rhino 8.app/Contents/MacOS/Rhinoceros" -nosplash \
        -runscript='-_RunPythonScript "<this file>"'

DIFFERENCE FROM THE EDDY3D ORIGINAL: Eddy3D hosts its export script inside a GhPython
component in Eddy3D/GenerateDocumentation.ghx, so its driver opens that definition and
flips a Boolean Toggle. Mycelium has no such definition and does not need one -- the
exporter only requires *an* active canvas document to place components on, so this driver
creates an empty one and executes the script directly. One less file to keep in sync.

ENGINE GOTCHA (why this file is plain ASCII with a coding header): -_RunPythonScript may host
this with IronPython 2, whose parser rejects any non-ASCII byte unless a PEP-263 coding line is
present -- an em-dash in a COMMENT once produced "SyntaxError: Non-ASCII character '\\xe2'" and the
export silently never started. Keep this file ASCII-only; keep the coding line as a belt.

AS HEADLESS AS RHINO GETS: there is no headless launch mode in Rhino 8 for Mac (no -headless
argument in the binary, no LSBackgroundOnly, and `rhinocode script` only talks to an already
running instance). The Rhino window does open. But the Grasshopper EDITOR is never shown: the
canvas object is created by LoadEditor() and GH_Canvas.GenerateHiResImage paints into an offscreen
bitmap, so the screenshots do not need the editor on screen. What this removes is the HUMAN and
the GH window; a logged-in GUI session must still exist for the canvas control to be creatable.

IMPORT GOTCHA: the plain-Rhino python host references RhinoCommon but NOT Grasshopper, so a bare
`import Grasshopper` fails ("No module named Grasshopper"). Loading the plug-in object first puts
the assembly in the domain; clr.AddReference then makes the import resolve.

API GOTCHA: do NOT use DocumentServer.AddDocument(doc, True) -- its second parameter is by-ref and
the python binding rejects it ("expected StrongBox[bool], got bool"). Assigning canvas.Document is
sufficient and registers the document.

Outcome is written to the file named by MYCELIUM_DOCS_SENTINEL ("0" ok, "1" failed); the wrapper
reads it so a failed export can never look like a success. Progress is appended to
MYCELIUM_DOCS_LOG (default ~/mycelium_docs_export.log) because Rhino's command line is invisible
to the shell that launched it.
"""

import os
import sys
import traceback

import clr
import Rhino

_GH = Rhino.RhinoApp.GetPlugInObject("Grasshopper")
if _GH is None:
    raise RuntimeError("Grasshopper plug-in object not available - is Grasshopper installed?")
clr.AddReference("Grasshopper")
import Grasshopper  # noqa: E402  (must follow AddReference)

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_SCRIPT = os.environ.get(
    "MYCELIUM_EXPORT_SCRIPT", os.path.join(_THIS_DIR, "export_components.py"))
LOG_PATH = os.environ.get(
    "MYCELIUM_DOCS_LOG", os.path.expanduser("~/mycelium_docs_export.log"))


def log(message):
    line = "[docs-export] " + str(message)
    print(line)  # Rhino command line
    try:
        with open(LOG_PATH, "a") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


def load_editor():
    _GH.DisableBanner()
    if not _GH.IsEditorLoaded():
        log("loading Grasshopper editor (canvas object needed; the window is never shown)")
        _GH.LoadEditor()
    canvas = Grasshopper.Instances.ActiveCanvas
    if canvas is None:
        raise RuntimeError(
            "Grasshopper editor loaded but ActiveCanvas is still null - screenshots cannot be "
            "captured. Is this a logged-in GUI session (not ssh)?")
    return canvas


def blank_document(canvas):
    """The exporter places each component on ActiveCanvas.Document; give it an empty one."""
    doc = Grasshopper.Kernel.GH_Document()
    canvas.Document = doc
    doc.Enabled = False  # the exporter manages the solver state itself
    log("created a blank canvas document")
    return doc


def run_export():
    if not os.path.exists(EXPORT_SCRIPT):
        raise IOError("Export script not found: " + EXPORT_SCRIPT)

    log("running " + EXPORT_SCRIPT)
    namespace = {
        "__file__": EXPORT_SCRIPT,
        "__name__": "__main__",
        "export": True,
        "pluginName": "Mycelium",
        "pluginGHRepo": "https://github.com/MyceliumGH-Dev/Mycelium",
        "workingDir": os.path.join(os.path.dirname(_THIS_DIR), "docs"),
    }
    with open(EXPORT_SCRIPT, "r") as fh:
        source = fh.read()
    exec(compile(source, EXPORT_SCRIPT, "exec"), namespace)
    log("export script finished")


def main():
    canvas = load_editor()
    blank_document(canvas)
    run_export()


if __name__ == "__main__":
    exit_code = 0
    try:
        open(LOG_PATH, "w").close()
        main()
    except Exception as ex:
        log("FAILED: " + str(ex))
        log(traceback.format_exc())
        exit_code = 1

    sentinel = os.environ.get("MYCELIUM_DOCS_SENTINEL")
    if sentinel:
        try:
            with open(sentinel, "w") as fh:
                fh.write(str(exit_code))
        except Exception:
            pass

    # Do not let a save prompt block the unattended quit. RhinoApp.Exit() was observed NOT to
    # terminate the process under -runscript; the _Exit command does.
    try:
        active = Rhino.RhinoDoc.ActiveDoc
        if active is not None:
            active.Modified = False
    except Exception:
        pass
    if os.environ.get("MYCELIUM_DOCS_KEEP_OPEN") != "1":
        Rhino.RhinoApp.RunScript("_-Exit", False)
