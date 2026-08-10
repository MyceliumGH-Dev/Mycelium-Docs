# ![](/images/icons/Tree_Config.png) Tree Config - [[source code]](https://github.com/MyceliumGH-Dev/Mycelium/blob/dev/src/Mycelium/Components/TreeConfigComponent.cs)

Configure tree generation parameters for the massing generator

<span class="faint">Grasshopper: **Mycelium** → **Vegetation** → `TreeCfg`</span>

#### Input

| Name | Nickname | Description | Type | Default |
| ---- | -------- | ----------- | ---- | ------- |
| TreeDensity | TDens | Tree density percentage (0-100%). 100% = maximum density (1 tree per 25m²) | `Number` | 10.0 |
| MinDiameter | MinD | Minimum tree diameter in meters | `Number` | 2.0 |
| MaxDiameter | MaxD | Maximum tree diameter in meters | `Number` | 5.0 |
| GenerateInCourtyards | Court | Generate trees in building courtyards | `Boolean` | true |

#### Output

| Name | Nickname | Description | Type | Default |
| ---- | -------- | ----------- | ---- | ------- |
| Trees |  | Tree configuration data for the massing generator | `Text` |  |
