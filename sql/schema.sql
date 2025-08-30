SET search_path TO public;

CREATE TABLE IF NOT EXISTS public.datacenter
(
  id SERIAL PRIMARY KEY,
  name varchar(255) NOT NULL,
  created_at timestamp DEFAULT (now() AT TIME ZONE 'UTC'::text) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.switch
(
  id serial PRIMARY KEY,
  name varchar(255) NOT NULL,
  vlans integer[] DEFAULT ARRAY[]::integer[] NOT NULL,
  created_at timestamp DEFAULT (now() AT TIME ZONE 'UTC'::text) NOT NULL,
  modified_at timestamp DEFAULT (now() AT TIME ZONE 'UTC'::text) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.server
(
  id serial PRIMARY KEY,
  hostname varchar(255) NOT NULL,
  configuration jsonb DEFAULT '{}'::jsonb NOT NULL,
  datacenter_id integer NOT NULL REFERENCES public.datacenter,
  created_at timestamp DEFAULT (now() AT TIME ZONE 'UTC'::text) NOT NULL,
  modified_at timestamp DEFAULT (now() AT TIME ZONE 'UTC'::text) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.switch_to_server
(
  switch_id integer NOT NULL REFERENCES public.switch,
  server_id integer NOT NULL REFERENCES public.server,
  PRIMARY KEY (switch_id, server_id)
);
