FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN python - <<'PY'
import subprocess
import tomllib

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

deps = data["project"]["dependencies"]
subprocess.check_call(["pip", "install", "--no-cache-dir", *deps])
PY

COPY src ./src

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
