# Commands

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run

``` bash
python app.py
```

## Run background worker (Celery)

```bash
celery -A celery_worker.celeryApp worker --loglevel=info --pool=solo
```

## Redis (required for Celery mode)

```bash
docker run -p 6379:6379 redis:7
```

## Future

```bash
uvicorn app.main:app --reload
pytest
ruff check . --fix
```
