# Use an official Node runtime as the base image
FROM node:18-alpine as build

# Set the working directory in the container
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (both production and development)
RUN npm ci

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the build output to replace the default nginx page
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 3000
EXPOSE 3000

# Copy custom nginx configuration (optional)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Start nginx
CMD ["nginx", "-g", "daemon off;"]