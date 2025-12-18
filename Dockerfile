# Stage 1: Build
FROM cgr.dev/chainguard/python:latest-dev AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:$PATH"

WORKDIR /app

# Install requirements in venv environment
RUN python -m venv /app/venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM cgr.dev/chainguard/python:latest AS production

WORKDIR /app

# Configure the environment to use the venv environment
ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"

# Copy build artifacts
COPY --from=builder /app/venv /venv

# Copy application files
COPY main.py .
ADD https://td.unfoldingword.org/exports/langnames.json .

EXPOSE 5000

ENTRYPOINT [ "python", "/app/main.py" ]