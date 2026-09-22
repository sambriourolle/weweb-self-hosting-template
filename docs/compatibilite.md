# Compatibilité des exports

Le préparateur ne promet aucune compatibilité universelle. Il a été exercé sur des exports ayant les signatures suivantes :

- backend Node `>=24.11`, `src/index_server.ts`, intégrations `weweb-auth`, `weweb-storage` et `aws-s3` présentes dans l'export ;
- routes de workflows Hono, métadonnées API `/api/...` utilisant `{param}` ;
- frontend Vite avec `vite.config.js`, `src/extensions/**/package.json` et imports `@weweb-internal/...`.

Correctifs appliqués dans une **copie de build** : enregistrement du pilote S3, endpoint MinIO et path-style, cookies HTTP seulement lorsque `LOCAL_HTTP=true`, conversion de routes/paramètres, alias Vite des extensions. Chaque remplacement doit apparaître exactement une fois.

Un arrêt `ERREUR DE COMPATIBILITÉ` est attendu pour une version ou architecture inconnue. Ne modifiez pas le script pour supprimer le contrôle : comparez l'export avec la signature, écrivez un test de fixture, puis ajoutez un correctif versionné et vérifié. Le frontend peut aussi nécessiter une correction spécifique à ses propres workflows/configuration ; celle-ci n'est jamais déduite à partir d'un projet exemple.

Le double préfixe `/api/api` est traité dans Nginx parce qu'il a été observé sur l'export testé. Si votre export ne le produit pas, la règle `/api/` reste correcte ; si son backend possède une topologie différente, le préparateur doit refuser ou être étendu avec un test.
