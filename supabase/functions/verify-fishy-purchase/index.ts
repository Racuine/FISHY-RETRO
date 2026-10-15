import { createClient } from 'npm:@supabase/supabase-js@2';
import { SignJWT, importPKCS8 } from 'npm:jose@5';
const ids=new Set(['fishy_bronze','fishy_silver','fishy_gold','fishy_platinum','fishy_emerald','fishy_ruby','fishy_sapphire','fishy_amethyst','fishy_diamond','fishy_black_diamond']);
function response(body:unknown,status=200){return new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json'}})}
Deno.serve(async req=>{
 if(req.method!=='POST')return response({error:'Method not allowed'},405);
 try{
  const jwt=req.headers.get('Authorization')?.replace(/^Bearer /,'');if(!jwt)return response({error:'Connexion requise'},401);
  const url=Deno.env.get('SUPABASE_URL')!,anon=Deno.env.get('SUPABASE_ANON_KEY')!,service=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
  const auth=createClient(url,anon);const {data:{user},error:userError}=await auth.auth.getUser(jwt);
  if(userError||!user)return response({error:'Session invalide'},401);
  const {productId,purchaseToken}=await req.json();
  if(typeof productId!=='string'||!ids.has(productId)||typeof purchaseToken!=='string'||purchaseToken.length<12||purchaseToken.length>4096)return response({error:'Produit ou reçu invalide'},400);
  const pkg=Deno.env.get('GOOGLE_PLAY_PACKAGE_NAME')||'com.fishyretro.game';
  const account=JSON.parse(Deno.env.get('GOOGLE_PLAY_SERVICE_ACCOUNT_JSON')||'{}');
  if(!account.client_email||!account.private_key)throw Error('Service account not configured');
  const key=await importPKCS8(account.private_key,'RS256');const now=Math.floor(Date.now()/1000);
  const assertion=await new SignJWT({scope:'https://www.googleapis.com/auth/androidpublisher'}).setProtectedHeader({alg:'RS256'}).setIssuer(account.client_email).setAudience('https://oauth2.googleapis.com/token').setIssuedAt(now).setExpirationTime(now+3600).sign(key);
  const tokenResp=await fetch('https://oauth2.googleapis.com/token',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({grant_type:'urn:ietf:params:oauth:grant-type:jwt-bearer',assertion})});
  if(!tokenResp.ok)throw Error('Google API credentials rejected');const token=(await tokenResp.json()).access_token;
  const api=`https://androidpublisher.googleapis.com/androidpublisher/v3/applications/${encodeURIComponent(pkg)}/purchases/products/${encodeURIComponent(productId)}/tokens/${encodeURIComponent(purchaseToken)}`;
  const google=await fetch(api,{headers:{Authorization:`Bearer ${token}`}});
  if(!google.ok)return response({error:'Achat non reconnu par Google Play'},403);
  const purchase=await google.json();
  if(purchase.purchaseState!==0||purchase.consumptionState!==0)return response({error:'Paiement non finalisé ou déjà consommé'},409);
  const admin=createClient(url,service);
  const {error:grantError}=await admin.rpc('fishy_grant_premium',{p_user_id:user.id,p_product_id:productId,p_purchase_token:purchaseToken});
  if(grantError)return response({error:'Impossible d’attribuer le skin : '+grantError.message},409);
  if(purchase.acknowledgementState===0){
   const ack=await fetch(api+':acknowledge',{method:'POST',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},body:'{}'});
   if(!ack.ok)return response({error:'Skin attribué, confirmation Google en attente : relancer Restaurer mes achats'},503);
  }
  return response({ok:true,productId});
 }catch(e){console.error('verify purchase',e);return response({error:'Vérification indisponible. Réessaie via Restaurer mes achats.'},500)}
});
