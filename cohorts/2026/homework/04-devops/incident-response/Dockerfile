FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn pydantic httpx

# Copy app code (for the agent to fix)
COPY app/ ./app/
COPY static/ ./static/
COPY pyproject.toml uv.lock ./

# Copy incident-response service code
COPY incident-response/ ./incident-response/

ENV INCIDENT_RESPONSE_PORT=8001
ENV APP_DIR=/app

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "incident-response.main:app", "--host", "0.0.0.0", "--port", "8001"]