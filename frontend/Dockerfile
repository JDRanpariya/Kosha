FROM oven/bun:1.1-alpine

WORKDIR /app

# Cache layer: install deps first

COPY package.json ./
RUN bun install

COPY . .

EXPOSE 5173
CMD ["bun", "run", "dev", "--", "--host", "0.0.0.0"]
