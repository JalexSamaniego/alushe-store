-- ════════════════════════════════════════════════════════════
-- Alushe Store — Tabla de Puntos de Entrega (Supabase)
-- Córrelo UNA vez en: Supabase → SQL Editor → New query → Run
-- Deja el admin y la página pública sincronizados en tiempo real.
-- ════════════════════════════════════════════════════════════

-- 1) Tabla
create table if not exists public.puntos_entrega (
  id          text primary key,
  nombre      text not null,
  hora        text not null,
  maps_url    text,
  ref_img     text,
  croquis_img text,
  orden       int  not null default 0,
  activo      boolean not null default true,
  creado      timestamptz not null default now()
);

-- 2) Seguridad: lectura pública, escritura solo autenticada (igual que productos/banners)
alter table public.puntos_entrega enable row level security;

drop policy if exists "puntos lectura publica"     on public.puntos_entrega;
drop policy if exists "puntos escritura autenticada" on public.puntos_entrega;

create policy "puntos lectura publica"
  on public.puntos_entrega for select using (true);

create policy "puntos escritura autenticada"
  on public.puntos_entrega for all to authenticated
  using (true) with check (true);

-- 3) Realtime (para que la página pública y el admin se actualicen solos)
alter publication supabase_realtime add table public.puntos_entrega;

-- 4) Datos iniciales — los 10 puntos actuales, con sus imágenes ya existentes en GitHub.
--    upsert: si vuelves a correrlo no duplica.
insert into public.puntos_entrega (id, nombre, hora, maps_url, ref_img, croquis_img, orden) values
  ('guadalajara_factor',   '"Guadalajara" Factor',            '4:00 pm', 'https://maps.app.goo.gl/S5Rf4VzhrjDkAnDe6', 'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/referencia/guadalajara_factor.jpg',   'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/croquis/guadalajara_factor.png',   1),
  ('catedral',             'Zona Centro "Catedral"',          '4:30 pm', 'https://maps.app.goo.gl/99kjyTA6yEKn3c737', 'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/referencia/catedral.jpg',             'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/croquis/catedral.png',             2),
  ('santuario_libro',      'Santuario "Libro"',               '5:00 pm', 'https://maps.app.goo.gl/c6xkrWRUiBZtoHgaA', 'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/referencia/santuario_libro.jpg',      'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/croquis/santuario_libro.png',      3),
  ('plaza_galas',          'Plaza Galas "Office Depot"',      '5:30 pm', 'https://maps.app.goo.gl/1kfNca72vWncHhm48', 'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/referencia/plaza_galas.jpg',          'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/croquis/plaza_galas.png',          4),
  ('oxxo_luz_esperanza',   '"Oxxo" Luz y Esperanza',          '5:30 pm', 'https://maps.app.goo.gl/BqtiNzuEhs1AGMqa6', 'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/referencia/oxxo_luz_esperanza.jpg',   'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/croquis/oxxo_luz_esperanza.png',   5),
  ('oxxo_morga',           '"Oxxo" Morga',                    '6:00 pm', 'https://maps.app.goo.gl/zcHsmC8ZJMC4Njs47', 'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/referencia/oxxo_morga.jpg',           'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/croquis/oxxo_morga.png',           6),
  ('guadalajara_puentes',  '"Guadalajara" Puentes Gemelos',   '6:30 pm', 'https://maps.app.goo.gl/9EDMhMzFvNnot8116', 'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/referencia/guadalajara_puentes.jpg',  'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/croquis/guadalajara_puentes.png',  7),
  ('alsuper_ojo_agua',     '"Alsúper" Ojo de Agua',           '7:00 pm', 'https://maps.app.goo.gl/j5kWsf4Qyo88yV6T6', 'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/referencia/alsuper_ojo_agua.jpg',     'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/croquis/alsuper_ojo_agua.png',     8),
  ('oxxo_santa_maria',     '"Oxxo" Santa María',              '7:30 pm', 'https://maps.app.goo.gl/2es8XfLCFhMnxpvx9', 'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/referencia/oxxo_santa_maria.jpg',     'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/croquis/oxxo_santa_maria.png',     9),
  ('oxxo_zacatecas',       '"Oxxo" Calle Zacatecas',          '8:00 pm', 'https://maps.app.goo.gl/RTqGAe8Y6gtEfvD97', 'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/referencia/oxxo_zacatecas.jpg',       'https://raw.githubusercontent.com/JalexSamaniego/alushe-store/master/assets/images/croquis/oxxo_zacatecas.png',       10)
on conflict (id) do update set
  nombre = excluded.nombre, hora = excluded.hora, maps_url = excluded.maps_url,
  ref_img = excluded.ref_img, croquis_img = excluded.croquis_img, orden = excluded.orden;

-- Listo. Verifica con:  select * from public.puntos_entrega order by orden;
