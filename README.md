# bksys-transaction-ms

Transaction Micro Service

## Setup project

requirements:
- python 3.11
- poetry

### Install dependencies and load environment
```
poetry install && poetry shell
```

### Run application for development
```
uvicorn bksys-transaction-ms:app --reload --port 8083
```

## Lint project
```
poetry run flake8
```