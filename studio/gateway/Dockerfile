# ===========================================================================
# Nous RCM Studio — unified gateway
# Build context = repo root (so it can build BOTH frontends and the landing).
# Builds:
#   - ACE coding SPA   with base "/coding/"  -> /usr/share/nginx/html/coding
#   - P2R policy SPA   with base "/policy/"  -> /usr/share/nginx/html/policy
#   - a small landing                         -> /usr/share/nginx/html/index.html
# Serves all three from one origin and reverse-proxies each module's API.
# ===========================================================================

# --- build the Coding (ACE) SPA under /coding/ ---
FROM node:20-alpine AS build-coding
WORKDIR /app
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
ENV VITE_BASE_PATH=/coding/ \
    VITE_ROUTER_BASE=/coding \
    VITE_API_BASE=/coding/api \
    VITE_STUDIO=1
RUN npm run build

# --- build the Policy (P2R) SPA under /policy/ ---
FROM node:20-alpine AS build-policy
WORKDIR /app
COPY p2r/frontend/package.json ./
RUN npm install
COPY p2r/frontend/ ./
ENV VITE_BASE_PATH=/policy/ \
    VITE_ROUTER_BASE=/policy \
    VITE_API_BASE=/policy/api \
    VITE_STUDIO=1
RUN npm run build

# --- serve everything from one nginx ---
FROM nginx:1.27-alpine
COPY --from=build-coding /app/dist /usr/share/nginx/html/coding
COPY --from=build-policy /app/dist /usr/share/nginx/html/policy
COPY studio/gateway/index.html /usr/share/nginx/html/index.html
COPY studio/gateway/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
