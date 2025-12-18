# Stage 1: Build
FROM cgr.dev/chainguard/python:latest-dev AS builder

WORKDIR /app

COPY requirements.txt .

# Install requirements in venv environment
# Disable caching, to keep Docker image lean
RUN python -m venv /app/venv && \
    . /app/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM cgr.dev/chainguard/python:latest

# Copy build artifacts
COPY --from=builder /app/venv /app/venv

WORKDIR /app

# Copy application files
COPY main.py .
ADD https://td.unfoldingword.org/exports/langnames.json .

EXPOSE 5000

# Configure the environment to use the venv environment
ENV PATH="/app/venv/bin/:$PATH"

CMD [ "python", "/app/main.py" ]
