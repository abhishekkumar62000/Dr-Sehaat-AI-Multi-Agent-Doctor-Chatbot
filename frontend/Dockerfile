# Dockerfile for Healthcare Chatbot Frontend

FROM python:3.11-slim

WORKDIR /app

# Copy frontend files
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000 || exit 1

# Run HTTP server
CMD ["python", "-m", "http.server", "8000", "--directory", "/app"]
