# Build from monorepo root: docker build -f apps/web/Dockerfile -t notifications-hub-web .
FROM node:24-alpine AS base

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@9.15.0 --activate

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .nvmrc ./
COPY apps/web/package.json ./apps/web/
COPY libs/js/design-system/package.json ./libs/js/design-system/
COPY libs/js/notifications-ui/package.json ./libs/js/notifications-ui/

RUN pnpm install --frozen-lockfile --filter web...

COPY apps/web ./apps/web
COPY libs/js/design-system ./libs/js/design-system
COPY libs/js/notifications-ui ./libs/js/notifications-ui
COPY tsconfig.base.json ./

FROM base AS development
WORKDIR /app/apps/web
EXPOSE 3000
CMD ["pnpm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]

FROM base AS build
WORKDIR /app/apps/web
RUN pnpm run build

FROM node:24-alpine AS production
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@9.15.0 --activate
COPY --from=build /app/apps/web/.next ./.next
COPY --from=build /app/apps/web/package.json ./package.json
COPY --from=build /app/apps/web/public ./public
COPY --from=build /app/node_modules ./node_modules
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/ || exit 1
USER node
CMD ["pnpm", "run", "start"]
