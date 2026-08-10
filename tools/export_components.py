# -*- coding: utf-8 -*-
"""Regenerate the component reference from the installed Mycelium plug-in.

Ported from Eddy3D-Documentation/tools/export_components.py. The Eddy3D version is hosted
inside a GhPython component in `Eddy3D/GenerateDocumentation.ghx`, which supplies the
`export` / `pluginName` / `pluginGHRepo` globals. Mycelium has no such definition, so this
port defaults those globals and can be executed directly:

    Rhino -> _RunPythonScript -> tools/export_components.py

or unattended through `tools/generate_docs.sh`, which drives Rhino for you.

It walks every non-obsolete object proxy whose Grasshopper category is `Mycelium`,
instantiates it on the canvas, and writes:

    docs/components/<Name>.md      one page per component (description + IO tables)
    docs/categories/<Panel>.md     one page per ribbon panel, with quick-link cards
    docs/Components.md             the overview page
    docs/toolbar.md                the ribbon widget, included by the pages above
    docs/components_nav.yml        the `nav:` block to paste into mkdocs.yml
    docs/images/icons/*.png        24x24 component icons
    docs/images/components/*.png   canvas screenshots (cropped by crop_images.py)

Hand edits to any of the generated files above are overwritten on the next run.
"""

import Grasshopper
import System.Drawing
import shutil
import os
import glob
import re
import json
import time

try:
    import System.Windows.Forms as WinForms
except ImportError:  # pragma: no cover - only missing outside a GUI session
    WinForms = None

# --- CROSS-COMPATIBLE URL DECODING (IronPython 2.7 & Python 3) ---
try:
    from urllib.parse import unquote, quote
except ImportError:
    from urllib import unquote, quote

# --- CONFIGURATION -----------------------------------------------------------
CLEAN_OUTPUT_DIR = True
USE_CROPPED_IMAGES = True

# --- SAFETY SETTINGS ---
DISABLE_SOLVER = True
COMPONENT_WAIT_TIME = 0.05

# Ribbon panel order. Grasshopper sorts panels by the plug-in's registration order, which
# alphabetical sorting does not reproduce (Eddy3D gets away with it because its panels are
# numbered "00 Setup", "01 Outdoor Setup", ...). Anything not listed here is appended
# alphabetically, so a new panel still shows up without editing this file.
CATEGORY_ORDER = ["Massing", "Building Types", "Vegetation", "Site", "Utilities"]

# Short blurb per panel, rendered under the heading on each category page.
CATEGORY_BLURB = {
    "Massing": "The generator itself: parcel boundary in, city block out.",
    "Building Types": ("One component per typology. Each emits a serialized configuration; "
                       "feed any combination into the Massing Generator and every block "
                       "picks one at random."),
    "Vegetation": "Tree density, size, and courtyard placement.",
    "Site": "Ground and context geometry.",
    "Utilities": "Example definitions and helpers.",
}

# --- FILE TRACKER ---
WRITTEN_FILES = []
COMPONENT_DESCRIPTIONS = {}
# -----------------------------------------------------------------------------


def track_file(path):
    norm_path = os.path.normpath(path)
    if norm_path not in WRITTEN_FILES:
        WRITTEN_FILES.append(norm_path)


def _read_text_safely(path):
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _ensure_parent_dir(path):
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent)


def ensure_utf8_file(path):
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as _f:
            _ = _f.read()
    except UnicodeDecodeError:
        txt = _read_text_safely(path)
        _ensure_parent_dir(path)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)


def write_utf8(path, text, mode="w"):
    _ensure_parent_dir(path)
    with open(path, mode, encoding="utf-8", newline="\n") as f:
        f.write(text)
    track_file(path)


