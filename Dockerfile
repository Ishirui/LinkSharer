FROM python:3.12-alpine

# Upgrade system
RUN apk update && apk upgrade

# Setup workspace
RUN mkdir -p /app/src /app/data /app/config
WORKDIR /app

# Install Python requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy app sources and setup
COPY src/ src/

VOLUME "/app/data"
EXPOSE 5353

ARG UID=1000
RUN adduser user --uid ${UID} -S
RUN chown -R user /app
USER user

# Launch app
CMD [ "gunicorn", "-b", "0.0.0.0:5353", "src.linksharer:app" ]
