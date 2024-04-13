FROM python:3.12-alpine

# Upgrade system
RUN apk update && apk upgrade

# Setup workspace
RUN mkdir -p /app/src /app/data /app/config
WORKDIR /app

# Install Python requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

VOLUME "/app/data"
EXPOSE 5353

ARG UID=1000
RUN adduser user --uid ${UID} -S
RUN chown -R user /app
USER user

# Setup env vars for dockerized app

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ENV LINKSHARER_CONFIG_PATH=/app/config
ENV LINKSHARER_DATA_PATH=/app/data

# Copy app sources and setup
COPY src/ src/

# Launch app
CMD [ "gunicorn", "-b", "0.0.0.0:5353", "src.linksharer:app" ]
