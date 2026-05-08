# PLI — adresse de test locale

Adresse créée pour les tests locaux PLI :

```text
test.pli@demo-pli.com
```

Usage :

- cette adresse est seedée dans la démo locale via `POST /demo/seed?reset=true` ou `POST /demo/reset` ;
- elle apparaît comme contact `demo-contact-test` / `Adresse test PLI` ;
- elle est disponible dans la liste des conversations ;
- elle sert à tester la recherche et le composer local sans vrai compte Gmail/Microsoft ;
- ce n’est pas une boîte mail publique et elle ne reçoit pas de vrais emails Internet.

Adresse de boîte locale démo PLI existante :

```text
demo@pli-app.fr
```

Pour tester :

```bash
cd /Users/jm/context-engine/projects/pli-app
make demo
```

Puis dans l’application, chercher ou ouvrir `test.pli@demo-pli.com`.
