FROM python:alpine

EXPOSE 5000

WORKDIR /app

COPY main.py .
COPY requirements.txt .
ADD https://td.unfoldingword.org/exports/langnames.json .

# Install requirements
# Disable caching, to keep Docker image lean
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "/app/main.py" ]
