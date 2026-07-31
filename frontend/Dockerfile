# Frontend image: MULTI-STAGE build.
#   Stage 1 (node): install deps and build the static site.
#   Stage 2 (nginx): serve those static files. The final image contains only the
#   built site + nginx — not Node or node_modules — so it's small.

# ---- Stage 1: build ----
FROM node:20-alpine AS build
WORKDIR /app

# At build time, tell the app to call the API at "/api" (nginx proxies it to the
# backend). Vite bakes env vars into the build, so this must be set BEFORE build.
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- Stage 2: serve ----
FROM nginx:alpine
# Copy the built site into nginx's web root.
COPY --from=build /app/dist /usr/share/nginx/html
# Our nginx config: serve the SPA and proxy /api to the backend container.
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
