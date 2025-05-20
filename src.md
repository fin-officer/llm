ollama-client/
├── Dockerfile
├── pyproject.toml
├── README.md
├── ansible/
│   ├── inventories/
│   │   ├── development/
│   │   │   ├── hosts.yml
│   │   │   └── group_vars/
│   │   │       └── all.yml
│   │   └── production/
│   │       ├── hosts.yml
│   │       └── group_vars/
│   │           └── all.yml
│   ├── playbooks/
│   │   ├── deploy.yml
│   │   ├── test-shell.yml
│   │   ├── test-mcp.yml
│   │   └── test-rest.yml
│   └── roles/
│       ├── common/
│       ├── ollama-deploy/
│       └── ollama-test/
├── tests/
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_shell.py
│   ├── test_rest_api.py
│   └── test_mcp.py
└── ollama_client/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   ├── client.py
    │   ├── models.py
    │   └── exceptions.py
    ├── interfaces/
    │   ├── __init__.py
    │   ├── shell/
    │   │   ├── __init__.py
    │   │   ├── cli.py
    │   │   └── interactive.py
    │   ├── rest/
    │   │   ├── __init__.py
    │   │   ├── app.py
    │   │   ├── routes.py
    │   │   └── schemas.py
    │   └── mcp/
    │       ├── __init__.py
    │       ├── adapter.py
    │       └── handlers.py
    └── utils/
        ├── __init__.py
        └── logging.py