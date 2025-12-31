# =============================================================================
# Agent Web UI Dockerfile
# =============================================================================

FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json ./

RUN npm install --no-audit --no-fund

COPY . .

ENV NUXT_APP_BASE_URL=/agent/
ENV NUXT_PUBLIC_API_BASE=/api
ENV NUXT_PUBLIC_PREVIEW_BASE=/preview

RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/.output ./.output

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
