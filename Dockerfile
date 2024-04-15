# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Copy application code and dependency files
COPY ./src /app/src
COPY ./pyproject.toml /app
COPY ./pdm.lock /app

# Set the working directory in the container
WORKDIR /app

# Create and activate the virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install PDM
RUN pip install pdm
RUN pdm install

# Expose port 8000 for FastAPI
EXPOSE 8000

# Install MySQL client
# RUN apt-get update && apt-get install -y default-mysql-client

# # Copy SQL initialization script
# COPY ./src/database/init.sql /docker-entrypoint-initdb.d/init.sql

# Command to run the FastAPI application
CMD ["uvicorn", "src.server.main:app", "--host", "grids-service", "--port", "8000", "--reload"]
