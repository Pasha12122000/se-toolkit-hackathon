FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json tsconfig.json vite.config.ts index.html ./
COPY src ./src

RUN npm install
RUN npm run build

FROM alpine
COPY --from=builder /app/dist /output

