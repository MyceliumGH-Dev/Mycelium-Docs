# First Steps

A first massing in about five minutes.

## 1. Start From a Template

The fastest route is not to build the graph by hand.

1. Drop a **Mycelium Templates** component on the canvas.
2. Click **Select Template** on the component.
3. Pick a template — it is downloaded on demand and a working example graph is inserted
   next to the component.

Templates come from the
[Mycelium-Templates](https://github.com/MyceliumGH-Dev/Mycelium-Templates) repository, on
the branch named after your installed plugin version, so a template always matches the
components you have.

!!! tip "Your own templates"

    Wire a folder path or a GitHub tree URL into the component's `Directory` input and
    your definitions appear in the menu alongside the official ones.

---

## 2. Build It By Hand

If you would rather wire it yourself, the minimum graph is four objects.

### Boundary

Reference a **closed, planar curve** from Rhino into a Curve parameter. This is the
parcel outline. A non-planar or open curve will not generate.

### Building configurations

Add at least one config component from **Mycelium → Building Types**:

- [Courtyard Config](components/Courtyard_Config.md) — perimeter block with a central void
- [Linear Config](components/Linear_Config.md) — bar along the block's long axis
- [Point Config](components/Point_Config.md) — compact point block
- [L-Shape Config](components/L-Shape_Config.md)
- [U-Shape Config](components/U-Shape_Config.md)
- [Tall Building Config](components/Tall_Building_Config.md) — tower

Every config exposes the same parameter set: floor range, corner radius, minimum footprint
area, setback range, and building depth range. Merge as many as you like into a single
list — each block picks one at random.

### Massing Generator

Wire it up:

| Input | Feed it |
| --- | --- |
| `Boundary` | the parcel curve |
| `BuildingConfigs` | the merged list of config outputs |
| `Divisions` | subdivision depth — start at `2`, raise for smaller blocks |
| `StreetWidth` | street width in model units |
| `NumParks` | how many blocks become parks |
| `Seed` | any integer; change it to get a different alternative |

`Masses` gives you the buildings, `Streets` the street geometry, `Parks` and `Courtyards`
the open space.

### Trees (optional)

Add a [Tree Config](components/Tree_Config.md) and wire its output into the generator's
`Trees` input. Set `GenerateInCourtyards` to place trees inside perimeter blocks as well
as in parks.

---

## 3. Choose a Street Network

Right-click the Massing Generator → **Street Network** and pick a family. The default
`Irregular Grid → Recursive Orthogonal` is the backwards-compatible behaviour; the other
families produce recognisably different urban form.

Driving it as a parameter instead — useful for sweeping every family in one run — is done
through the `StreetNetwork` text input, which overrides the menu.

---

## 4. Read the Metrics

Two outputs matter for analysis:

**`Metrics`** — development metrics: gross floor area, GIA, NIA, FAR, estimated unit
count, footprint and mass counts.

**`MorphologyMetrics`** — urban morphology indicators:

| Indicator | Meaning |
| --- | --- |
| `lambda_p` | Plan area density — built plan area over site area |
| `lambda_f` | Frontal area density facing `AnalysisDirection` |
| open / park ratio | Share of the site that is unbuilt, and that is park |
| height statistics | Mean, standard deviation, median, 90th percentile — both unweighted and plan-area-weighted |

!!! note "Use the weighted height moments"

    Roughness parameterizations expect the **plan-area-weighted** mean and standard
    deviation. The unweighted values give a single small structure the same influence as
    a tower.

---

## 5. Export a Reproducible Case

The `CaseManifest` output is schema-versioned JSON containing:

- a deterministic SHA-256 **case ID**, computed from the canonicalized boundary, the
  effective parameters, the seed, the plugin version, and the model units
- the effective generator inputs and street-network selection
- geometry counts, development metrics, and morphology metrics

Wire it to a panel and use the panel's **Stream Contents** command to write it next to
your geometry. Two runs sharing a case ID produced the same city.

The schema is published at
[`docs/case-manifest.schema.json`](https://github.com/MyceliumGH-Dev/Mycelium/blob/dev/docs/case-manifest.schema.json).

---

## Troubleshooting

??? question "Nothing generates"

    Check that the boundary curve is closed and planar. Also confirm at least one config
    component is wired into `BuildingConfigs` — with an empty list there is no typology to
    place.

??? question "Blocks are too large or too small"

    `Divisions` controls recursion depth, so block count roughly doubles per step. Adjust
    it before touching `MinArea` on the configs.

??? question "A warning about boolean fallbacks"

    A footprint may extend past its setback. The geometry is still returned, and the case
    manifest records how many fallbacks were taken, so you can filter those cases out of a
    dataset.

??? question "The template list is empty"

    No branch matching your installed version exists yet in Mycelium-Templates. Report the
    version you are on in an [issue](https://github.com/MyceliumGH-Dev/Mycelium/issues).

---

Next: the full [component reference](Components.md).
