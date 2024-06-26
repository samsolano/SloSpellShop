create table
  public.potions (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    name text null,
    red bigint null,
    green bigint null,
    blue bigint null,
    dark bigint null,
    quantity bigint null,
    constraint potions_pkey primary key (id)
  ) tablespace pg_default;