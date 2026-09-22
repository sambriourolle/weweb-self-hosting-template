# Héberger localement un export WeWeb avec Docker

> **Expérimental et non officiel.** Ce dépôt exécute les exports que **vous** fournissez ; il ne contient aucun export WeWeb, utilisateur, base, fichier ni secret. Il est testé sur une forme précise d'exports frontend/backend WeWeb (Node 24, backend Hono/WeWeb Auth, stockage `aws-s3`). Les exports inconnus arrêtent le build avec une erreur de compatibilité plutôt que d'être modifiés silencieusement.

## Ce qui est réellement automatisé

`docker compose up --build` copie vos exports dans l'image, enlève `.env*`, applique des correctifs contrôlés et compilera le **vrai frontend exporté**. Les correctifs connus activent MinIO compatible S3, les cookies HTTP uniquement pour une origine loopback, les paramètres de routes et les imports d'extensions `@weweb-internal`.

Services persistants : PostgreSQL et MinIO (volumes Docker). Seul le frontend est publié, sur `127.0.0.1:8080` par défaut. Le proxy Nginx envoie `/api` au backend réel. Les buckets et un compte MinIO applicatif sont créés sans écraser d'objet existant.

## Limite cruciale : la base de données

Un export de code frontend/backend WeWeb inspecté ne contient **pas** le schéma, les utilisateurs, les données ni les objets S3. Il est donc impossible de créer un bootstrap SQL générique honnête à partir des deux dossiers. Cette maquette ne fournit pas de schéma SamNotes déguisé en solution générale.

Avant le premier démarrage, copiez le SQL de votre propre application dans `imports/database/` (un ou plusieurs fichiers `*.sql`). PostgreSQL les exécute seulement lors de la création initiale du volume. Pour une application avec WeWeb Auth, ce SQL doit notamment créer les tables `auth` attendues par votre version exportée. Générez/exportez le schéma depuis la source que vous contrôlez et vérifiez-le dans un projet jetable. Pour changer ce SQL sur une base déjà initialisée, effectuez une migration explicite ; ne lancez pas `down -v` sur vos données.

## Démarrage : les seules préparations sont les copies et `.env`

```sh
git clone https://github.com/sambriourolle/weweb-self-hosting-template.git
cd weweb-self-hosting-template
cp .env.example .env
# Éditez .env : remplacez chaque CHANGE_ME par une valeur aléatoire distincte.
# macOS/Linux : openssl rand -base64 36

# Copiez les RACINES de vos exports, pas leurs .git/node_modules/.env.
rsync -a --delete /chemin/vers/export-frontend/ imports/frontend/
rsync -a --delete /chemin/vers/export-backend/ imports/backend/
rsync -a --delete /chemin/vers/votre-schema-sql/ imports/database/

docker compose up --build
```

Aucune commande de patch ou de préparation à lancer ensuite : les Dockerfiles appellent `scripts/prepare.py` durant le build. Ouvrez l'URL définie par `APP_URL` (par défaut <http://127.0.0.1:8080>). La création de compte dépend de votre configuration d'auth exportée ; elle n'est pas inventée par ce dépôt.

Pour arrêter : `docker compose down`. Cela conserve les données. **`docker compose down -v` détruit PostgreSQL et MinIO.**

## Origine, sécurité et exposition

`APP_URL` doit exactement correspondre à l'URL navigateur, port compris. Il est injecté au build frontend ; modifiez-le puis rebâtissez. Par défaut, `BIND_ADDRESS=127.0.0.1` et `LOCAL_HTTP=true`: HTTP et les cookies relâchés sont acceptables uniquement sur la machine locale. Pour un LAN ou Internet, ne changez pas seulement l'adresse : utilisez HTTPS avec une origine sûre et `LOCAL_HTTP=false`, puis testez les cookies/authentification. Ce dépôt ne revendique ni déploiement Internet, ni TLS, ni fonctionnement hors-ligne (les images et dépendances doivent être téléchargées au premier build).

Ne commitez jamais `.env`, les exports, votre SQL réel, dumps, ni données utilisateur. Ils sont ignorés par Git et les `.env*` sont exclus du contexte Docker ; inspectez toutefois vos exports avant de les copier.

## Vérification et exploitation

```sh
python3 -m unittest discover -s tests/unit -v
docker compose config --quiet
# après démarrage : vérifier les conteneurs et les logs sans afficher .env
curl -i http://127.0.0.1:8080/api/auth/get-session
```

Le dernier appel doit répondre sans erreur 5xx ; il ne prouve pas que votre schéma, authentification ni workflows sont corrects. Testez dans le navigateur exporté : inscription/connexion, route API authentifiée, fichier S3, puis `docker compose up -d --force-recreate` et revalidez la persistance. Sauvegardez PostgreSQL et MinIO avant toute mise à jour ; cette v0.1 ne fournit pas encore de procédure de restauration validée.

## Compatibilité et refus volontaire

Compatible uniquement avec les signatures contrôlées par `scripts/prepare.py`. Le build s'arrête si un fichier ou une signature a changé, si les extensions frontend ne sont pas détectées, ou si un correctif ne peut être appliqué exactement une fois. Cela évite d'exécuter une exportation à moitié corrigée. Consultez [docs/compatibilite.md](docs/compatibilite.md) avant d'ouvrir une issue avec les versions d'export et le message redigé de l'erreur — jamais les secrets.

## Licence

Les scripts, Dockerfiles et documentation de ce dépôt sont sous licence MIT. Les exports WeWeb restent soumis à leurs propres licences et conditions : vous les fournissez localement et ils ne sont pas redistribués ici.
