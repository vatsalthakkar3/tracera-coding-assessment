FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_CACHE_DIR=/root/.cache/uv

WORKDIR /app

COPY ./pyproject.toml ./requirements.txt* ./uv.lock* ./

RUN if [ -f "pyproject.toml" ]; then \
        uv sync --frozen --no-cache; \
    elif [ -f "requirements.txt" ]; then \
        uv pip install --system -r requirements.txt; \
    else \
        echo "No dependency file found, skipping installation."; \
    fi

COPY . .

CMD ["python", "-m", "src.main"]
