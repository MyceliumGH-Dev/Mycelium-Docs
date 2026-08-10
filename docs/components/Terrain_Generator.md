# ![](/images/icons/Terrain_Generator.png) Terrain Generator - [[source code]](https://github.com/MyceliumGH-Dev/Mycelium/blob/dev/src/Mycelium/Components/TerrainGeneratorComponent.cs)

Generates organic terrain with adjustable peak sharpness and damping

<span class="faint">Grasshopper: **Mycelium** → **Site** → `Terrain`</span>

#### Input

| Name | Nickname | Description | Type | Default |
| ---- | -------- | ----------- | ---- | ------- |
| Boundary | B | Closed curve that defines the terrain outline | `Curve` |  |
| Resolution | R | Grid cell size - smaller values give more detail but run slower (try 1 to 10) | `Number` | 5.0 |
| BaseHeight | Hb | Base ground level - the terrain sits on top of this | `Number` | 0.0 |
| MaxHeight | H | Maximum terrain height in model units (try 5 to 50) | `Number` | 20.0 |
| NoiseScale | NS | Horizontal scale of hills - smaller values create broader hills, larger values create tighter bumps | `Number` | 0.05 |
| Seed | S | Random seed - same number always produces the same terrain shape | `Integer` | 0 |
| Damping | D | Peak sharpness - below 1 smooths and rounds peaks, 1 is raw noise, above 1 sharpens peaks and flattens valleys (try 0.3 to 3.0) | `Number` | 1.0 |

#### Output

| Name | Nickname | Description | Type | Default |
| ---- | -------- | ----------- | ---- | ------- |
| Terrain | T | Generated terrain surface | `Brep` |  |
