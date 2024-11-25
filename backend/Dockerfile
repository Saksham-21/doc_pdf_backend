# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/uploads

# Install libreoffice for .docx to .pdf conversion
RUN apt-get update && apt-get install -y libreoffice && apt-get clean

# Copy the backend application code into the container
COPY . .

# Expose the FastAPI application port (default: 8000)
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]