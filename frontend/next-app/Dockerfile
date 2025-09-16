### Multi-stage build for Next.js (production)
FROM node:18-alpine AS builder
WORKDIR /app

# Install build deps
COPY package*.json ./
RUN npm ci

# Copy sources and build
COPY . ./
ARG BACKEND_URL
ENV BACKEND_URL=$BACKEND_URL
RUN npm run build

### Production image
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Copy necessary artifacts from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./

# Install only prod dependencies
RUN npm ci --production

EXPOSE 3000
# Start Next in production mode
CMD ["npm", "run", "start", "--", "-p", "3000"]
