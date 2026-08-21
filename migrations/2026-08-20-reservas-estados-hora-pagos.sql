-- Migración de usr_app.reservas: estados, hora y cobro.
--
-- El proyecto no tiene herramienta de migraciones: el seed de
-- docker-entrypoint-initdb.d sólo corre sobre un volumen nuevo, así que en
-- cualquier entorno con datos hay que aplicar este archivo a mano.
--
-- Es idempotente: se puede ejecutar varias veces sin romper nada.
--
--   docker compose exec -T db psql -U postgres -d reservat \
--     -v ON_ERROR_STOP=1 -f - < migrations/2026-08-20-reservas-estados-hora-pagos.sql
--
-- Antes de correrlo conviene tener una copia: ./backup-db.sh

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Decisión del administrador
-- ---------------------------------------------------------------------
ALTER TABLE usr_app.reservas
    ADD COLUMN IF NOT EXISTS motivo_rechazo text,
    ADD COLUMN IF NOT EXISTS fecha_decision timestamp with time zone,
    ADD COLUMN IF NOT EXISTS id_admin_decision uuid;

-- Las reservas anteriores a la máquina de estados pueden tener el estado
-- vacío o con valores viejos ('confirmada', 'cancelada'). Se normalizan
-- antes de imponer la restricción, o el ALTER falla.
UPDATE usr_app.reservas SET estado = 'pendiente'
 WHERE estado IS NULL OR btrim(estado) = '';

UPDATE usr_app.reservas SET estado = 'aprobada'
 WHERE lower(estado) IN ('confirmada', 'confirmado', 'completada', 'completado');

UPDATE usr_app.reservas SET estado = 'rechazada'
 WHERE lower(estado) IN ('cancelada', 'cancelado');

-- Cualquier otro valor inesperado vuelve a 'pendiente': es el único estado
-- desde el que un administrador puede decidir, así que no se pierde nada.
UPDATE usr_app.reservas SET estado = 'pendiente'
 WHERE estado NOT IN ('pendiente', 'aprobada', 'rechazada');

ALTER TABLE usr_app.reservas ALTER COLUMN estado SET DEFAULT 'pendiente';
ALTER TABLE usr_app.reservas ALTER COLUMN estado SET NOT NULL;

ALTER TABLE usr_app.reservas DROP CONSTRAINT IF EXISTS reservas_estado_check;
ALTER TABLE usr_app.reservas ADD CONSTRAINT reservas_estado_check
    CHECK (estado IN ('pendiente', 'aprobada', 'rechazada'));

-- Un rechazo sin motivo no sirve: ese texto es el que se le envía al
-- mayorista y al proveedor.
UPDATE usr_app.reservas
   SET motivo_rechazo = 'No se registró un motivo.'
 WHERE estado = 'rechazada' AND motivo_rechazo IS NULL;

ALTER TABLE usr_app.reservas DROP CONSTRAINT IF EXISTS reservas_motivo_rechazo_check;
ALTER TABLE usr_app.reservas ADD CONSTRAINT reservas_motivo_rechazo_check
    CHECK (estado <> 'rechazada' OR motivo_rechazo IS NOT NULL);

-- ---------------------------------------------------------------------
-- 2. Hora reservada
-- ---------------------------------------------------------------------
-- Sólo aplica a experiencias y restaurantes; el alojamiento se define por
-- su rango de fechas.
ALTER TABLE usr_app.reservas
    ADD COLUMN IF NOT EXISTS hora time without time zone;

-- ---------------------------------------------------------------------
-- 3. Cobro
-- ---------------------------------------------------------------------
ALTER TABLE usr_app.reservas
    ADD COLUMN IF NOT EXISTS estado_pago text NOT NULL DEFAULT 'no_aplica',
    ADD COLUMN IF NOT EXISTS pago_link_id text,
    ADD COLUMN IF NOT EXISTS pago_link_url text,
    ADD COLUMN IF NOT EXISTS pago_transaccion_id text,
    ADD COLUMN IF NOT EXISTS pago_metodo text,
    ADD COLUMN IF NOT EXISTS fecha_pago timestamp with time zone;

ALTER TABLE usr_app.reservas DROP CONSTRAINT IF EXISTS reservas_estado_pago_check;
ALTER TABLE usr_app.reservas ADD CONSTRAINT reservas_estado_pago_check
    CHECK (estado_pago IN ('no_aplica', 'pendiente', 'aprobado', 'rechazado', 'error'));

-- El webhook busca la reserva por el identificador del enlace de pago.
CREATE INDEX IF NOT EXISTS idx_reservas_pago_link_id
    ON usr_app.reservas (pago_link_id)
    WHERE pago_link_id IS NOT NULL;

-- El dashboard filtra por estado constantemente.
CREATE INDEX IF NOT EXISTS idx_reservas_estado
    ON usr_app.reservas (estado);

COMMIT;

-- ---------------------------------------------------------------------
-- Verificación
-- ---------------------------------------------------------------------
-- Todas las columnas deben aparecer y el reparto de estados debe cuadrar
-- con lo que había antes.
SELECT column_name, data_type, is_nullable
  FROM information_schema.columns
 WHERE table_schema = 'usr_app' AND table_name = 'reservas'
   AND column_name IN ('estado', 'motivo_rechazo', 'fecha_decision',
                       'id_admin_decision', 'hora', 'estado_pago',
                       'pago_link_id', 'pago_link_url',
                       'pago_transaccion_id', 'pago_metodo', 'fecha_pago')
 ORDER BY column_name;

SELECT estado, estado_pago, count(*) AS reservas
  FROM usr_app.reservas
 GROUP BY estado, estado_pago
 ORDER BY estado, estado_pago;
