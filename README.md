# Mycelium-Docs

Component documentation for [Mycelium](https://github.com/MyceliumGH-Dev/Mycelium), built
with [MkDocs](https://www.mkdocs.org/) and
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Deployments

| Target | URL | Trigger |
| --- | --- | --- |
| Netlify (primary) | https://mycelium-gh-docs.netlify.app | push to `main` |
| GitHub Pages (mirror) | https://myceliumgh-dev.github.io/Mycelium-Docs/ | `deploy.yml` on push to `main` |

> **The gh-pages mirror renders without icons and screenshots.** Generated component pages
> use root-absolute asset paths (`/images/icons/...`) — the shape Grasshopper's exporter
> produces — which resolve at a domain root but not under the `/Mycelium-Docs/` subpath
> Pages serves from. Treat Netlify as the canonical URL. Pointing a custom domain (or a
> Pages custom domain) at the repo fixes the mirror without touching the exporter.

The marketing site lives in a separate repository:
[Mycelium-Website](https://github.com/MyceliumGH-Dev/Mycelium-Website).

## Branch model

- **`dev` is the working branch** — land changes here.
- **`main` is the published branch** — nothing reaches the live site until a `dev → main`
  PR is merged.

```bash
git push origin dev
gh pr create --base main --head dev
gh pr merge --merge
```

## Local development

```bash
pip install -r requirements.txt
mkdocs serve
```

Or with Docker, serving on <http://localhost:8080>:

```bash
./serve-docker.sh
```

## Regenerating the component reference

These files are **generated** — hand edits are overwritten:

```
docs/components/*.md          one page per component
docs/categories/*.md          one page per ribbon panel
docs/Components.md            overview
docs/toolbar.md               the ribbon widget
docs/components_nav.yml       nav block to paste into mkdocs.yml
docs/images/icons/*.png       component icons
docs/images/components/*.png  canvas screenshots
```

Regeneration reads the **installed plug-in** off a live Grasshopper canvas, so it needs
Rhino 8 with Mycelium installed and a logged-in desktop session (it is unattended, not
headless — Rhino opens and quits on its own):

```bash
tools/generate_docs.sh          # regenerate into the working tree
tools/generate_docs.sh --check  # fail if the checked-in docs have drifted
```

If the component set changed, paste `docs/components_nav.yml` over the `Components:` block
in `mkdocs.yml`, then run `python patch_nav.py` if the icon markup was lost.

Everything else — `index.md`, `first_steps.md` — is hand-written and safe to edit.

## Release coupling

On every Mycelium plugin release:

- `mkdocs.yml` → `latest_mycelium_version` pin.
- Re-run `tools/generate_docs.sh` if components or their descriptions changed.
- Then the `dev → main` PR.
