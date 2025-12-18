# Stage 1: Build
FROM dhi.io/python:3.12-alpine3.22-dev AS build

WORKDIR /app

COPY requirements.txt .

# Install requirements in venv environment
# Disable caching, to keep Docker image lean
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM dhi.io/python:3.12-alpine3.22

# Copy build artifacts
COPY --from=build /opt/venv /opt/venv

WORKDIR /app

# Copy application files
COPY main.py .
ADD https://td.unfoldingword.org/exports/langnames.json .

EXPOSE 5000

# Configure the environment to use the venv environment
ENV PATH="/opt/venv/bin/:$PATH"

CMD [ "python", "/app/main.py" ]
