FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_TOOL_BIN_DIR=/usr/local/bin


RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY --chown=nonroot:nonroot . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

ARG EMBEDDING_MODEL=all-MiniLM-L6-v2
ENV EMBEDDING_MODEL=${EMBEDDING_MODEL}
ENV HF_HOME=/app/.cache/huggingface

RUN python -c "import os; from sentence_transformers import SentenceTransformer; SentenceTransformer(os.environ['EMBEDDING_MODEL'])" \
 && chown -R nonroot:nonroot /app/.cache

ENV HF_HUB_OFFLINE=1

ENTRYPOINT []

USER nonroot

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