def clean_string(text):
    """Turn a Grasshopper display name into a filesystem- and URL-safe stem."""
    if not text:
        return ""

    # 1. Decode URL percent-encoding (%28 -> '(', %29 -> ')', %C2%B7 -> '.')
    try:
        text = unquote(str(text))
    except Exception:
        pass

    # 2. Separators and punctuation that would break a path become underscores.
    text = re.sub(r"[_\s]*[·/\\&|:()][_\s]*", "_", text)

    # 3. Strip characters that are invalid in filenames.
    text = re.sub(r"[<>?*\"']", "", text)

    # 4. Remove control characters.
    text = "".join([c for c in text if ord(c) >= 32])

    # 5. Collapse runs of spaces/underscores.
    text = re.sub(r"[\s_]+", "_", text)

    # 6. No leading/trailing underscores.
    return text.strip("_")


def category_sort_key(name):
    try:
        return (0, CATEGORY_ORDER.index(name))
    except ValueError:
        return (1, name)


def sorted_categories(plugin_components):
    """Ribbon order for the display names behind the sanitized category keys."""
    return sorted(plugin_components.keys(),
                  key=lambda k: category_sort_key(CATEGORY_DISPLAY.get(k, k)))


# Sanitized category key -> original display name, filled during the export pass.
CATEGORY_DISPLAY = {}


def write_grouped_components(file_path, exposure_dict, base_folder):
    main_components = []
    hidden_components = []

    # Sort exposures by their logical GH_Exposure enum order, not alphabetically.
    exposure_order = ["primary", "secondary", "tertiary", "quarternary", "quinary",
                      "senary", "septenary", "hidden", "obscure"]

    def get_expo_weight(expo):
        try:
            return exposure_order.index(expo.lower())
        except ValueError:
            return 99

    for expo_name in sorted(exposure_dict.keys(), key=get_expo_weight):
        comps = sorted(exposure_dict[expo_name])

        valid_comps = []
        for c in comps:
            md_path = os.path.join(base_folder, "components", "%s.md" % c)
            if os.path.exists(md_path):
                valid_comps.append(c)
            else:
                print("Warning: Skipping broken link for %s (File missing: %s)" % (c, md_path))

        if "obscure" in expo_name.lower():
            hidden_components.extend(valid_comps)
        else:
            main_components.extend(valid_comps)

    def write_cards(comps, title):
        if not comps:
            return
        # Raw HTML heading: keeps it out of the integrated nav TOC (toc.integrate).
        slug = title.lower().replace(" ", "-")
        write_utf8(file_path,
                   '<h4 id="%s">%s</h4>\n<div class="index-quicklink-container">\n' % (slug, title),
                   mode="a")
        for comp in comps:
            desc = COMPONENT_DESCRIPTIONS.get(comp, "")
            card = '    <a href="/components/%s/" style="text-decoration: none;">\n' % comp
            card += '        <div class="index-quicklink">\n'
            card += '            <div class="index-quicklink-title">\n'
            card += '                <img src="/images/icons/%s.png" class="nav-gh-icon"> %s\n' % (
                comp, comp.replace("_", " "))
            card += '            </div>\n'
            card += '            <div class="index-quicklink-text">%s</div>\n' % desc
            card += '        </div>\n'
            card += '    </a>\n'
            write_utf8(file_path, card, mode="a")
        write_utf8(file_path, "</div>\n\n", mode="a")

    write_cards(main_components, "Main Components")
    write_cards(hidden_components, "Hidden Components")


def reset_output_directories(base_dir):
    if not CLEAN_OUTPUT_DIR:
        return
    print("Cleaning output directories in %s..." % base_dir)
    cat_dir = os.path.join(base_dir, "categories")
    if os.path.exists(cat_dir):
        try:
            shutil.rmtree(cat_dir)
        except Exception:
            pass
    comp_dir = os.path.join(base_dir, "components")
    if os.path.exists(comp_dir):
        for f in glob.glob(os.path.join(comp_dir, "*.md")):
            try:
                os.remove(f)
            except Exception:
                pass


