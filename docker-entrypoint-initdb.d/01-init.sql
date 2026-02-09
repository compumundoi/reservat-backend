-- Seeder script for Reservat Database
-- This script creates schema, tables, constraints and seeds initial data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema
CREATE SCHEMA IF NOT EXISTS usr_app;

-- Set search path
SET search_path TO usr_app, public;

-- ============================================
-- CREATE TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS usuarios (
    id uuid DEFAULT uuid_generate_v4() NOT NULL,
    nombre text NOT NULL,
    apellido text,
    email text NOT NULL,
    "contraseña" text NOT NULL,
    fecha_registro timestamp with time zone DEFAULT now(),
    ultimo_login timestamp with time zone,
    activo boolean DEFAULT true,
    tipo_usuario character varying
);

CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor uuid DEFAULT uuid_generate_v4() NOT NULL,
    tipo text NOT NULL,
    nombre text NOT NULL,
    descripcion text,
    email text NOT NULL,
    telefono text,
    direccion text,
    ciudad text,
    pais text,
    sitio_web text,
    rating_promedio numeric(3,2) DEFAULT 0.0,
    verificado boolean DEFAULT false,
    fecha_registro timestamp with time zone DEFAULT now(),
    ubicacion character varying,
    redes_sociales character varying,
    relevancia character varying,
    usuario_creador character varying,
    tipo_documento character varying,
    numero_documento character varying,
    activo boolean DEFAULT true,
    CONSTRAINT proveedores_tipo_check CHECK ((tipo = ANY (ARRAY['restaurante'::text, 'hotel'::text, 'tour'::text, 'transporte'::text])))
);

CREATE TABLE IF NOT EXISTS servicios (
    id_servicio uuid DEFAULT uuid_generate_v4() NOT NULL,
    proveedor_id uuid NOT NULL,
    nombre text NOT NULL,
    descripcion text,
    tipo_servicio text,
    precio numeric(10,2) NOT NULL,
    moneda text DEFAULT 'USD'::text,
    activo boolean DEFAULT true,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    relevancia character varying,
    ciudad character varying,
    departamento character varying,
    ubicacion character varying,
    detalles_del_servicio character varying
);

CREATE TABLE IF NOT EXISTS hoteles (
    id_hotel uuid NOT NULL,
    estrellas integer,
    numero_habitaciones integer,
    servicios_incluidos text,
    check_in time without time zone,
    check_out time without time zone,
    admite_mascotas boolean,
    tiene_estacionamiento boolean,
    tipo_habitacion text,
    precio_ascendente numeric(10,2),
    servicio_restaurante boolean DEFAULT false,
    recepcion_24_horas boolean DEFAULT false,
    bar boolean DEFAULT false,
    room_service boolean DEFAULT false,
    asensor boolean DEFAULT false,
    rampa_discapacitado boolean DEFAULT false,
    pet_friendly boolean DEFAULT false,
    auditorio boolean DEFAULT false,
    parqueadero boolean DEFAULT false,
    piscina boolean DEFAULT false,
    planta_energia boolean DEFAULT false,
    CONSTRAINT hoteles_estrellas_check CHECK (((estrellas >= 1) AND (estrellas <= 5)))
);

CREATE TABLE IF NOT EXISTS restaurantes (
    id_restaurante uuid NOT NULL,
    tipo_cocina text,
    horario_apertura time without time zone,
    horario_cierre time without time zone,
    capacidad integer,
    menu_url text,
    tiene_terraza boolean,
    apto_celiacos boolean,
    apto_vegetarianos boolean,
    reservas_requeridas boolean,
    entrega_a_domicilio boolean,
    wifi boolean DEFAULT false,
    zonas_comunes boolean DEFAULT false,
    auditorio boolean DEFAULT false,
    pet_friendly boolean DEFAULT false,
    eventos boolean DEFAULT false,
    menu_vegana boolean DEFAULT false,
    bufete boolean DEFAULT false,
    catering boolean DEFAULT false,
    menu_infantil boolean DEFAULT false,
    parqueadero boolean DEFAULT false,
    terraza boolean DEFAULT false,
    sillas_bebe boolean DEFAULT false,
    decoraciones_fechas_especiales boolean DEFAULT false,
    rampa_discapacitados boolean DEFAULT false,
    aforo_maximo integer,
    tipo_comida text,
    precio_ascendente numeric(10,2)
);

