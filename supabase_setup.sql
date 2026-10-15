-- FISHY! RETRO V8 — run in Supabase SQL Editor once.
-- User identity is auth.users; only public profile data is readable.
create table if not exists public.profiles (
 id uuid primary key references auth.users(id) on delete cascade,
 username text not null,
 country text not null,
 best_score integer not null default 0 check (best_score >= 0),
 created_at timestamptz not null default now(),
 constraint fishy_username_format check (username ~ '^[A-Za-z0-9_]{3,16}$'),
 constraint fishy_country_format check (country ~ '^[A-Z]{2}$')
);
create unique index if not exists fishy_username_unique_ci on public.profiles(lower(username));
create index if not exists fishy_world_rank on public.profiles(best_score desc, created_at asc);
create index if not exists fishy_country_rank on public.profiles(country, best_score desc, created_at asc);
alter table public.profiles enable row level security;
revoke all on public.profiles from anon, authenticated;
grant select on public.profiles to authenticated;
drop policy if exists fishy_public_profiles on public.profiles;
create policy fishy_public_profiles on public.profiles for select to authenticated using (true);

-- Country and username are immutable because clients have no table UPDATE privilege.
create or replace function public.create_fishy_profile(p_username text, p_country text)
returns void language plpgsql security definer set search_path = '' as $$
begin
 if auth.uid() is null then raise exception 'Connexion requise'; end if;
 if p_username !~ '^[A-Za-z0-9_]{3,16}$' then raise exception 'Pseudo invalide'; end if;
 if p_country !~ '^[A-Z]{2}$' then raise exception 'Pays invalide'; end if;
 if p_country not in ('AF','ZA','AL','DZ','DE','AD','AO','AI','AQ','AG','SA','AR','AM','AW','AU','AT','AZ','BS','BH','BD','BB','BE','BZ','BM','BT','BY','BO','BA','BW','BN','BR','BG','BF','BI','BJ','KH','CM','CA','CV','CL','CN','CY','CO','KM','CG','CD','KP','KR','CR','HR','CU','CW','CI','DK','DJ','DM','ES','EE','SZ','FJ','FI','FR','GA','GM','GH','GI','GD','GL','GR','GP','GU','GT','GG','GN','GQ','GW','GY','GF','GE','GS','HT','HN','HU','IN','ID','IQ','IR','IE','IS','IL','IT','JM','JP','JE','JO','KZ','KE','KG','KI','KW','RE','LA','LS','LV','LB','LR','LY','LI','LT','LU','MK','MG','MY','MW','MV','ML','MT','MA','MQ','MU','MR','YT','MX','FM','MD','MC','MN','MS','ME','MZ','MM','NA','NR','NI','NE','NG','NU','NO','NC','NZ','NP','OM','UG','UZ','PK','PW','PA','PG','PY','NL','BQ','PH','PL','PF','PR','PT','PE','QA','HK','MO','RO','GB','RU','RW','CF','DO','EH','BL','KN','SM','MF','SX','PM','VC','SH','LC','SV','WS','AS','ST','RS','SC','SL','SG','SK','SI','SO','SD','SS','LK','CH','SR','SE','SJ','SY','SN','TJ','TZ','TW','TD','CZ','TF','IO','PS','TH','TL','TG','TK','TO','TT','TN','TM','TR','TV','UA','UY','VU','VE','VN','WF','YE','ZM','ZW','EG','AE','EC','ER','VA','US','ET','BV','CX','IM','NF','KY','CC','CK','FO','HM','FK','MP','MH','UM','PN','SB','TC','VG','VI','AX') then raise exception 'Pays non pris en charge'; end if;
 insert into public.profiles(id,username,country) values (auth.uid(),p_username,p_country);
end; $$;
revoke all on function public.create_fishy_profile(text,text) from public;
grant execute on function public.create_fishy_profile(text,text) to authenticated;

-- Only improves a personal best. Important: score values are still client-reported,
-- so this is NOT cheat-proof; server-side game validation is required for competitive play.
create or replace function public.submit_fishy_score(p_score integer)
returns void language plpgsql security definer set search_path = '' as $$
begin
 if auth.uid() is null then raise exception 'Connexion requise'; end if;
 if p_score is null or p_score < 0 or p_score > 1000000 then raise exception 'Score invalide'; end if;
 update public.profiles set best_score=greatest(best_score,p_score) where id=auth.uid();
 if not found then raise exception 'Profil requis'; end if;
end; $$;
revoke all on function public.submit_fishy_score(integer) from public;
grant execute on function public.submit_fishy_score(integer) to authenticated;

-- Deterministic ranking: highest score first, oldest profile first on ties.
create or replace function public.fishy_leaderboard(p_country text default null, p_limit integer default 100)
returns table("position" bigint,username text,country text,best_score integer)
language sql stable security definer set search_path = '' as $$
 select row_number() over (order by p.best_score desc,p.created_at asc,p.id asc) as "position",
 p.username,p.country,p.best_score
 from public.profiles p
 where p.best_score > 0 and (p_country is null or p.country=p_country)
 order by "position" limit least(greatest(coalesce(p_limit,100),1),100);
$$;
revoke all on function public.fishy_leaderboard(text,integer) from public;
grant execute on function public.fishy_leaderboard(text,integer) to authenticated;

create or replace function public.fishy_my_rank(p_country text default null)
returns table("position" bigint) language sql stable security definer set search_path = '' as $$
 select ranked."position" from (
  select p.id,row_number() over(order by p.best_score desc,p.created_at asc,p.id asc) "position"
  from public.profiles p where p.best_score>0 and (p_country is null or p.country=p_country)
 ) ranked where ranked.id=auth.uid();
$$;
revoke all on function public.fishy_my_rank(text) from public;
grant execute on function public.fishy_my_rank(text) to authenticated;
