FROM public.ecr.aws/docker/library/node:24.12.0-bookworm-slim AS prepare
RUN apt-get update && apt-get install -y --no-install-recommends python3 && rm -rf /var/lib/apt/lists/*
WORKDIR /scaffold
COPY scripts/prepare.py ./prepare.py
COPY imports/frontend /imports/frontend
COPY imports/backend /imports/backend
RUN python3 ./prepare.py --frontend /imports/frontend --backend /imports/backend --output /prepared

FROM public.ecr.aws/docker/library/node:24.12.0-bookworm-slim AS deps
WORKDIR /app
COPY --from=prepare /prepared/backend/package.json /prepared/backend/package-lock.json ./
RUN npm ci --ignore-scripts

FROM public.ecr.aws/docker/library/node:24.12.0-bookworm-slim
WORKDIR /app
ENV NODE_ENV=development
COPY --from=deps /app/node_modules ./node_modules
COPY --from=prepare /prepared/backend ./
RUN node ./init-data.ts
EXPOSE 3030
CMD ["node", "src/index_server.ts"]