def captureGrasshopperScreen(fileName, workingDirectory, component=None):
    target_dir = os.path.join(workingDirectory, "images", "components")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    imageSettings = Grasshopper.GUI.Canvas.GH_Canvas.GH_ImageSettings()
    imageSettings.Zoom = 2.15
    canvas = Grasshopper.GH_InstanceServer.ActiveCanvas
    canvas.Refresh()

    if component and component.Attributes:
        b = component.Attributes.Bounds
        # Generous margin so shadows, wires and balloons are not clipped.
        margin = 150
        rect = System.Drawing.Rectangle(int(b.X) - margin, int(b.Y) - margin,
                                        int(b.Width) + 2 * margin, int(b.Height) + 2 * margin)
    else:
        rect = System.Drawing.Rectangle(0, 0, 2, 2)

    imgsOfCanvas = canvas.GenerateHiResImage(rect, imageSettings)
    screenCapture = imgsOfCanvas[0][0]

    filePath = os.path.join(target_dir, fileName)
    if os.path.exists(filePath):
        os.remove(filePath)

    shutil.copyfile(screenCapture, filePath)
    track_file(filePath)

    try:
        shutil.rmtree(os.path.split(screenCapture)[0])
    except Exception:
        pass


def exportIcon(component, workingDirectory):
    target_dir = os.path.join(workingDirectory, "images", "icons")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    filePath = os.path.join(target_dir, getComponentName(component) + ".png")
    component.Icon_24x24.Save(filePath)
    track_file(filePath)


def getComponentByName(document, name):
    for component in document.Objects:
        if component.Name == name:
            return component


def getComponentName(component):
    return clean_string(component.Name.replace(pluginName + "_", ""))


def get_source_path(class_name, repo_dir):
    """Locate the .cs file declaring class_name, relative to the plug-in repo root."""
    if not class_name:
        return None
    pattern = re.compile(r"class\s+" + re.escape(class_name) + r"\b")
    try:
        for root, dirs, files in os.walk(repo_dir):
            if any(x in root for x in ["obj", "bin", "Tests", "Properties", ".git"]):
                continue
            for f in files:
                if f.endswith(".cs"):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                            if pattern.search(fh.read()):
                                return os.path.relpath(path, repo_dir).replace("\\", "/")
                    except Exception:
                        pass
    except Exception:
        pass
    return None


def clean_description(component):
    desc = component.Description.split("Provided by ")[0].replace("\n", " ")
    desc = re.sub(r"(?i)\s*Version\s+\d+\.\d+\.\d+\.\d+", "", desc)
    return " ".join(desc.split())


def exportDescription(component, githubFolder, githubRepo=None):
    bName = component.Name.replace(pluginName + "_", "")
    name = getComponentName(component)

    components_dir = os.path.join(githubFolder, "components")
    if not os.path.exists(components_dir):
        os.makedirs(components_dir)

    lines = []
    lines.append("# ![](/images/icons/%s.png) %s" % (name, bName))
    if githubRepo:
        repo_dir = os.path.abspath(os.path.join(githubFolder, "..", "..", PLUGIN_REPO_DIR))
        try:
            class_name = type(component).__name__
        except Exception:
            class_name = None
        mapped_path = get_source_path(class_name, repo_dir) if os.path.isdir(repo_dir) else None

        if mapped_path:
            lines[-1] += " - [[source code]](%s/blob/%s/%s)\n" % (githubRepo, PLUGIN_BRANCH, mapped_path)
        else:
            lines[-1] += " - [[source code]](%s/search?q=%s)\n" % (
                githubRepo, quote('"%s"' % component.Name))
    else:
        lines[-1] += "\n"

    image_filename = "%s-crop.png" % name if USE_CROPPED_IMAGES else "%s.png" % name
    if os.path.exists(os.path.join(githubFolder, "images", "components", image_filename)):
        lines.append("![](/images/components/%s)" % image_filename)

    lines.append("\n" + clean_description(component))
    lines.append('\n<span class="faint">Grasshopper: **%s** → **%s** → `%s`</span>'
                 % (component.Category, component.SubCategory, component.NickName))

    try:
        def cell(v):
            return str(v).strip().replace("\n", " ").replace("|", "\\|")

        def param_row(param):
            name_ = cell(param.Name)
            nick = cell(param.NickName)
            if nick == name_:
                nick = ""
            try:
                type_name = cell(param.TypeName)
            except Exception:
                type_name = ""
            optional = "*optional*" if getattr(param, "Optional", False) else ""
            return "| %s | %s | %s | %s | %s |" % (
                name_, nick, cell(param.Description),
                "`%s`" % type_name if type_name else "", optional)

        def param_table(params):
            rows = [param_row(params[i]) for i in range(params.Count)]
            if not rows:
                return ["*None*"]
            return ["| Name | Nickname | Description | Type | Default |",
                    "| ---- | -------- | ----------- | ---- | ------- |"] + rows

        lines.append("\n#### Input\n")
        lines.extend(param_table(component.Params.Input))
        lines.append("\n#### Output\n")
        lines.extend(param_table(component.Params.Output))
    except Exception as e:
        print(" - Warning: could not build IO tables: %s" % e)

    write_utf8(os.path.join(components_dir, "%s.md" % name), "\n".join(lines) + "\n")


