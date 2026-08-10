"""Re-add the icon <img> markup to component entries in mkdocs.yml's nav.

Run after pasting a plain nav block over the Components section:

    python patch_nav.py

Idempotent: entries that already carry an <img> are left alone.
"""

import re

with open("mkdocs.yml", "r", encoding="utf-8") as f:
    text = f.read()


def repl(m):
    spaces, comp_name, filename = m.group(1), m.group(2), m.group(3)

    # Already patched.
    if "<img" in comp_name:
        return m.group(0)

    icon_name = filename[:-3]
    return (f"{spaces}- \"<img src='/images/icons/{icon_name}.png' "
            f"class='nav-gh-icon' /> {comp_name}\": components/{filename}")


new_text = re.sub(r'^(\s*)-\s*"([^"]+)":\s*components/([^.]+\.md)$', repl, text,
                  flags=re.MULTILINE)

with open("mkdocs.yml", "w", encoding="utf-8") as f:
    f.write(new_text)

print("mkdocs.yml nav patched.")
