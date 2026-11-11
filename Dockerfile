# Site public : seul index.html est servi (données intégrées).
FROM nginx:1.27-alpine
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
