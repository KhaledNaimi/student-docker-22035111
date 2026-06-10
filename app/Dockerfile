# ── Stage: runtime ─────────────────────────────────────────────────────────────
# Use a slim Python image to keep the final image small
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Install Python dependencies first (Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source (everything not in .dockerignore)
COPY . .

# Expose the port the Flask app listens on
EXPOSE 8000

# Run the application (not in debug mode for production)
CMD ["python", "app.py"]
