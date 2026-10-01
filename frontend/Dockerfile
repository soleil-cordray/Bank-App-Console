# Multi-stage build: build stage and nginx runtime
FROM node:20-alpine as builder

WORKDIR /build

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the React app
RUN npm run build

# Runtime stage: serve with nginx
FROM nginx:alpine

# Remove default nginx config
RUN rm -rf /etc/nginx/conf.d/default.conf /etc/nginx/nginx.conf

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built app from builder
COPY --from=builder /build/dist /usr/share/nginx/html

EXPOSE 80

# Health check
HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