CREATE TABLE IF NOT EXISTS transportes (
    id_transporte uuid NOT NULL,
    tipo_vehiculo text NOT NULL,
    modelo text,
    anio integer,
    placa text,
    capacidad integer,
    aire_acondicionado boolean,
    wifi boolean,
    disponible boolean DEFAULT true,
    combustible text,
    seguro_vigente boolean DEFAULT true,
    fecha_mantenimiento timestamp with time zone,
    CONSTRAINT transportes_anio_check CHECK ((anio > 1980))
);

CREATE TABLE IF NOT EXISTS experiencias (
    id_experiencia uuid DEFAULT uuid_generate_v4() NOT NULL,
    duracion integer,
    dificultad text,
    idioma text,
    incluye_transporte boolean,
    grupo_maximo integer,
    guia_incluido boolean,
    equipamiento_requerido text,
    punto_de_encuentro text,
    numero_rnt text
);

CREATE TABLE IF NOT EXISTS fotos (
    id uuid DEFAULT uuid_generate_v4() NOT NULL,
    servicio_id uuid,
    url text NOT NULL,
    descripcion text,
    orden integer,
    es_portada boolean DEFAULT false,
    fecha_subida timestamp with time zone DEFAULT now(),
    eliminado boolean NOT NULL
);

CREATE TABLE IF NOT EXISTS rutas (
    id uuid DEFAULT uuid_generate_v4() NOT NULL,
    nombre text NOT NULL,
    descripcion text,
    puntos_interes text,
    recomendada boolean DEFAULT false,
    origen character varying,
    destino character varying,
    precio character varying,
    duracion_estimada integer,
    activo boolean DEFAULT true
);

CREATE TABLE IF NOT EXISTS viajes (
    id uuid DEFAULT uuid_generate_v4() NOT NULL,
    ruta_id uuid,
    fecha_inicio timestamp with time zone NOT NULL,
    fecha_fin timestamp with time zone NOT NULL,
    capacidad_total integer,
    capacidad_disponible integer,
    precio numeric(10,2),
    guia_asignado text,
    estado text DEFAULT 'programado'::text,
    id_transportador uuid NOT NULL,
    activo boolean DEFAULT true,
    CONSTRAINT viajes_estado_check CHECK ((estado = ANY (ARRAY['programado'::text, 'en_curso'::text, 'finalizado'::text, 'cancelado'::text])))
);

CREATE TABLE IF NOT EXISTS fechas_bloqueadas (
    id uuid DEFAULT uuid_generate_v4() NOT NULL,
    servicio_id uuid,
    fecha timestamp with time zone NOT NULL,
    motivo text,
    bloqueado_por text,
    bloqueo_activo boolean
);

CREATE TABLE IF NOT EXISTS mayoristas (
    id uuid NOT NULL,
    nombre text,
    apellidos text,
    descripcion text,
    email text,
    telefono text,
    direccion text,
    ciudad text,
    pais text,
    recurente boolean DEFAULT false,
    usuario_creador text,
    verificado boolean DEFAULT false,
    fecha_creacion timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    intereses text,
    tipo_documento character varying NOT NULL,
    numero_documento character varying NOT NULL,
    activo boolean DEFAULT true,
    fecha_actualizacion timestamp with time zone
);

CREATE TABLE IF NOT EXISTS reservas (
    id_reserva uuid NOT NULL,
    id_proveedor uuid,
    id_servicio uuid,
    id_mayorista uuid,
    nombre_servicio character varying,
    descripcion character varying,
    tipo_servicio character varying,
    precio character varying,
    ciudad character varying,
    activo character varying,
    estado character varying,
    observaciones character varying,
    fecha_creacion date,
    cantida integer
);

-- ============================================
-- PRIMARY KEYS AND UNIQUE CONSTRAINTS
-- ============================================

ALTER TABLE ONLY usuarios DROP CONSTRAINT IF EXISTS usuarios_pkey;
ALTER TABLE ONLY usuarios ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);

ALTER TABLE ONLY usuarios DROP CONSTRAINT IF EXISTS usuarios_email_key;
ALTER TABLE ONLY usuarios ADD CONSTRAINT usuarios_email_key UNIQUE (email);

ALTER TABLE ONLY proveedores DROP CONSTRAINT IF EXISTS proveedores_pkey;
ALTER TABLE ONLY proveedores ADD CONSTRAINT proveedores_pkey PRIMARY KEY (id_proveedor);

ALTER TABLE ONLY proveedores DROP CONSTRAINT IF EXISTS proveedores_email_key;
ALTER TABLE ONLY proveedores ADD CONSTRAINT proveedores_email_key UNIQUE (email);

ALTER TABLE ONLY servicios DROP CONSTRAINT IF EXISTS servicios_pkey;
ALTER TABLE ONLY servicios ADD CONSTRAINT servicios_pkey PRIMARY KEY (id_servicio);

