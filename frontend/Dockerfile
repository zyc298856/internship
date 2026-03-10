FROM node:20-alpine

WORKDIR /app

COPY package.json ./
# Run install. We don't have package-lock.json locally yet but npm install will generate it in container
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
