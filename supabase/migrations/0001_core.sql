-- 0001_core.sql · Growth Ops Lab core tables
-- Run once in Supabase → SQL Editor. Safe to re-run (uses IF NOT EXISTS).

create extension if not exists pgcrypto;  -- gen_random_uuid() (already on in Supabase)

-- ---------------------------------------------------------------
-- leads: every inbound lead from any project
-- ---------------------------------------------------------------
create table if not exists public.leads (
  id                  uuid primary key default gen_random_uuid(),
  created_at          timestamptz not null default now(),
  source              text,
  email               text,
  first_name          text,
  last_name           text,
  company             text,
  company_size        text,
  role                text,
  use_case            text,
  timeline            text,
  utm_source          text,
  utm_medium          text,
  utm_campaign        text,
  gclid               text,
  fbclid              text,
  page_url            text,
  score               int,
  tier                text check (tier in ('A','B','C','unscored')),
  reason              text,
  scored_by           text,
  hubspot_contact_id  text,
  status              text default 'new',
  is_demo             boolean default true
);

-- One live row per email (case-insensitive). Rows marked 'duplicate' are exempt,
-- so the edge function can upsert by email.
create unique index if not exists leads_email_unique
  on public.leads (lower(email))
  where status <> 'duplicate';

-- ---------------------------------------------------------------
-- events_log: what every script / function did, for debugging
-- ---------------------------------------------------------------
create table if not exists public.events_log (
  id          bigserial primary key,
  created_at  timestamptz not null default now(),
  project     text,
  event       text,
  ok          boolean,
  payload     jsonb
);

create index if not exists events_log_created_at_idx on public.events_log (created_at desc);

-- ---------------------------------------------------------------
-- Security: RLS on, and NO policies for anon/authenticated.
-- Only the service_role (secret) key can read or write these tables.
-- ---------------------------------------------------------------
alter table public.leads      enable row level security;
alter table public.events_log enable row level security;
