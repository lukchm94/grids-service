# Builder container uses pdm to install dependencies
FROM python:3.11 AS builder

ENV PDM_VERSION=2.12.2

WORKDIR /build
COPY pdm.lock pyproject.toml ./
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install pdm && pdm install --prod --no-lock --no-editable

# Fresh container that does not have the build tool pdm
# Also using the slim image to save image size
FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Copy installed dependencies and binaries from the build container,
# and append to PYTHONPATH and PATH respectively
COPY --from=builder /build/__pypackages__/3.11/lib lib
COPY --from=builder /build/__pypackages__/3.11/bin bin

ENV PYTHONPATH "/app/lib"
ENV PATH "/app/bin:{$PATH}"

CMD [ "uvicorn", "src.server.main:app", "--host", "127.0.0.1", "--port", "3306" ]