FROM public.ecr.aws/docker/library/node:24.12.0-bookworm-slim AS prepare
RUN apt-get update && apt-get install -y --no-install-recommends python3 && rm -rf /var/lib/apt/lists/*
WORKDIR /scaffold
COPY scripts/prepare.py ./prepare.py
COPY imports/frontend /imports/frontend
COPY imports/backend /imports/backend
RUN python3 ./prepare.py --frontend /imports/frontend --backend /imports/backend --output /prepared

FROM public.ecr.aws/docker/library/node:24.12.0-bookworm-slim AS build
WORKDIR /export
COPY --from=prepare /prepared/frontend/package.json /prepared/frontend/package-lock.json ./
RUN npm ci --ignore-scripts
COPY --from=prepare /prepared/frontend ./
ARG APP_URL
RUN printf 'APP_URL=%s\nSERVER_URL=%s\n' "$APP_URL" "$APP_URL" > .env.production && npm run build

FROM public.ecr.aws/nginx/nginx:1.29.3-alpine
COPY --from=build /export/dist /usr/share/nginx/html
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
