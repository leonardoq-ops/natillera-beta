# Build context MUST be the repo root (natillera-beta/), not api/, so
# this can COPY app/natillera_engine and app/db into the image - keeping
# exactly one copy of that code in git, combined only at build time.
#
#   docker build -f api/Dockerfile -t natillera-proof-api .
#
FROM python:3.12-slim

WORKDIR /srv

COPY api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/natillera_engine ./natillera_engine
COPY app/db ./db
COPY api/*.py ./

ENV PORT=8080
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
