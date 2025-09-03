FROM cubejs/cube:v0.34.62

WORKDIR /cube/conf

# Install system dependencies including MySQL client
RUN apt-get update && apt-get install -y \
    curl \
    default-mysql-client \
    telnet \
    netcat-openbsd \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy package.json and install dependencies first
COPY package.json ./
RUN npm install

# Copy application files
COPY index.js ./
COPY cube.js ./
COPY config/ ./config/
COPY model/ ./model/
COPY test.sh ./

# Make test script executable
RUN chmod +x test.sh

# Create logs directory
RUN mkdir -p /cube/conf/logs

EXPOSE 4000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:4000/readyz || exit 1

CMD ["node", "index.js"]