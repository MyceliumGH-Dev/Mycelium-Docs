# ![](/images/icons/L-Shape_Config.png) L-Shape Config - [[source code]](https://github.com/MyceliumGH-Dev/Mycelium/blob/dev/src/Mycelium/Components/BuildingConfigComponents.cs)

Configure L-Shape building parameters

Allows the L-shaped building typology on blocks handled by the [Massing Generator](/components/Massing_Generator/).

<span class="faint">Grasshopper: **Mycelium** → **Building Types** → `LCfg`</span>

#### Input

| Name | Nickname | Description | Type | Default |
| ---- | -------- | ----------- | ---- | ------- |
| MinFloors | Fmin | Minimum floors | `Number` | 3.0 |
| MaxFloors | Fmax | Maximum floors | `Number` | 6.0 |
| Radius | R | Corner radius for footprint | `Number` | 0.0 |
| MinArea | MinA | Minimum footprint area (m²) | `Number` | 100.0 |
| MinSetback | Smin | Minimum setback distance (m) | `Number` | 3.0 |
| MaxSetback | Smax | Maximum setback distance (m) | `Number` | 3.0 |
| MinDepth | Dmin | Minimum building depth/width (m) | `Number` | 12.0 |
| MaxDepth | Dmax | Maximum building depth/width (m) | `Number` | 12.0 |

#### Output

| Name | Nickname | Description | Type | Default |
| ---- | -------- | ----------- | ---- | ------- |
| Config | Cfg | Building configuration data | `Text` |  |
