FROM arm64v8/nginx:1.27

COPY nginx.conf /etc/nginx/templates/default.conf.template