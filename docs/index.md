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

1. In Rhino 8, run `_PackageManager`.
2. Search for **mycelium**, install, and restart Rhino.
3. The components appear in Grasshopper under the **Mycelium** tab.

Full instructions, manual install, and pre-release builds:
[mycelium-gh.netlify.app/download](https://mycelium-gh.netlify.app/download/).

!!! warning "Rhino 8 only"

    Mycelium targets .NET 7 and relies on assemblies that only Rhino 8 supplies. It does
    not load in Rhino 7.

---

## The Toolbar

{!toolbar.md!}

Components are organized into five panels:

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

## Street Networks

Right-click the Massing Generator → **Street Network**. The selection is stored in the
Grasshopper definition and shown beneath the component.

| Family | Sub-options |
| --- | --- |
| Irregular Grid | `Recursive Orthogonal` (default), `Deformed Grid`, `Staggered Grid` |
| Orthogonal Grid | `Regular Grid`, `Rectangular Grid`, `Cerdà Grid`, `Hierarchical Superblock` |
| Diagonal Grid | `Single Axis`, `Cross Axes`, `Orthogonal Overlay` |
| Radial–Concentric Grid | `Civic Core`, `Polygonal Radial`, `Fan Plan` |

For batch campaigns, wire a sub-option name into the `StreetNetwork` input instead — e.g.
`"Orthogonal/Cerda"` or `"Fan Plan"`. It overrides the menu selection. Names are case-,
accent- and separator-insensitive; an unknown name raises a warning listing the valid
ones.

---

## Getting Help

- **Issues and feature requests**:
  [MyceliumGH-Dev/Mycelium](https://github.com/MyceliumGH-Dev/Mycelium/issues)
- **Templates**:
  [MyceliumGH-Dev/Mycelium-Templates](https://github.com/MyceliumGH-Dev/Mycelium-Templates)
- **Website**: [mycelium-gh.netlify.app](https://mycelium-gh.netlify.app)

When reporting a geometry problem, include the `CaseManifest` JSON — it pins down the
exact inputs, seed, and plugin version that produced the result.
