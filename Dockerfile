FROM python:3.12-alpine

# Upgrade system
RUN apk update && apk upgrade

# Setup workspace and user
ARG UID=1000
RUN adduser user --uid ${UID} -S
RUN mkdir /app
RUN chown user /app
WORKDIR /app

# Install Python requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy app sources
USER user
COPY src/ ./

# Launch app
CMD [ "gunicorn", "-b", "0.0.0.0:5000", "linksharer:app" ]
