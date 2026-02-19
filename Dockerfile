# Use slim Python image to keep things small
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to take advantage of layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (Matches Flask app default)
EXPOSE 5001

# Run the application
CMD ["python", "app.py"]
