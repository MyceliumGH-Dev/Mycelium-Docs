# ![](/images/icons/Massing_Generator.png) Massing Generator - [[source code]](https://github.com/MyceliumGH-Dev/Mycelium/blob/dev/src/Mycelium/Components/MassingGeneratorComponent.cs)

Generate building masses with multiple typologies from a parcel boundary

<span class="faint">Grasshopper: **Mycelium** → **Massing** → `Massing`</span>

#### Input

| Name | Nickname | Description | Type | Default |
| ---- | -------- | ----------- | ---- | ------- |
| Boundary | B | Parcel boundary curve (closed, planar) | `Curve` |  |
| FloorHeight | FH | Floor-to-floor height (m) | `Number` | 4 |
| Divisions | Div | Subdivision recursion depth | `Integer` | 2 |
| StreetWidth | SW | Width of streets (m) | `Number` | 2.0 |
| BuildingConfigs | Configs | List of building configurations from Config components | `Text` | *optional* |
| NumParks | Parks | Number of park parcels | `Integer` | 2 |
| GenerateFloorSlabs | Slabs | Generate individual floor slabs | `Boolean` | false |
| Trees |  | Tree configuration from Tree Config component (optional) | `Text` | *optional* |
| Seed |  | Random seed | `Integer` | 0 |
| AnalysisDirection | Dir | Horizontal analysis direction for directional frontal area density (lambda_f) | `Vector` | *optional* |
| StreetNetwork | Net | Street network sub-option, e.g. "Orthogonal/Cerda" or "Fan Plan". Overrides the context-menu selection so a batch campaign can sweep the network families as an ordinary parameter. Leave empty to use the menu selection. | `Text` | *optional* |

#### Output

| Name | Nickname | Description | Type | Default |
| ---- | -------- | ----------- | ---- | ------- |
| Footprints | F | Building footprint curves | `Curve` |  |
| Masses | M | Building mass geometry | `Brep` |  |
| Heights | H | Building heights | `Number` |  |
| Streets | Str | Street geometry | `Curve` |  |
| FloorSlabs | FS | Individual floor slabs | `Brep` |  |
| Parks | P | Park boundaries | `Curve` |  |
| Courtyards | Court | Courtyard boundaries (for tree generation) | `Curve` |  |
| Trees | T | Tree spheres | `Brep` |  |
| Parcels | Parc | Building parcel boundaries | `Curve` |  |
| Metrics | Met | Area and unit metrics | `Text` |  |
| MorphologyMetrics | Morph | Urban morphology indicators including lambda_p, directional lambda_f, open/park ratios, and height statistics | `Text` |  |
| CaseManifest | JSON | Versioned JSON case manifest containing inputs, provenance, counts, development metrics, and morphology metrics | `Text` |  |
