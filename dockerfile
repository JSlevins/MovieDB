FROM python:3.14-slim

# Setting work dir
WORKDIR /app/

# Copying files 
COPY src/requirements.txt ./
#COPY src/ ./src

# Setting requirements
RUN pip install --no-cache-dir -r requirements.txt

# Default command
