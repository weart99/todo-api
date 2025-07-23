FROM python:3.12-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml .

# Install dependencies
RUN uv sync --no-dev

COPY src/ ./src/

EXPOSE 8000

# Launch the application using uv
CMD ["uv", "run", "uvicorn", "src.todo_api.main:app", "--host", "0.0.0.0", "--port", "8000"]