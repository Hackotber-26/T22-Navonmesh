FROM node:20-alpine AS base

WORKDIR /app

# Install dependencies based on package.json
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend ./

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["npm", "run", "dev"]

