-- ════════════════════════════════════════════════════════════
-- Alushe Store — Módulo de inventario (stock + bitácora de movimientos)
-- Córrelo UNA vez en: Supabase → SQL Editor → New query → Run
-- ════════════════════════════════════════════════════════════

-- 1) Columnas de inventario en productos
alter table public.productos
  add column if not exists stock         int           not null default 0,
  add column if not exists stock_minimo  int           not null default 0,
  add column if not exists costo         numeric(10,2);

-- 2) Bitácora de movimientos (ledger)
create table if not exists public.movimientos_inventario (
  id             bigint generated always as identity primary key,
  producto_id    bigint not null references public.productos(id) on delete cascade,
  tipo           text   not null check (tipo in ('entrada','salida','ajuste')),
  cantidad       int    not null,          -- piezas movidas (o stock final si tipo='ajuste')
  stock_anterior int    not null,
  stock_nuevo    int    not null,
  motivo         text,
  usuario        text,
  creado         timestamptz not null default now()
);
create index if not exists idx_mov_producto on public.movimientos_inventario(producto_id, creado desc);

-- 3) Función atómica: registra el movimiento y ajusta el stock en una sola transacción.
--    Es el punto de integración con la app: cualquier cliente llama esta función
--    y el stock queda consistente, con bitácora y sin condiciones de carrera.
create or replace function public.registrar_movimiento(
  p_producto_id bigint,
  p_tipo        text,
  p_cantidad    int,
  p_motivo      text default null
) returns int
language plpgsql
security definer
set search_path = public
as $$
declare
  v_actual int;
  v_nuevo  int;
  v_user   text;
begin
  select stock into v_actual from productos where id = p_producto_id for update;
  if not found then
    raise exception 'Producto % no existe', p_producto_id;
  end if;

  v_nuevo := case p_tipo
    when 'entrada' then v_actual + abs(p_cantidad)
    when 'salida'  then v_actual - abs(p_cantidad)
    when 'ajuste'  then p_cantidad
    else v_actual
  end;

  if v_nuevo < 0 then
    raise exception 'Stock insuficiente (actual %, salida %)', v_actual, abs(p_cantidad);
  end if;

  v_user := coalesce((auth.jwt() ->> 'email'), 'sistema');

  update productos set stock = v_nuevo, actualizado = now() where id = p_producto_id;

  insert into movimientos_inventario
    (producto_id, tipo, cantidad, stock_anterior, stock_nuevo, motivo, usuario)
  values
    (p_producto_id, p_tipo, p_cantidad, v_actual, v_nuevo, p_motivo, v_user);

  return v_nuevo;
end
$$;

-- 4) Seguridad: la bitácora se lee autenticado; la función solo la ejecuta un usuario autenticado
alter table public.movimientos_inventario enable row level security;

drop policy if exists "mov lectura autenticada" on public.movimientos_inventario;
create policy "mov lectura autenticada"
  on public.movimientos_inventario for select to authenticated using (true);

revoke all on function public.registrar_movimiento(bigint,text,int,text) from public, anon;
grant execute on function public.registrar_movimiento(bigint,text,int,text) to authenticated;

-- 5) Realtime para que el admin (y la app) se actualicen solos
alter publication supabase_realtime add table public.movimientos_inventario;

-- Prueba rápida (reemplaza 1 por un id real de productos):
--   select public.registrar_movimiento(1,'entrada',5,'inventario inicial');
--   select stock from public.productos where id = 1;   -- debe ser 5
