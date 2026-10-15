# FISHY! RETRO V8 — Classement mondial et par pays

## Ce qui est livré
- Jeu V7 conservé, menu CLASSEMENT ajouté (accueil + fin de partie).
- Authentification Supabase par **code e-mail (OTP)** et **Google OAuth**.
- Pseudo unique insensible à la casse (3–16 caractères ASCII lettres/chiffres/underscore).
- Pays définitif après création du profil (249 pays et territoires ISO 3166-1 alpha-2).
- Top 100 mondial, Top 100 national, position personnelle et score synchronisé en fin de partie.
- Profil récupérable après réinstallation en se reconnectant avec le **même compte**.
- Si Supabase n'est pas configuré, le jeu local continue à fonctionner ; le classement explique la configuration manquante.

## Installation Supabase (ordre important)
1. Créer un projet sur https://supabase.com/dashboard .
2. Dans **SQL Editor**, exécuter entièrement `supabase_setup.sql`.
3. Dans **Authentication > Providers > Email**, activer Email et OTP. Pour utiliser le champ code à 6 chiffres, adapter le modèle d'e-mail Magic Link pour inclure `{{ .Token }}`. Sans cela, l'e-mail peut ne proposer qu'un lien.
4. Dans **Authentication > Providers > Google**, activer Google et renseigner **Client ID** et **Client Secret** d'un client OAuth Google *Web application*. Dans Google Cloud Console, configurer l'URI de redirection autorisée fourni par Supabase : `https://TON-PROJET.supabase.co/auth/v1/callback`. La configuration de l'écran de consentement Google est aussi nécessaire.
5. Dans **Authentication > URL Configuration > Redirect URLs**, ajouter **`com.fishyretro.game://auth/callback`** (Android) et les URL HTTPS exactes de ton éventuel hébergement web. Pour tester la connexion Google depuis un navigateur, il faut servir le HTML via HTTP(S), pas ouvrir le fichier `file://`.
6. Dans **Project Settings > API Keys**, copier la **Project URL** et la clé **publishable** (ou `anon` publique). Les renseigner dans `www/config.js`. **Ne jamais mettre `service_role` ou `secret` dans le client.**
7. Recréer l'APK via le workflow GitHub Actions (la dépendance Capacitor Browser/App et le deep link sont inclus).
8. Tester avec deux comptes et deux appareils : unicité du pseudo (y compris majuscules/minuscules), pays immuable, records, classement national et mondial, connexion Google et code e-mail, reconnexion après réinstallation.

## Notes importantes
- Le jeu reste jouable sans connexion, mais le classement nécessite Internet. Les scores ne sont envoyés que si le joueur est connecté au moment de la fin de partie. Un ancien meilleur score local **n'est pas automatiquement importé**, car le score ne serait pas vérifiable.
- Les scores sont envoyés par le client. Le SQL empêche de diminuer un record et interdit de modifier pseudo/pays, **mais ne protège pas contre les scores falsifiés**. Pour un classement compétitif, prévoir une validation serveur des parties et une protection anti-abus avant le lancement public.
- Le classement expose pseudo, pays et meilleur score aux autres joueurs connectés. Prévoir une politique de confidentialité, un moyen de supprimer son compte et un dispositif de modération des pseudos avant la publication.
- L'identité du compte est stockée dans l'authentification Supabase ; la connexion avec le même fournisseur et le même compte permet de récupérer son profil. Si une personne utilise Google et e-mail séparément, Supabase peut créer deux identités : prévoir un flux de liaison des identités pour les fusionner.
- Le pays est choisi manuellement et ne représente pas une vérification de localisation.
- Le fichier HTML seul nécessite `config.js` placé à côté pour le classement ; le jeu local fonctionne sans configuration.