ALTER TABLE ONLY hoteles DROP CONSTRAINT IF EXISTS hoteles_pkey;
ALTER TABLE ONLY hoteles ADD CONSTRAINT hoteles_pkey PRIMARY KEY (id_hotel);

ALTER TABLE ONLY restaurantes DROP CONSTRAINT IF EXISTS restaurantes_pkey;
ALTER TABLE ONLY restaurantes ADD CONSTRAINT restaurantes_pkey PRIMARY KEY (id_restaurante);

ALTER TABLE ONLY transportes DROP CONSTRAINT IF EXISTS transportes_pkey;
ALTER TABLE ONLY transportes ADD CONSTRAINT transportes_pkey PRIMARY KEY (id_transporte);

ALTER TABLE ONLY experiencias DROP CONSTRAINT IF EXISTS experiencias_pkey;
ALTER TABLE ONLY experiencias ADD CONSTRAINT experiencias_pkey PRIMARY KEY (id_experiencia);

ALTER TABLE ONLY fotos DROP CONSTRAINT IF EXISTS fotos_pkey;
ALTER TABLE ONLY fotos ADD CONSTRAINT fotos_pkey PRIMARY KEY (id);

ALTER TABLE ONLY rutas DROP CONSTRAINT IF EXISTS rutas_pkey;
ALTER TABLE ONLY rutas ADD CONSTRAINT rutas_pkey PRIMARY KEY (id);

ALTER TABLE ONLY viajes DROP CONSTRAINT IF EXISTS viajes_pkey;
ALTER TABLE ONLY viajes ADD CONSTRAINT viajes_pkey PRIMARY KEY (id);

ALTER TABLE ONLY fechas_bloqueadas DROP CONSTRAINT IF EXISTS fechas_bloqueadas_pkey;
ALTER TABLE ONLY fechas_bloqueadas ADD CONSTRAINT fechas_bloqueadas_pkey PRIMARY KEY (id);

ALTER TABLE ONLY reservas DROP CONSTRAINT IF EXISTS reservas_pkey;
ALTER TABLE ONLY reservas ADD CONSTRAINT reservas_pkey PRIMARY KEY (id_reserva);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_servicios_proveedor ON servicios USING btree (proveedor_id);
CREATE INDEX IF NOT EXISTS idx_fotos_servicio ON fotos USING btree (servicio_id);
CREATE INDEX IF NOT EXISTS idx_fechas_bloqueadas_servicio ON fechas_bloqueadas USING btree (servicio_id);

-- ============================================
-- FOREIGN KEYS
-- ============================================

ALTER TABLE ONLY servicios DROP CONSTRAINT IF EXISTS servicios_proveedor_id_fkey;
ALTER TABLE ONLY servicios ADD CONSTRAINT servicios_proveedor_id_fkey FOREIGN KEY (proveedor_id) REFERENCES proveedores(id_proveedor) ON DELETE CASCADE;

ALTER TABLE ONLY hoteles DROP CONSTRAINT IF EXISTS hoteles_id_fkey;
ALTER TABLE ONLY hoteles ADD CONSTRAINT hoteles_id_fkey FOREIGN KEY (id_hotel) REFERENCES proveedores(id_proveedor) ON DELETE CASCADE;

ALTER TABLE ONLY restaurantes DROP CONSTRAINT IF EXISTS restaurantes_id_fkey;
ALTER TABLE ONLY restaurantes ADD CONSTRAINT restaurantes_id_fkey FOREIGN KEY (id_restaurante) REFERENCES proveedores(id_proveedor) ON DELETE CASCADE;

ALTER TABLE ONLY transportes DROP CONSTRAINT IF EXISTS transportes_id_fkey;
ALTER TABLE ONLY transportes ADD CONSTRAINT transportes_id_fkey FOREIGN KEY (id_transporte) REFERENCES proveedores(id_proveedor) ON DELETE CASCADE;

ALTER TABLE ONLY experiencias DROP CONSTRAINT IF EXISTS experiencias_id_fkey;
ALTER TABLE ONLY experiencias ADD CONSTRAINT experiencias_id_fkey FOREIGN KEY (id_experiencia) REFERENCES proveedores(id_proveedor) ON DELETE CASCADE;

ALTER TABLE ONLY fotos DROP CONSTRAINT IF EXISTS fotos_servicio_id_fkey;
ALTER TABLE ONLY fotos ADD CONSTRAINT fotos_servicio_id_fkey FOREIGN KEY (servicio_id) REFERENCES servicios(id_servicio) ON DELETE CASCADE;

