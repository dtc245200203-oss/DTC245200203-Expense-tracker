# Multi-stage / Hardened Dockerfile for Expense Tracker
FROM node:20-alpine AS base

# Install dumb-init for proper PID 1 signal handling
RUN apk add --no-cache dumb-init

# Create non-root system group and user
RUN addgroup -g 10001 -S appgroup && \
    adduser -u 10001 -S appuser -G appgroup

WORKDIR /usr/src/app

# Install dependencies with clean cache
COPY package.json ./
RUN npm install --omit=dev && npm cache clean --force

# Copy application source code
COPY --chown=appuser:appgroup . .

# Set environment
ENV NODE_ENV=production \
    PORT=3000

# Create log directory with non-root ownership
RUN mkdir -p /var/log/app && chown -R 10001:10001 /var/log/app

# Security: Switch to non-root user
USER 10001:10001

# Expose internal container port
EXPOSE 3000

# Container Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:3000/healthz || exit 1

# Start app with dumb-init
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["node", "src/server.js"]
