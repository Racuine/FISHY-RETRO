-- Run after your V7 security and shop SQL. Does not modify coin balances.
create table if not exists public.fishy_premium_purchases (
 purchase_token text primary key,
 user_id uuid not null references auth.users(id) on delete cascade,
 product_id text not null,
 skin_id integer not null check (skin_id between 20 and 29),
 purchased_at timestamptz not null default now()
);
create unique index if not exists fishy_premium_user_skin on public.fishy_premium_purchases(user_id,skin_id);
alter table public.fishy_premium_purchases enable row level security;
revoke all on public.fishy_premium_purchases from anon, authenticated;
-- Only the Edge Function service_role may insert verified purchases.
create or replace function public.fishy_grant_premium(p_user_id uuid,p_product_id text,p_purchase_token text)
returns void language plpgsql security definer set search_path=public as $$
declare v_skin integer;
begin
 v_skin:=case p_product_id
 when 'fishy_bronze' then 20 when 'fishy_silver' then 21 when 'fishy_gold' then 22
 when 'fishy_platinum' then 23 when 'fishy_emerald' then 24 when 'fishy_ruby' then 25
 when 'fishy_sapphire' then 26 when 'fishy_amethyst' then 27 when 'fishy_diamond' then 28
 when 'fishy_black_diamond' then 29 else null end;
 if v_skin is null then raise exception 'Invalid product';end if;
 if exists(select 1 from public.fishy_premium_purchases where purchase_token=p_purchase_token and user_id<>p_user_id) then raise exception 'Token belongs to another user';end if;
 insert into public.fishy_premium_purchases(purchase_token,user_id,product_id,skin_id)
 values(p_purchase_token,p_user_id,p_product_id,v_skin)
 on conflict do nothing;
 if not exists(select 1 from public.fishy_premium_purchases where purchase_token=p_purchase_token and user_id=p_user_id and product_id=p_product_id) then raise exception 'Purchase already linked or invalid';end if;
end $$;
revoke all on function public.fishy_grant_premium(uuid,text,text) from public,anon,authenticated;
grant execute on function public.fishy_grant_premium(uuid,text,text) to service_role;
-- Extend the existing RPC used by the shop. SECURITY DEFINER needed because purchase rows have no user RLS access.
create or replace function public.fishy_premium_owned()
returns table(skin_id integer) language sql stable security definer set search_path=public as $$
 select p.skin_id from public.fishy_premium_purchases p where p.user_id=auth.uid()
$$;
revoke all on function public.fishy_premium_owned() from public,anon;
grant execute on function public.fishy_premium_owned() to authenticated;
