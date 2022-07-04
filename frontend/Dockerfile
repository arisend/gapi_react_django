FROM node:12-alpine as builder
WORKDIR /
COPY package.json /package.json
RUN npm install --only=prod
COPY . /
RUN npm run build