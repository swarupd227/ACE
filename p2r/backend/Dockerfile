# Build context is the REPO ROOT (so we can COPY the shared core/ alongside p2r/).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/srv

WORKDIR /srv

COPY p2r/backend/requirements.txt .
RUN pip install -r requirements.txt

# Shared platform core + the P2R app. One-way: core knows nothing about p2r/ace.
COPY core ./core
COPY p2r/backend/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
