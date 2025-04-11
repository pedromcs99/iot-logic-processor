# Use an official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy the project files
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy the application code
COPY . .

# Default command: Run the Celery worker (Can be overridden)
CMD ["celery", "-A", "app.tasks", "worker", "--loglevel=info"]