ALTER TABLE ONLY viajes DROP CONSTRAINT IF EXISTS viajes_ruta_id_fkey;
ALTER TABLE ONLY viajes ADD CONSTRAINT viajes_ruta_id_fkey FOREIGN KEY (ruta_id) REFERENCES rutas(id) ON DELETE CASCADE;

ALTER TABLE ONLY fechas_bloqueadas DROP CONSTRAINT IF EXISTS fechas_bloqueadas_servicio_id_fkey;
ALTER TABLE ONLY fechas_bloqueadas ADD CONSTRAINT fechas_bloqueadas_servicio_id_fkey FOREIGN KEY (servicio_id) REFERENCES servicios(id_servicio) ON DELETE CASCADE;

-- ============================================
-- SEED DATA - USUARIOS
-- ============================================

INSERT INTO usuarios (id, nombre, apellido, email, "contraseña", fecha_registro, ultimo_login, activo, tipo_usuario) VALUES
('f647ef5e-a997-452f-88b4-a49482fe1e63', 'Guillermo', 'Bedoya Ortega', 'guillermobedoya104@gmail.com', '$2b$12$aR1WovS5AiD3BYAPow7mP.FaMV6E4xt99CPRBdQx8ytjTNV8mNqyu', '2025-07-07 22:41:05.796699+00', '2025-07-31 00:16:04.792506+00', true, 'admin'),
('01a8ada7-5bd3-4cf2-b423-3b396f9725c2', 'Asesor', 'Agua de Río', 'asesor@aguaderio.com.co', '$2b$12$CUOxgRGj0YwmWgNA0Fgw4OBfTAOOtxlDIz4PfAaqREc28FBSD2f6y', '2025-07-29 04:32:16.270071+00', '2025-08-08 21:13:55.086621+00', true, 'proveedor'),
('25082cdb-48c1-4f14-aa4a-dcc05211e184', 'Asesor', 'hotelboutiquedonpepe', 'asesor@hotelboutiquedonpepe.com', '$2b$12$qPfxui2qqBz9gOenu6qBQexvTwKw7b15LmmpOGwXrSTgPreIkWzmm', '2025-07-29 04:08:43.254988+00', '2025-08-08 21:14:28.420519+00', true, 'proveedor'),
('335daa2b-5761-46b2-92f5-a65ffff03277', 'Luis gabriel', 'Quiceno espitia', 'quiceno@email.com', '$2b$12$zg9Di/Upb/mecp6UHXzhRuyh.MeHKg4PRqA1tbnuEwDMNUhc5Za1e', '2025-02-07 02:21:14.915+00', '2025-08-08 23:14:49.921259+00', true, 'admin'),
('bf005c77-72aa-4771-aed9-b35d46a56ef0', 'Asesor', 'Xperience', 'asesor@xperiences.com.co', '$2b$12$XGjXqr.rNFHiuw5SRP7Hpe53gZecFQ3FUSUFgYP61nzBi6vUVAisi', '2025-07-29 04:52:49.81493+00', '2025-08-08 23:16:06.903228+00', true, 'proveedor'),
('8140adb9-85ec-4817-b340-0213ec6e9de9', 'Asesor', 'marmi', 'asesor@marmi.com', '$2b$12$6GhqDVLHe2OKqtoJfpnWLOCCG74XjEpWAZ0KBnH/HnJf/2f2HeyY6', '2025-07-29 04:17:36.179405+00', '2025-07-29 05:58:41.528882+00', true, 'proveedor'),
('543d6f47-61cc-411f-90e9-da09cf470b87', 'mayorista', 'de prueba', 'mayorista@gmail.com', '$2b$12$Rs.bco4iZqiUbjV1ru5fteA7rnxaHE2kmewxOUJ6JepHjYCm7N1RK', '2025-07-29 05:47:15.665239+00', '2025-07-31 00:14:18.539951+00', true, 'mayorista'),
('164fe8d0-aca7-4421-a5b2-0f20ed4be367', 'Asesor', 'Landmark', 'asesor@landmark.com', '$2b$12$clYakNP.DlSCIwSGnnR7AuCs07Z9PIIbmOoyWdizms3oxLy5XDST2', '2025-07-29 03:44:47.917404+00', '2025-07-31 00:19:19.465076+00', true, 'proveedor'),
('d09bb133-1a3e-443f-85e4-9fe791870c9b', 'Asesor', 'Colombia Experience', 'asesor@colombiaexperience.co', '$2b$12$9wEL2nf6eXB9nXDm9OF/tuKUXHf1wBxgyo63y7Kp0KKmX9S0GhaXC', '2025-07-29 04:44:43.03009+00', '2025-07-29 06:44:28.542692+00', true, 'proveedor')
ON CONFLICT DO NOTHING;

