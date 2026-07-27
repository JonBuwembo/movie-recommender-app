FROM node:22

WORKDIR /app

# copy dependency file
COPY package*.json ./

# install dependencies
RUN npm install


# copy source code
COPY . .

EXPOSE 3000

CMD ["npm", "start"]