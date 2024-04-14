FROM node:18.17 as builder

WORKDIR /app

COPY typeracer_clone_react/ .
RUN npm ci 
RUN npm run build


FROM nginx as prod
ENV NODE_ENV production

WORKDIR /

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder ./app/dist ./usr/share/nginx/html