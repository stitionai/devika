# Pulling stage 1 image, keep alias as layer1
FROM node:latest as layer1

# Setting necessary arguments
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Copy UI source code
copy ui /home/nonroot/client

# Change Work directory
WORKDIR /home/nonroot/client

# Building APP bundle
RUN npm run build

# Pulling stage 2 image, to significantly reduce image size
FROM gcr.io/distroless/nodejs20-debian11

# Copy build files from layer 1
COPY --from=layer1 /home/nonroot/client/build /app
COPY --from=layer1 /home/nonroot/client/package.json /app

# Change Work directory
WORKDIR /app

# RUN APP
CMD ["index.js"]