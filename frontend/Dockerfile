FROM node:22-alpine

WORKDIR /usr/src/app

# Install deps separately to use Docker cache
COPY frontend/package.json frontend/package-lock.json* ./ 
RUN npm install

# Copy the rest of the app
COPY frontend/ ./

EXPOSE 3000

CMD ["npm", "start"]
