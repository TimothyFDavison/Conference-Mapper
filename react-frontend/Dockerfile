# Copy and build dependencies
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install --frozen-lockfile
COPY .. .
RUN npm run build

# Serve with nginx
FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
ENV PUBLIC_URL=/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]