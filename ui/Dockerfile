FROM node:20-slim

WORKDIR /app

# Application code and dependencies will be mounted via volume in compose.yaml
# No installation needed in Docker build for development environment

# Expose port
EXPOSE 3000

# Start development server (overridden by compose.yaml)
CMD ["npm", "run", "dev"]
