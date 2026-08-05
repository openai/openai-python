# Stage 1: Build dependencies
FROM python:3.12-alpine AS builder

WORKDIR /app

# Install compiler toolchain and build requirements for potential source builds
RUN apk add --no-cache gcc musl-dev libffi-dev g++ cargo

# Create a virtual environment for isolated dependency building
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy package descriptors and source code
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Upgrade pip and install package dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Stage 2: Clean, optimized runner image
FROM python:3.12-alpine AS runner

WORKDIR /app

# Install runtime dependencies (like curl if needed, but python built-ins are enough)
# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy example mock server
COPY examples/staging_server.py ./staging_server.py
RUN chmod +x ./staging_server.py

# Expose staging port
EXPOSE 8080

# Configure default environment variables
ENV OPENAI_API_KEY=""

# Health check configuration
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')"

# Command to start the staging server
CMD ["python", "staging_server.py"]
