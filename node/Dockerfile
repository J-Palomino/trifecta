# Use the official Node.js 14 image as a parent image
FROM node:16

# Set the working directory in the container to /app
WORKDIR /app

# Copy the package.json and package-lock.json files to the container
COPY ./node/package*.json ./

# Install any needed packages specified in package.json
RUN npm install

# Copy the current directory contents into the container at /app
COPY ./node/ .

# Make port 3000 available to the world outside this container
EXPOSE 443 

# Run index.js when the container launches
CMD ["node", "node_modules/meshcentral"] 