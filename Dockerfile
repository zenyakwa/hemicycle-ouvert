# Site public : index.html (données intégrées), logos des groupes, table des codes postaux
# (data/cp.json, mise à jour chaque nuit par src/fetch.py), configuration nginx.
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
COPY logos/ /usr/share/nginx/html/logos/
COPY data/cp.json /usr/share/nginx/html/cp.json
EXPOSE 80
