# Banana OS — architecture cible

## Navigation
Accueil, Opérations, Finance, Réseau, Documents, Intelligence. Un espace dirigeant, droits employés désactivés par défaut. Espace client et site public inchangés.

## Données
Identifiants stables, société obligatoire, provenance, date de vérification, versions, journal d'audit. Montants en centimes MAD, HT/TVA/TTC distincts. Valeurs inconnues null, jamais zéro implicite. Séparer commande, livraison, facture, paiement et rapprochement. Import CRM idempotent, sauvegarde préalable, aucun effacement historique.

## Finance
Transactions confirmées, soldes rapprochés, coûts directs, charges, échéances, provisions, réserves, capacité de délégation et rémunération. Prévisions distinctes des faits. Aucun placement ni paiement automatique.

## Documents
Brouillon, à contrôler, à valider, approuvé, archivé. Approbation explicite par version et empreinte; destination autorisée; conserver original et historique. Pas d'archivage automatique sans approbation.

## Intégrations
Adaptateurs serveur pour CRM, Gmail, Drive, Sheets, Docs, Calendar; compte professionnel vérifié avant utilisation. Secrets hors dépôt. Automatisations horaires avec déduplication et alertes actionnables. Pas de synchronisation bancaire supposée.

## Sécurité et déploiement
Authentification serveur dédiée, contrôle d'autorisation sur chaque API, stockage privé séparé du journal, protection CSRF, journalisation sans secrets, sauvegarde et restauration testées. Ne jamais publier de données réelles dans les assets statiques. Vérifier le backend CRM et son export avant migration. Tests de non-régression du site et de l'espace client, accès anonyme refusé, tests de rapprochement et validation documentaire. Déployer en préproduction puis production seulement après vérification des accès, des tests et du plan de retour arrière. Le prototype HTML actuel n'est pas un CRM opérationnel.