-- ============================================
-- SEED DATA - PROVEEDORES
-- ============================================

INSERT INTO proveedores (id_proveedor, tipo, nombre, descripcion, email, telefono, direccion, ciudad, pais, sitio_web, rating_promedio, verificado, fecha_registro, ubicacion, redes_sociales, relevancia, usuario_creador, tipo_documento, numero_documento, activo) VALUES
('a98d6834-9795-4f37-93d9-15212419fba9', 'hotel', 'Hotel Landmark', 'Hotel boutique en Medellín con restaurantes, spa y piscina.', 'asesor@landmark.com', '+57 304 2343158', 'Calle 14 # 43D 85', 'Medellin', 'Colombia', 'https://landmarkmedellin.com/es/inicio/', 4.00, true, '2025-07-29 04:50:29.526+00', 'El Poblado', NULL, 'Alto', 'admin', 'RUT', '111413', true),
('887c7ed8-98c8-4017-8968-aeb68c9ddefa', 'hotel', 'Hotel Boutique Don Pepe', 'Hotel boutique en Santa Marta con spa y restaurante.', 'asesor@hotelboutiquedonpepe.com', '+57 3218291777', 'Cl 16 # 1c – 92 Barrio Centro. Santa Marta', 'Santa Marta', 'Colombia', 'https://hotelboutiquedonpepe.com/', 5.00, true, '2025-07-29 05:10:17.288+00', 'Centro', NULL, 'Alto', 'admin', 'NIT', '900433951', true),
('920235c4-ee96-43fb-9c32-00ea167a34b5', 'restaurante', 'Marmi Ristorante', 'Restaurante italiano con fusiones francesas.', 'asesor@marmi.com', '+57 317 7506407', 'Carrera 4 No. 26- 40 Locales 113 – 114 - 115', 'Santa Marta', 'Colombia', 'https://marmi.precompro.com/', 5.00, true, '2025-07-29 05:13:28.064+00', 'Prado Plaza', 'marmiristorantebar', 'media', 'admin', 'RUT', '255542', true),
('c4845980-6a2f-4b6c-95ff-b3a988e22669', 'restaurante', 'Agua De Rio Café', 'Café y bistro en Santa Marta.', 'asesor@aguaderio.com.co', '+57 314-515-9599', 'Carrera 2 #16 - 47, Centro Histórico', 'Santa Marta', 'Colombia', 'https://aguaderio.com.co/', 5.00, true, '2025-07-29 05:28:07.78+00', 'Centro Histórico', 'aguaderio_smr', 'media', 'admin', 'NIT', '806015647-5', true),
('4a49fc05-fa00-469b-ad9f-b51d92f5c050', 'tour', 'Agencia Colombia Experience', 'Agencia de turismo en Cartagena.', 'asesor@colombiaexperience.co', '(+57) 311-816-1350', 'Centro Comercial Pasaje Leclerc – Local 7', 'Cartagena', 'Colombia', 'https://colombiaexperience.co/', 4.00, true, '2025-07-29 04:37:32.98+00', NULL, NULL, 'MEDIA', 'admin', 'NIT', NULL, true),
('8a0f251f-864a-489b-8a8c-3c9f4f2be408', 'tour', 'Asesor Xperiences', 'Agencia de viajes operadora.', 'asesor@xperiences.com.co', '313 305 2017', 'CR 44 NO. 58 A 13 SUR', 'Bogota', 'Colombia', 'https://xperiencia.com.co/', 4.00, true, '2025-07-29 05:47:14.483+00', NULL, NULL, 'MEDIA', 'admin', 'NIT', NULL, true)
ON CONFLICT DO NOTHING;

-- ============================================
-- SEED DATA - SERVICIOS
-- ============================================

