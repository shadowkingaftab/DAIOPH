# Community Plugins

This directory is reserved for community-contributed plugins for DAIOPH.

## Structure

Each plugin lives in its own subdirectory and must contain:

- `manifest.json` — plugin metadata (name, version, title, domain, entry, register).
- `plugin.py` — the plugin implementation exposing a `register(registry) -> int`
  entry point that registers its `ToolSchema` instances into a
  `tools.registry.ToolRegistry`.

## Guidelines

- **No network by default.** Web/network tools must use injected backends so
  tests and offline deployments never touch the network.
- **Approval-gated destructive tools.** Any tool that writes, deletes, executes,
  or sends must set `destructive=True` on its `ToolSchema`.
- **Deny by default.** Tools are only callable when the registry's
  `allowed_tools` includes them (or an approval callback grants a destructive
  call).
- **Stdlib only.** Prefer the Python standard library; avoid adding heavy
  third-party dependencies.

## Example

```python
from tools.registry.tool_schema import ToolSchema

def my_tool(value: str) -> str:
    return value.upper()

my_tool_schema = ToolSchema(
    name="community_upper",
    description="Uppercase a string",
    fn=my_tool,
    params={"value": str},
)
```

Register it from `plugin.py`:

```python
def register(registry) -> int:
    registry.register(my_tool_schema)
    return 1