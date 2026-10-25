-- ════════════════════════════════════════════════════════════
-- Valores por defecto de inventario:
--   • Stock MÍNIMO 1 a todos los que estén por debajo (con bitácora).
--   • Costo = $1 a todos los que no tengan costo (lo irás ajustando tú).
-- Córrelo UNA vez en: Supabase → SQL Editor → Run
-- ════════════════════════════════════════════════════════════

-- 1) Stock mínimo 1 (deja el movimiento en el historial)
with ajustados as (
  update public.productos
     set stock = 1, actualizado = now()
   where stock < 1
  returning id
)
insert into public.movimientos_inventario
  (producto_id, tipo, cantidad, stock_anterior, stock_nuevo, motivo, usuario)
select id, 'ajuste', 1, 0, 1, 'stock inicial masivo', 'sistema'
from ajustados;

-- 2) Costo $1 por defecto donde falte
update public.productos
   set costo = 1, actualizado = now()
 where costo is null;

-- Verifica:
--   select count(*) filter (where stock < 1) as sin_stock,
--          count(*) filter (where costo is null) as sin_costo
--   from public.productos;   -- ambos deben ser 0