def getPluginComponents(pluginName):
    components = {}
    for proxy in Grasshopper.Instances.ComponentServer.ObjectProxies:
        if proxy.Obsolete:
            continue
        if proxy.Desc.Category.strip() == pluginName:
            try:
                if str(proxy.Kind) == "UserObject":
                    components[proxy.Desc.Name] = Grasshopper.Kernel.GH_UserObject(
                        proxy.Location).InstantiateObject()
                else:
                    components[proxy.Desc.Name] = proxy.CreateInstance()
            except Exception:
                print("Skipping %s - Could not instantiate" % proxy.Desc.Name)
    return components


def createFolderStructure(githubFolder):
    if not os.path.exists(githubFolder):
        os.makedirs(githubFolder)
    for sub in ["images/components", "images/icons", "categories", "components"]:
        d = os.path.join(githubFolder, sub)
        if not os.path.exists(d):
            os.makedirs(d)


def build_toolbar_html(plugin_components):
    exposure_order = ["primary", "secondary", "tertiary", "quarternary", "quinary",
                      "senary", "septenary", "hidden", "obscure"]

    def get_expo_weight(expo):
        try:
            return exposure_order.index(expo.lower())
        except ValueError:
            return 99

    html = '<div class="Main-GhToolbar-Container">\n'
    for catKey in sorted_categories(plugin_components):
        readable = CATEGORY_DISPLAY.get(catKey, catKey.replace("_", " "))
        shortTitle = re.sub(r"^\d+[\s_]+", "", readable)

        html += '<div class="SubGroup-Container" data-category="%s">\n' % catKey
        html += '<div class="SubGroup-Icons">\n'
        html += '<div class="sub-group">\n'

        index = 0
        for expo_name in sorted(plugin_components[catKey].keys(), key=get_expo_weight):
            for comp in sorted(plugin_components[catKey][expo_name]):
                dataAttr = "above-dataComment" if (index % 2 == 0) else "below-dataComment"
                display = comp.replace("_", " ")
                html += ('<a href="/components/%s/" class="GhComponentItem" %s="%s">'
                         '<img src="/images/icons/%s.png" class="gh-component-selected" '
                         'alt="%s" /></a>\n' % (comp, dataAttr, display, comp, display))
                index += 1

        html += '</div>\n</div>\n'
        html += '<div class="SubGroup-Title">%s</div>\n' % shortTitle
        html += '</div>\n'
    html += '</div>\n\n'
    return html


# --- MAIN EXECUTION ----------------------------------------------------------

# Globals the Eddy3D original receives from its hosting GhPython component. Defaulted here
# so the script also runs straight from _RunPythonScript.
pluginName = globals().get("pluginName", "Mycelium")
pluginGHRepo = globals().get("pluginGHRepo", "https://github.com/MyceliumGH-Dev/Mycelium")
export = globals().get("export", True)

PLUGIN_REPO_DIR = "Mycelium"   # sibling checkout of the plug-in repo
PLUGIN_BRANCH = "dev"          # branch the [[source code]] links point at
DOC_REPO_DIR = "Mycelium-Docs"

