# Build Stage
FROM node:18.12.0-alpine AS build

RUN npm install pnpm@8.5.1 -g

WORKDIR /app

COPY ./package.json ./pnpm-lock.yaml /app/

COPY ./chore/nginx/nginx.conf /app/

RUN pnpm install

COPY . /app

RUN pnpm build

# Production Stage
FROM nginx:alpine

COPY --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
