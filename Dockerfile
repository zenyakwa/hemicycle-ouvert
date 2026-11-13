# Site public : index.html (données intégrées), logos des groupes, configuration nginx.
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
COPY logos/ /usr/share/nginx/html/logos/
EXPOSE 80