componentsHeights = {}
pluginComponents = {}

_workingDir = globals().get("workingDir", None)
if _workingDir:
    githubFolder = _workingDir
else:
    # Prefer a docs checkout found relative to this file, then the active definition, then
    # the conventional ~/Documents/GitHub location.
    githubFolder = None
    _here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else None
    if _here:
        _candidate = os.path.join(os.path.dirname(_here), "docs")
        if os.path.isdir(_candidate):
            githubFolder = _candidate
    if githubFolder is None:
        try:
            ghdoc = Grasshopper.Instances.ActiveCanvas.Document
            if ghdoc and ghdoc.FilePath:
                _cur = os.path.dirname(ghdoc.FilePath)
                for _ in range(5):
                    _candidate = os.path.join(_cur, DOC_REPO_DIR, "docs")
                    if os.path.isdir(_candidate):
                        githubFolder = _candidate
                        break
                    _cur = os.path.dirname(_cur)
        except Exception:
            pass
    if githubFolder is None:
        githubFolder = os.path.expanduser("~/Documents/GitHub/%s/docs" % DOC_REPO_DIR)

print("Writing to: %s" % githubFolder)

doc = Grasshopper.Instances.ActiveCanvas.Document
original_solver_state = doc.Enabled
if DISABLE_SOLVER:
    print("Disabling Solver...")
    doc.Enabled = False

if export:
    reset_output_directories(githubFolder)
    createFolderStructure(githubFolder)
    components = getPluginComponents(pluginName)
    print("Found %d components in category '%s'" % (len(components), pluginName))

    for GHObjectName, GHObject in components.items():
        if not GHObject.Attributes:
            continue

        GHObject.Attributes.Pivot = System.Drawing.PointF(200, 215)
        print("Processing: %s" % GHObjectName)

        try:
            doc.AddObject(GHObject, False, 0)
            GHObject.Attributes.ExpireLayout()
            GHObject.Attributes.PerformLayout()

            if COMPONENT_WAIT_TIME > 0:
                if WinForms is not None:
                    WinForms.Application.DoEvents()
                time.sleep(COMPONENT_WAIT_TIME)

            component = getComponentByName(doc, GHObjectName)
            name = getComponentName(component)

            # Hidden/obscure components are excluded from the documentation entirely.
            expo_check = str(component.Exposure).lower()
            if "hidden" in expo_check or "obscure" in expo_check:
                print(" - Skipping hidden component.")
                continue

            try:
                captureGrasshopperScreen(name + ".png", githubFolder, component)
                exportIcon(component, githubFolder)
                exportDescription(component, githubFolder, pluginGHRepo)
                componentsHeights[name] = str(component.Attributes.Bounds.Height)
                COMPONENT_DESCRIPTIONS[name] = clean_description(component)

                catKey = clean_string(component.SubCategory)
                CATEGORY_DISPLAY[catKey] = component.SubCategory
                pluginComponents.setdefault(catKey, {})
                expo = str(component.Exposure).split(",")[-1].strip()
                pluginComponents[catKey].setdefault(expo, []).append(name)
            except Exception as e:
                print(" - Error exporting contents: %s" % e)

        except Exception as e:
            print(" - CRITICAL ERROR processing component: %s" % e)

        finally:
            try:
                doc.RemoveObject(GHObject, False)
            except Exception:
                print(" - Warning: Could not remove object cleanly.")

    json_path = os.path.join(githubFolder, "images", "componentsHeight.json")
    write_utf8(json_path, json.dumps(componentsHeights, ensure_ascii=False, indent=4))

if DISABLE_SOLVER:
    doc.Enabled = original_solver_state
    print("Solver state restored.")

