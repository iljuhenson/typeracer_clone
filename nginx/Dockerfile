FROM node:18.17 as builder

WORKDIR /app

#COPY typeracer_clone_react/ .
#COPY typeracer_clone_react/src/ /app/src
#COPY typeracer_clone_react/package.json typeracer_clone_react/package-lock.json typeracer_clone_react/vite.config.js typeracer_clone_react/.eslintrc.cjs typeracer_clone_react/index.html /app/
#
#RUN npm ci
#RUN npm run build

COPY typeracer_clone_react/dist/ /app/dist


FROM nginx as prod
ENV NODE_ENV production

WORKDIR /

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder ./app/dist ./usr/share/nginx/html