INSERT INTO servicios (id_servicio, proveedor_id, nombre, descripcion, tipo_servicio, precio, moneda, activo, fecha_creacion, fecha_actualizacion, relevancia, ciudad, departamento, ubicacion, detalles_del_servicio) VALUES
('eae51613-f27e-41a5-88b0-59ec02c01684', '4a49fc05-fa00-469b-ad9f-b51d92f5c050', 'Pasadía en Isla Kokomo', 'Almuerzo típico, Cóctel de bienvenida', 'experiencias', 79.00, 'USD', true, '2025-07-29 06:48:46.078+00', '2025-07-29 06:48:46.078+00', 'MEDIA', 'Cartagena', 'Bolivar', NULL, '{"tipo_tour":"Cultural","duracion":"Día completo","grupo_objetivo":"Individual","incluye":{"transporte":true,"guia":true,"alimentacion":true,"entradas_sitios":true},"dificultad":"Media"}'),
('b975406c-3ae6-4105-9e74-15bef4477450', '887c7ed8-98c8-4017-8968-aeb68c9ddefa', 'Habitación Don Pepe Estandar', 'Habitaciones de 23 metros cuadrados', 'alojamiento', 200000.00, 'COP', true, '2025-07-29 06:31:56.81+00', '2025-07-30 01:41:31.007+00', 'ALTA', 'Santa Marta', 'Magdalena', 'Cl 16 # 1c – 92 Barrio Centro', '{"tipo_alojamiento":"Hotel","habitacion":"Estándar","capacidad":2}'),
('7465d99a-8cdb-4289-9ce0-0f7cd8185bb1', '4a49fc05-fa00-469b-ad9f-b51d92f5c050', 'Pasadía Isla Bora Bora', 'Día de playa en Bora Bora Beach Club', 'experiencias', 95.00, 'USD', true, '2025-07-29 06:48:46.078+00', '2025-07-29 06:48:46.078+00', 'MEDIA', 'Cartagena', 'Bolivar', NULL, '{"tipo_tour":"Cultural","duracion":"Día completo"}'),
('3d3551fa-4202-4452-bc3d-87dd8835f77b', 'a98d6834-9795-4f37-93d9-15212419fba9', 'Habitación Duplex King Suite', 'Suite de dos pisos con jacuzzi', 'alojamiento', 700000.00, 'COP', true, '2025-07-29 06:19:04.378+00', '2025-07-29 21:07:51.864+00', 'MEDIA', 'Medellín', 'Antioquia', 'Calle 14 # 43D 85', '{"tipo_alojamiento":"Hotel","habitacion":"Suite","capacidad":2}'),
('019f2d43-8fa0-4414-80f5-fe2180942fe5', '920235c4-ee96-43fb-9c32-00ea167a34b5', 'Cena Amor y Amistad', 'Combo Cena + Bebida con música en vivo', 'restaurante', 200000.00, 'COP', true, '2025-07-29 06:05:27.468+00', '2025-07-29 21:08:51.803+00', 'ALTA', 'Santa Marta', 'Magdalena', 'Carrera 4 # 26 - 40 Prado Plaza', '{"tipo_establecimiento":"Restaurante gourmet","capacidad":20}'),
('0ac1364c-1e81-4166-8162-e3bc35ff4320', 'a98d6834-9795-4f37-93d9-15212419fba9', 'Habitación Deluxe Queen', 'Habitación con vista al jardín', 'alojamiento', 450000.00, 'COP', true, '2025-07-29 06:19:04.378+00', '2025-07-29 21:10:07.525+00', 'MEDIA', 'Medellín', 'Antioquia', 'Calle 14 # 43D 85', '{"tipo_alojamiento":"Hotel","habitacion":"Suite","capacidad":2}'),
('fcc1ad1e-e8a1-4130-8f99-16101cab1bef', '920235c4-ee96-43fb-9c32-00ea167a34b5', 'Pizza Napolitana', 'Pizza original napolitana', 'restaurante', 50000.00, 'COP', true, '2025-07-29 06:08:32.666+00', '2025-07-29 06:08:32.666+00', 'ALTA', 'Santa Marta', 'Magdalena', 'Carrera 4 # 26 - 40 Prado Plaza', '{"tipo_establecimiento":"Restaurante gourmet"}'),
('b1db139f-3ab9-4958-a8e5-dbec4b662b01', '920235c4-ee96-43fb-9c32-00ea167a34b5', 'Pastas Alfredo', 'Pastas alfredo únicas', 'restaurante', 30000.00, 'COP', true, '2025-07-29 06:08:32.666+00', '2025-07-29 06:08:32.666+00', 'MEDIA', 'Santa Marta', 'Magdalena', 'Carrera 4 # 26 - 40 Prado Plaza', '{"tipo_establecimiento":"Restaurante gourmet"}'),
('bf83f949-536a-4b0f-897a-39d680870634', '920235c4-ee96-43fb-9c32-00ea167a34b5', 'Pizza Vegetariana', 'Opción vegana', 'restaurante', 60000.00, 'COP', true, '2025-07-29 06:08:32.666+00', '2025-07-29 06:08:32.666+00', 'BAJA', 'Santa Marta', 'Magdalena', 'Carrera 4 # 26 - 40 Prado Plaza', '{"tipo_establecimiento":"Restaurante gourmet"}'),
('825a0035-0426-4489-9a25-2c4bb5eed93c', 'a98d6834-9795-4f37-93d9-15212419fba9', 'Habitación Suite', 'Habitación Suite', 'alojamiento', 200000.00, 'COP', true, '2025-07-29 06:19:04.378+00', '2025-07-29 06:19:04.378+00', 'MEDIA', 'Medellín', 'Antioquia', 'Calle 14 # 43D 85', '{"tipo_alojamiento":"Hotel","habitacion":"Suite"}'),
('3805fdc3-1e10-4958-bc84-f293469f6e7c', 'a98d6834-9795-4f37-93d9-15212419fba9', 'Habitación Estandar', 'Habitación Estandar', 'alojamiento', 400000.00, 'COP', true, '2025-07-29 06:19:04.378+00', '2025-07-29 06:19:04.378+00', 'MEDIA', 'Medellín', 'Antioquia', 'Calle 14 # 43D 85', '{"tipo_alojamiento":"Hotel","habitacion":"Suite"}'),
('c021316c-4b9c-4452-a48a-17b78329f033', '8a0f251f-864a-489b-8a8c-3c9f4f2be408', 'Parapente en la Calera', 'Vuela sobre los Andes Colombianos', 'experiencias', 250000.00, 'COP', true, '2025-07-29 06:59:56.05+00', '2025-07-29 06:59:56.05+00', 'ALTA', 'Bogotá', 'Cundinamarca', 'Calle 100 # 15-20', '{"tipo_tour":"Aventura","duracion":"Medio día"}'),
('991c3412-f883-42f8-b61f-0051b9af4e50', '8a0f251f-864a-489b-8a8c-3c9f4f2be408', 'Cordillera Blanca Perú', 'Destino de montaña en Huaraz', 'experiencias', 4800000.00, 'COP', true, '2025-07-29 07:03:45.014+00', '2025-07-29 07:03:45.014+00', 'ALTA', 'Huaraz', 'Huaraz', 'Huaraz - PERU', '{"tipo_tour":"Aventura","duracion":"Varios días"}'),
('2926ca3b-74ce-4b92-ba40-6ca99308412e', '887c7ed8-98c8-4017-8968-aeb68c9ddefa', 'Habitación Luxury', 'Habitaciones de 29 metros', 'alojamiento', 300000.00, 'COP', true, '2025-07-29 06:33:10.744+00', '2025-07-29 21:08:34.864+00', 'MEDIA', 'Santa Marta', 'Magdalena', 'Cl 16 # 1c – 92 Barrio Centro', '{"tipo_alojamiento":"Hotel","habitacion":"Premium"}'),
('750cad05-1f81-4f7e-97c3-4e2e96190f47', '887c7ed8-98c8-4017-8968-aeb68c9ddefa', 'Habitación Luxury Twin', 'Habitación de 32 metros', 'alojamiento', 350000.00, 'COP', true, '2025-07-29 06:34:28.191+00', '2025-07-30 01:41:56.079+00', 'ALTA', 'Santa Marta', 'Magdalena', 'Cl 16 # 1c – 92 Barrio Centro', '{"tipo_alojamiento":"Hotel","habitacion":"Suite"}'),
('e2a0dc86-3905-4d13-866a-00cb826cc7a3', 'a98d6834-9795-4f37-93d9-15212419fba9', 'Habitación Doble Queen con Balcón', 'Ideal para familias', 'alojamiento', 450000.00, 'COP', true, '2025-07-29 06:19:04.378+00', '2025-07-30 01:42:14.931+00', 'MEDIA', 'Medellín', 'Antioquia', 'Calle 14 # 43D 85', '{"tipo_alojamiento":"Hotel","habitacion":"Suite"}')
ON CONFLICT DO NOTHING;

