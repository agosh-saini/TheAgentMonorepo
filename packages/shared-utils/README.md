# shared-utils

Shared utility library for all projects in this monorepo.

## Modules

| Module | Description |
|---|---|
| `sqlite` | SQLite connection helpers |
| `logging` | Structured logger factory |
| `env` | Environment variable loading with validation |
| `config` | Config file parsing helpers |

## Usage

Install into a Python project:

```bash
# From any apps/python/<project> directory
uv add ../../packages/shared-utils
```

## Examples

```python
from shared_utils.sqlite import get_connection
from shared_utils.logging import get_logger
from shared_utils.env import require_env

logger = get_logger(__name__)
conn = get_connection("data/sqlite/myapp.db")
api_key = require_env("ANTHROPIC_API_KEY")
```