# --- CATEGORY PAGES ----------------------------------------------------------
for catKey in sorted_categories(pluginComponents):
    readable = CATEGORY_DISPLAY.get(catKey, catKey.replace("_", " "))
    categoryFilePath = os.path.join(githubFolder, "categories", "%s.md" % catKey)
    ensure_utf8_file(categoryFilePath)

    # Scoped style dims every toolbar group except the current category's.
    dim_style = ("<style>\n"
                 '.Main-GhToolbar-Container .SubGroup-Container:not([data-category="%s"]) {\n'
                 "  filter: grayscale(1);\n"
                 "  opacity: 0.35;\n"
                 "}\n"
                 "</style>\n" % catKey)
    blurb = CATEGORY_BLURB.get(readable, "")
    header = "{!toolbar.md!}\n\n%s\n# %s\n" % (dim_style, readable)
    if blurb:
        header += "\n%s\n" % blurb
    write_utf8(categoryFilePath, header + "\n")
    write_grouped_components(categoryFilePath, pluginComponents[catKey], githubFolder)

# --- TOOLBAR + OVERVIEW ------------------------------------------------------
toolbar_html = build_toolbar_html(pluginComponents)

toolbarPath = os.path.join(githubFolder, "toolbar.md")
ensure_utf8_file(toolbarPath)
write_utf8(toolbarPath, toolbar_html)

summaryPath = os.path.join(githubFolder, "Components.md")
ensure_utf8_file(summaryPath)
write_utf8(summaryPath, "# %s Component List\n\n" % pluginName)
write_utf8(summaryPath, toolbar_html, mode="a")

for catKey in sorted_categories(pluginComponents):
    readable = CATEGORY_DISPLAY.get(catKey, catKey.replace("_", " "))
    # Raw HTML heading: keeps it out of the integrated nav TOC (toc.integrate).
    anchor = readable.lower().replace(" ", "-").replace("+", "")
    write_utf8(summaryPath, '<h2 id="%s">%s</h2>\n' % (anchor, readable), mode="a")
    write_grouped_components(summaryPath, pluginComponents[catKey], githubFolder)

# --- MKDOCS NAV BLOCK --------------------------------------------------------
navPath = os.path.join(githubFolder, "components_nav.yml")
ensure_utf8_file(navPath)
nav_lines = ["  - Components:", '      - "Overview": Components.md']

exposure_order = ["primary", "secondary", "tertiary", "quarternary", "quinary",
                  "senary", "septenary", "hidden", "obscure"]


def _expo_weight(expo):
    try:
        return exposure_order.index(expo.lower())
    except ValueError:
        return 99


for catKey in sorted_categories(pluginComponents):
    readable = CATEGORY_DISPLAY.get(catKey, catKey.replace("_", " "))
    nav_lines.append('      - "%s":' % readable)
    nav_lines.append('          - "Overview": categories/%s.md' % catKey)

    main_components = []
    hidden_components = []
    for expo_name in sorted(pluginComponents[catKey].keys(), key=_expo_weight):
        comps = sorted(pluginComponents[catKey][expo_name])
        if "obscure" in expo_name.lower():
            hidden_components.extend(comps)
        else:
            main_components.extend(comps)

    for comp in main_components + hidden_components:
        nav_lines.append(
            '          - "<img src=\'/images/icons/%s.png\' class=\'nav-gh-icon\' /> %s": '
            'components/%s.md' % (comp, comp.replace("_", " "), comp))

write_utf8(navPath, "\n".join(nav_lines) + "\n")

# --- SUMMARY -----------------------------------------------------------------
print("\n" + "=" * 60)
print("EXPORT COMPLETE: %d Files Written" % len(WRITTEN_FILES))
print("=" * 60)

images = [f for f in WRITTEN_FILES if f.endswith((".png", ".jpg", ".jpeg"))]
docs_written = [f for f in WRITTEN_FILES if f.endswith(".md")]
data_files = [f for f in WRITTEN_FILES if f.endswith((".json", ".yml"))]

for label, group in (("Markdown Documents", docs_written),
                     ("Images & Icons", images),
                     ("Data Files", data_files)):
    if group:
        print("\n--- %s (%d) ---" % (label, len(group)))
        for f in sorted(group):
            print("  %s" % f)

print("\nDone! Now run:  python tools/crop_images.py docs")
