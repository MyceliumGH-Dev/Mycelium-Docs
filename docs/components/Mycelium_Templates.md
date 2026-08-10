# ![](/images/icons/Mycelium_Templates.png) Mycelium Templates - [[source code]](https://github.com/MyceliumGH-Dev/Mycelium/blob/dev/src/Mycelium/Components/TemplateComponent.cs)

Load example Grasshopper definitions for common Mycelium workflows. Templates are synced from the Mycelium-Templates GitHub repository; your own folders and GitHub URLs are offered alongside.

<span class="faint">Grasshopper: **Mycelium** → **Utilities** → `Templates`</span>

#### Input

| Name | Nickname | Description | Type | Default |
| ---- | -------- | ----------- | ---- | ------- |
| Directory | Dir | Additional template sources: local folder paths or GitHub repository URLs. | `Text` | *optional* |

#### Output

| Name | Nickname | Description | Type | Default |
| ---- | -------- | ----------- | ---- | ------- |
| Templates | T | Template file paths from all sources. | `Text` |  |
