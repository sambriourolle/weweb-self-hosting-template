# Sécurité et données

- `.env`, `imports/`, sauvegardes et résultats de test sont ignorés par Git. Les `.env*` sont exclus du contexte Docker.
- Utilisez des secrets aléatoires distincts ; aucun exemple n'est une valeur exécutable.
- MinIO crée un utilisateur applicatif distinct du compte root. La politique est volontairement large sur les deux buckets de cette instance : elle n'isole pas des applications mutuellement non fiables.
- Les volumes Docker persistent tant que vous n'utilisez pas `docker compose down -v`.
- La première initialisation PostgreSQL exécute votre SQL. Un répertoire vide ne rend pas un backend WeWeb fonctionnel.
- HTTP loopback est le seul périmètre testé. Le passage au LAN/Internet requiert HTTPS, cookies sûrs, durcissement réseau et une revue de l'authentification.

Les copies de build sont éphémères dans les couches Docker. Elles peuvent néanmoins contenir votre code ; ne publiez pas l'image construite sans audit séparé.
