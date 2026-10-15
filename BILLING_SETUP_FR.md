# FISHY! RETRO — Google Play Billing (préparation)

## Prérequis
- Publier une version de test interne dans Google Play Console avec **le même applicationId** `com.fishyretro.game` et une signature Play App Signing correctement configurée.
- Créer 10 produits **achat unique / in-app** avec les identifiants exacts : `fishy_bronze`, `fishy_silver`, `fishy_gold`, `fishy_platinum`, `fishy_emerald`, `fishy_ruby`, `fishy_sapphire`, `fishy_amethyst`, `fishy_diamond`, `fishy_black_diamond`.
- Configurer les prix en euros dans Play Console. Les prix du HTML sont des prix indicatifs : le paiement réel utilise le prix configuré sur Google Play.
- Ajouter les comptes testeurs (test interne + testeurs de licence). Un APK debug installé hors Google Play peut ne pas permettre les achats.
- Activer Google Play Developer API dans Google Cloud et accorder au compte de service l'accès requis aux commandes/achats dans Play Console.

## Supabase
1. Exécuter `supabase_premium_billing.sql` après les SQL V5/V6/V7 déjà installés.
2. Déployer `supabase/functions/verify-fishy-purchase/index.ts` avec Supabase CLI : `supabase functions deploy verify-fishy-purchase`.
3. Configurer les secrets : `GOOGLE_PLAY_PACKAGE_NAME=com.fishyretro.game` et `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` (JSON complet du compte de service). Ne jamais placer cette clé dans `www/config.js`, GitHub ou le ZIP public.
4. La fonction utilise les secrets Supabase préexistants `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`.
5. Tester les achats et `RESTAURER MES ACHATS` sur une installation de test Google Play.

## Sécurité / limites
- Le jeton d'achat est vérifié par Google côté Edge Function; seul le rôle `service_role` peut attribuer les skins premium.
- Les achats sont liés au compte FISHY connecté. Pour éviter les pertes, se connecter au **même compte FISHY** lors de la restauration.
- Un achat effectué mais pas encore confirmé peut être restauré via le bouton boutique.
- Les notifications Google Play Real-time Developer Notifications (RTDN) et le traitement des remboursements/révocations **ne sont pas encore intégrés** : nécessaires avant ouverture publique, pour retirer les droits remboursés.
- Le projet n'a pas été compilé/testé ici sur Play Console; tester d'abord en piste interne.
- Ne pas envoyer la clé du compte de service dans une conversation ou un dépôt.
