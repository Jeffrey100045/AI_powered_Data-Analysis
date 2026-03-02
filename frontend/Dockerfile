# Step 1: Build the React application
FROM node:20-slim AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application and build
COPY . .
RUN npm run build

# Step 2: Serve the application using Nginx
FROM nginx:stable-alpine

# Copy built files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Render uses the PORT environment variable, so we need to adjust nginx to listen on it
# Usually Render manages the port mapping, but it's safer to be flexible
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