-- ============================================
-- SEED DATA - HOTELES
-- ============================================

INSERT INTO hoteles (id_hotel, estrellas, numero_habitaciones, servicios_incluidos, check_in, check_out, admite_mascotas, tiene_estacionamiento, tipo_habitacion, precio_ascendente, servicio_restaurante, recepcion_24_horas, bar, room_service, asensor, rampa_discapacitado, pet_friendly, auditorio, parqueadero, piscina, planta_energia) VALUES
('a98d6834-9795-4f37-93d9-15212419fba9', 5, 20, 'WIFI, AC, Baños privados.', '14:00:00', '12:00:00', true, true, 'Standard', 400000.00, true, true, true, false, false, true, true, true, false, true, false),
('887c7ed8-98c8-4017-8968-aeb68c9ddefa', 5, 12, 'Desayuno, WIFI', '14:00:00', '12:00:00', false, true, 'Standard', 450000.00, true, true, true, false, false, false, false, false, false, true, false)
ON CONFLICT DO NOTHING;

-- ============================================
-- SEED DATA - RESTAURANTES
-- ============================================

INSERT INTO restaurantes (id_restaurante, tipo_cocina, horario_apertura, horario_cierre, capacidad, menu_url, tiene_terraza, apto_celiacos, apto_vegetarianos, reservas_requeridas, entrega_a_domicilio, wifi, zonas_comunes, auditorio, pet_friendly, eventos, menu_vegana, bufete, catering, menu_infantil, parqueadero, terraza, sillas_bebe, decoraciones_fechas_especiales, rampa_discapacitados, aforo_maximo, tipo_comida, precio_ascendente) VALUES
('920235c4-ee96-43fb-9c32-00ea167a34b5', 'Italiana', '12:01:00', '22:00:00', 50, 'https://marmi.precompro.com/', false, false, false, true, true, true, false, false, false, false, false, false, false, true, false, true, false, true, false, 100, 'Gourmet', 32000.00),
('c4845980-6a2f-4b6c-95ff-b3a988e22669', 'Bar Café', '08:00:00', '22:30:00', 20, 'https://menupp.co/aguaderio', false, false, false, false, true, true, true, false, false, true, false, false, false, false, false, true, false, true, false, 20, 'Colombiana', 21000.00)
ON CONFLICT DO NOTHING;

