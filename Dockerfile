# Start from a small official Python image
FROM python:3.12-slim

# All following commands run inside this folder in the container
WORKDIR /app

# Install dependencies first, on their own layer (see note below)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy just the code the API needs to run
COPY main.py ask.py search.py ./

# Note which port the app listens on (documentation)
EXPOSE 8000

# The command that runs when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]