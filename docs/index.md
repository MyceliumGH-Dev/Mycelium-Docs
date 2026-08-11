---
hide:
  # Landing page for the docs — it routes you onward with its own links and cards, so the
  # nav tree (and, with toc.integrate, the TOC that lives inside it) is noise here.
  - navigation
  - toc
---

# Mycelium Documentation

Mycelium is a Grasshopper plugin for **generative urban massing** in Rhino 8. Feed it a
closed parcel boundary and it returns a complete city block: subdivided parcels, streets,
building masses across six typologies, parks, trees, terrain, and a full set of
development and morphology metrics.

![Sample massing outputs](/images/samples.gif){.skip-lightbox}

<div align="center" markdown="1">
  [First Steps :material-arrow-right:](first_steps.md){ .md-button .md-button--primary aria-label="Read the first steps guide" }
  [Component Reference :material-view-grid:](Components.md){ .md-button aria-label="Browse the component reference" }
</div>

---

## Install

In Rhino 8, run `_PackageManager`, search for **mycelium**, install, and restart. The
components appear in Grasshopper under the **Mycelium** tab.

Manual install, pre-release builds, and building from source are covered on the
[download page](https://mycelium-gh.netlify.app/download/).

!!! warning "Rhino 8 only"

    Mycelium targets .NET 7 and relies on assemblies that only Rhino 8 supplies. It does
    not load in Rhino 7.

---

## Where Things Are

Components are organized into five panels. The
[component reference](Components.md) carries the full toolbar and a card per component;
each panel page below carries its own.

| Panel | What lives there |
| --- | --- |
| [Massing](categories/Massing.md) | The generator itself — parcel in, city block out |
| [Building Types](categories/Building_Types.md) | One config component per typology |
| [Vegetation](categories/Vegetation.md) | Tree density, size, courtyard placement |
| [Site](categories/Site.md) | Procedural terrain |
| [Utilities](categories/Utilities.md) | Example definitions synced from GitHub |

---

## How the Pieces Fit

```
Boundary curve ─┐
                │
Config comps ───┼──▶  Massing Generator  ──▶ Footprints, Masses, Streets,
                │                             Parks, Courtyards, Trees, Parcels
Tree Config ────┘                        ──▶ Metrics, MorphologyMetrics
                                         ──▶ CaseManifest (JSON provenance)
```

1. **Subdivision** — recursive binary space partitioning splits the parcel into building
   blocks separated by streets. The street-network family is chosen from the component's
   right-click menu or driven by the `StreetNetwork` input.
2. **Typologies** — each block receives a randomly selected building type from the
   configurations you wired in: courtyard, linear, point, L-shape, U-shape, or tower.
3. **Open space** — `NumParks` blocks become parks and are populated with procedural
   trees; courtyards can receive trees too.
4. **Metrics & provenance** — development metrics, morphology indicators, and a
   schema-versioned JSON case manifest for every alternative.

Everything is driven by the `Seed` input, so alternatives are reproducible.

![Algorithm overview](/images/algorithm.jpeg){ loading=lazy }

---

## Getting Help

- **Issues and feature requests**:
  [MyceliumGH-Dev/Mycelium](https://github.com/MyceliumGH-Dev/Mycelium/issues)
- **Templates**:
  [MyceliumGH-Dev/Mycelium-Templates](https://github.com/MyceliumGH-Dev/Mycelium-Templates)
- **Website**: [mycelium-gh.netlify.app](https://mycelium-gh.netlify.app)

When reporting a geometry problem, include the `CaseManifest` JSON — it pins down the
exact inputs, seed, and plugin version that produced the result.