-- ============================================
-- SEED DATA - EXPERIENCIAS
-- ============================================

INSERT INTO experiencias (id_experiencia, duracion, dificultad, idioma, incluye_transporte, grupo_maximo, guia_incluido, equipamiento_requerido, punto_de_encuentro, numero_rnt) VALUES
('4a49fc05-fa00-469b-ad9f-b51d92f5c050', 7, 'MODERADO', 'ES', false, 5, true, 'Incluye transporte, guía, alimentación', 'Muelle', '171166'),
('8a0f251f-864a-489b-8a8c-3c9f4f2be408', 1, 'DIFICIL', 'ES', true, 9, true, 'Ropa cómoda, guantes, protector solar', 'Hotel', '70630')
ON CONFLICT DO NOTHING;

-- ============================================
-- SEED DATA - FOTOS
-- ============================================

INSERT INTO fotos (id, servicio_id, url, descripcion, orden, es_portada, fecha_subida, eliminado) VALUES
('a8de1366-37c8-45f7-a7ac-0157536ea4de', 'eae51613-f27e-41a5-88b0-59ec02c01684', 'https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/eae51613-f27e-41a5-88b0-59ec02c01684/img_1.jpeg', 'Imagen 1', 1, false, '2025-07-29 06:06:00+00', false),
('42ea930e-dd8f-450b-b28c-f20f401e81eb', '750cad05-1f81-4f7e-97c3-4e2e96190f47', 'https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/750cad05-1f81-4f7e-97c3-4e2e96190f47/img_1.jpg', 'Imagen 1', 1, false, '2025-07-29 06:06:00+00', false),
('f8703237-9c79-467f-a5c0-bd12a1e0a4d6', 'c021316c-4b9c-4452-a48a-17b78329f033', 'https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/c021316c-4b9c-4452-a48a-17b78329f033/img_1.jpg', 'Imagen 1', 1, false, '2025-07-29 06:06:00+00', false)
ON CONFLICT DO NOTHING;

-- ============================================
-- SEED DATA - MAYORISTAS
-- ============================================

INSERT INTO mayoristas (id, nombre, apellidos, descripcion, email, telefono, direccion, ciudad, pais, recurente, usuario_creador, verificado, fecha_creacion, intereses, tipo_documento, numero_documento, activo, fecha_actualizacion) VALUES
('32694fd8-bde4-4614-8810-b4cadb50ff03', 'luis Gabriel', 'Quiceno Espitia', 'Comprador independiente', 'mayorista@gmail.com', '3216253312', 'Calle 47 # 14 - 40', 'Montería', 'Colombia', true, 'admin', true, '2025-07-30 02:17:50.177197+00', 'Hoteles', 'RUT', '32132312', true, '2025-07-30 02:17:50.177201+00'),
('f14c86ff-5c5e-4fe2-baf6-331aca71d4aa', 'luis Gabriel', 'Quiceno Espitia', 'Comprador independiente', 'mayorista2@gmail.com', '3216253312', 'Calle 47 # 14 - 40', 'Montería', 'Colombia', true, 'admin', true, '2025-07-30 02:18:09.497269+00', 'Hoteles', 'RUT', '32132313', true, '2025-07-30 02:18:09.497274+00')
ON CONFLICT DO NOTHING;

COMMIT;
