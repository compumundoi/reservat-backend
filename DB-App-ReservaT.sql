--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.5 (Homebrew)

-- Started on 2025-08-09 15:14:54 -05

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 230 (class 1259 OID 16770)
-- Name: experiencias; Type: TABLE; Schema: usr_app; Owner: postgres
--

CREATE TABLE usr_app.experiencias (
    id_experiencia uuid DEFAULT public.uuid_generate_v4() NOT NULL,
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


ALTER TABLE usr_app.experiencias OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16712)
-- Name: fechas_bloqueadas; Type: TABLE; Schema: usr_app; Owner: postgres
--

CREATE TABLE usr_app.fechas_bloqueadas (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    servicio_id uuid,
    fecha timestamp with time zone NOT NULL,
    motivo text,
    bloqueado_por text,
    bloqueo_activo boolean
);


ALTER TABLE usr_app.fechas_bloqueadas OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16672)
-- Name: fotos; Type: TABLE; Schema: usr_app; Owner: postgres
--

CREATE TABLE usr_app.fotos (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    servicio_id uuid,
    url text NOT NULL,
    descripcion text,
    orden integer,
    es_portada boolean DEFAULT false,
    fecha_subida timestamp with time zone DEFAULT now(),
    eliminado boolean NOT NULL
);


ALTER TABLE usr_app.fotos OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16745)
-- Name: hoteles; Type: TABLE; Schema: usr_app; Owner: postgres
--

CREATE TABLE usr_app.hoteles (
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


ALTER TABLE usr_app.hoteles OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16809)
-- Name: mayoristas; Type: TABLE; Schema: usr_app; Owner: postgres
--

CREATE TABLE usr_app.mayoristas (
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
    contacto_principal character varying,
    telefono_contacto character varying,
    email_contacto character varying,
    comision_porcentaje double precision,
    limite_credito double precision,
    estado character varying DEFAULT 'activo'::character varying,
    observaciones text,
    activo boolean DEFAULT true,
    fecha_actualizacion timestamp with time zone
);


ALTER TABLE usr_app.mayoristas OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16607)
-- Name: proveedores; Type: TABLE; Schema: usr_app; Owner: postgres
--

CREATE TABLE usr_app.proveedores (
    id_proveedor uuid DEFAULT public.uuid_generate_v4() NOT NULL,
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


ALTER TABLE usr_app.proveedores OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 17022)
-- Name: reservas; Type: TABLE; Schema: usr_app; Owner: postgres
--

CREATE TABLE usr_app.reservas (
    id_reserva uuid NOT NULL,
    id_proveedor uuid,
    id_servicio uuid,
    id_mayorista uuid,
    nombre_servicio character varying,
    descripcion character varying,
    tipo_servicio character varying,
    precio character varying,
    ciudad character varying,
    activo boolean DEFAULT true,
    estado character varying,
    observaciones character varying,
    fecha_creacion date,
    cantidad integer,
    fecha_inicio date,
    fecha_fin date
);


ALTER TABLE usr_app.reservas OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16758)
-- Name: restaurantes; Type: TABLE; Schema: usr_app; Owner: postgres
--

CREATE TABLE usr_app.restaurantes (
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


ALTER TABLE usr_app.restaurantes OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16687)
-- Name: rutas; Type: TABLE; Schema: usr_app; Owner: postgres
--

CREATE TABLE usr_app.rutas (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
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


ALTER TABLE usr_app.rutas OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16634)
-- Name: servicios; Type: TABLE; Schema: usr_app; Owner: postgres
--

CREATE TABLE usr_app.servicios (
    id_servicio uuid DEFAULT public.uuid_generate_v4() NOT NULL,
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


ALTER TABLE usr_app.servicios OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16730)
-- Name: transportes; Type: TABLE; Schema: usr_app; Owner: postgres
--

CREATE TABLE usr_app.transportes (
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


ALTER TABLE usr_app.transportes OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16595)
-- Name: usuarios; Type: TABLE; Schema: usr_app; Owner: postgres
--

CREATE TABLE usr_app.usuarios (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    nombre text NOT NULL,
    apellido text,
    email text NOT NULL,
    "contraseña" text NOT NULL,
    fecha_registro timestamp with time zone DEFAULT now(),
    ultimo_login timestamp with time zone,
    activo boolean DEFAULT true,
    tipo_usuario character varying
);


ALTER TABLE usr_app.usuarios OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16696)
-- Name: viajes; Type: TABLE; Schema: usr_app; Owner: postgres
--

CREATE TABLE usr_app.viajes (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
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


ALTER TABLE usr_app.viajes OWNER TO postgres;

--
-- TOC entry 4449 (class 0 OID 16770)
-- Dependencies: 230
-- Data for Name: experiencias; Type: TABLE DATA; Schema: usr_app; Owner: postgres
--

COPY usr_app.experiencias (id_experiencia, duracion, dificultad, idioma, incluye_transporte, grupo_maximo, guia_incluido, equipamiento_requerido, punto_de_encuentro, numero_rnt) FROM stdin;
4a49fc05-fa00-469b-ad9f-b51d92f5c050	7	MODERADO	ES	f	5	t	Incluye:\n* Recogida en hotel zonas Turísticas\n* Transporte Marítimo en botes de lujos\n* Panorámico por las Islas del Rosario\n* Parada en Oceanario con entrada incluida\n* Actividad de Snorkel\n* Disfrute en Isla cholón (Cóctel de camarón de bienvenida)\n* Disfrute de playa en Isla Agua Azul / Isla Coral\n* Almuerzo en Islas de Barú, Playa Tranquila (Opciones de Pescado, Pechuga o Vegetariano)\n* Atardecer en Playa Tranquila, usos de las instalaciones.\n\nHorarios: Recogida en hotel entre las 7:30 y 8:20 am, Checking: 8:30 AM, Zarpe: 9:00 am, Retorno: 4:00 pm, Llegada muelle: 5:00 pm\nNota: Se permite el ingreso de alimentos y bebidas	Muelle	171166
8a0f251f-864a-489b-8a8c-3c9f4f2be408	1	DIFICIL	ES	t	9	t	Ropa adecuada: tenis, sudadera y/o pantaloneta,\nGorra.\nGafas con filtro.\nCarpa (solo si vas acampar)\nAislante.\nVestido de baño.\nRopa de Cambio\nRepelente.\nBloqueador.\nDocumento de identidad, carné seguro médico, teléfono celular con minutos, dinero extra para gastos personales.\nCantimplora con bebida hidratante.\nLa mejor actitud: Llega con entusiasmo y disposición para vivir una aventura única e inolvidable en el Desierto de la Tatacoa.	Hotel	70630
\.


--
-- TOC entry 4445 (class 0 OID 16712)
-- Dependencies: 226
-- Data for Name: fechas_bloqueadas; Type: TABLE DATA; Schema: usr_app; Owner: postgres
--

COPY usr_app.fechas_bloqueadas (id, servicio_id, fecha, motivo, bloqueado_por, bloqueo_activo) FROM stdin;
\.


--
-- TOC entry 4442 (class 0 OID 16672)
-- Dependencies: 223
-- Data for Name: fotos; Type: TABLE DATA; Schema: usr_app; Owner: postgres
--

COPY usr_app.fotos (id, servicio_id, url, descripcion, orden, es_portada, fecha_subida, eliminado) FROM stdin;
a8de1366-37c8-45f7-a7ac-0157536ea4de	eae51613-f27e-41a5-88b0-59ec02c01684	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/eae51613-f27e-41a5-88b0-59ec02c01684/img_1.jpeg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
a41971ce-4c09-4d10-936e-1e8fafafb244	2926ca3b-74ce-4b92-ba40-6ca99308412e	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/2926ca3b-74ce-4b92-ba40-6ca99308412e/img_4.jpg	Imagen 43	4	f	2025-07-29 06:06:00+00	f
cdf8a407-b326-4589-af32-486262f3fc3c	eae51613-f27e-41a5-88b0-59ec02c01684	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/eae51613-f27e-41a5-88b0-59ec02c01684/img_2.jpeg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
b9578be2-a4b9-44db-ab02-84304c8aab1c	2926ca3b-74ce-4b92-ba40-6ca99308412e	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/2926ca3b-74ce-4b92-ba40-6ca99308412e/img_5.jpg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
42ea930e-dd8f-450b-b28c-f20f401e81eb	750cad05-1f81-4f7e-97c3-4e2e96190f47	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/750cad05-1f81-4f7e-97c3-4e2e96190f47/img_1.jpg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
07429064-758a-4467-8021-4cff014a955a	750cad05-1f81-4f7e-97c3-4e2e96190f47	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/750cad05-1f81-4f7e-97c3-4e2e96190f47/img_2.jpg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
61ec7eaa-397f-44a0-a196-210c2e71e46d	750cad05-1f81-4f7e-97c3-4e2e96190f47	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/750cad05-1f81-4f7e-97c3-4e2e96190f47/img_3.jpg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
bb46e4a6-22f9-4664-aa3b-c01e71975a8e	750cad05-1f81-4f7e-97c3-4e2e96190f47	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/750cad05-1f81-4f7e-97c3-4e2e96190f47/img_4.jpg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
e9faafdc-3842-4036-8bbf-2e8cdda6b86c	750cad05-1f81-4f7e-97c3-4e2e96190f47	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/750cad05-1f81-4f7e-97c3-4e2e96190f47/img_5.jpeg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
89b0f834-1ef2-4df9-9e5e-273a962995c0	991c3412-f883-42f8-b61f-0051b9af4e50	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/991c3412-f883-42f8-b61f-0051b9af4e50/img_1.jpg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
af4ed0be-4d38-4365-a04a-cc1cbe93a612	991c3412-f883-42f8-b61f-0051b9af4e50	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/991c3412-f883-42f8-b61f-0051b9af4e50/img_2.jpg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
0cc3afe7-14a4-45b5-a82f-9ba176f6f92b	991c3412-f883-42f8-b61f-0051b9af4e50	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/991c3412-f883-42f8-b61f-0051b9af4e50/img_3.jpg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
d42f7381-ebf0-49e0-92c6-a9f9c2e3d181	991c3412-f883-42f8-b61f-0051b9af4e50	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/991c3412-f883-42f8-b61f-0051b9af4e50/img_4.jpg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
40849d09-d2a6-4a95-940e-320ff49bcfd8	991c3412-f883-42f8-b61f-0051b9af4e50	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/991c3412-f883-42f8-b61f-0051b9af4e50/img_5.jpg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
f8703237-9c79-467f-a5c0-bd12a1e0a4d6	c021316c-4b9c-4452-a48a-17b78329f033	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/c021316c-4b9c-4452-a48a-17b78329f033/img_1.jpg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
51bb29d0-0050-4e16-8ef1-d0ad68ac1bf3	c021316c-4b9c-4452-a48a-17b78329f033	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/c021316c-4b9c-4452-a48a-17b78329f033/img_2.jpg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
902da62d-f4e0-46e2-b88a-d45cf92299c7	eae51613-f27e-41a5-88b0-59ec02c01684	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/eae51613-f27e-41a5-88b0-59ec02c01684/img_3.jpeg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
6e0033ee-239e-464a-b302-17b5df3d6e7c	eae51613-f27e-41a5-88b0-59ec02c01684	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/eae51613-f27e-41a5-88b0-59ec02c01684/img_4.jpeg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
c80b8f2a-7c90-4068-96d7-36b20bef7cef	eae51613-f27e-41a5-88b0-59ec02c01684	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/eae51613-f27e-41a5-88b0-59ec02c01684/img_5.jpeg	Imagen 4	5	f	2025-07-29 06:06:00+00	f
5888546e-bce2-4cae-9eff-cc683e4d7135	3d3551fa-4202-4452-bc3d-87dd8835f77b	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/3d3551fa-4202-4452-bc3d-87dd8835f77b/img_1.jpeg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
a3c7c91d-ea8f-4c75-a624-b1e6de64d9d5	3d3551fa-4202-4452-bc3d-87dd8835f77b	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/3d3551fa-4202-4452-bc3d-87dd8835f77b/img_2.jpg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
aa4ea5b3-156a-4cc3-8671-5253a96746c7	3d3551fa-4202-4452-bc3d-87dd8835f77b	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/3d3551fa-4202-4452-bc3d-87dd8835f77b/img_3.jpg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
27c78924-659c-4502-8b2c-74a33f3c55ad	3d3551fa-4202-4452-bc3d-87dd8835f77b	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/3d3551fa-4202-4452-bc3d-87dd8835f77b/img_4.jpg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
ed246c60-6846-4b1d-b207-91f9fe8c0923	3d3551fa-4202-4452-bc3d-87dd8835f77b	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/3d3551fa-4202-4452-bc3d-87dd8835f77b/img_5.jpeg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
f4928434-b923-48e2-8fa9-eb7f7695b002	b975406c-3ae6-4105-9e74-15bef4477450	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/b975406c-3ae6-4105-9e74-15bef4477450/img_1.jpg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
7b2cabc4-4ca7-40a3-9904-829b204b7c8a	b975406c-3ae6-4105-9e74-15bef4477450	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/b975406c-3ae6-4105-9e74-15bef4477450/img_2.jpg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
6fd49192-ed40-460a-b048-11adbb79a426	b975406c-3ae6-4105-9e74-15bef4477450	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/b975406c-3ae6-4105-9e74-15bef4477450/img_3.jpg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
a2f87d51-1dd8-4086-b9f8-c9a70fcef4af	b975406c-3ae6-4105-9e74-15bef4477450	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/b975406c-3ae6-4105-9e74-15bef4477450/img_4.jpg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
28f74c3a-396f-411f-92c7-f0bbc782dec6	b975406c-3ae6-4105-9e74-15bef4477450	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/b975406c-3ae6-4105-9e74-15bef4477450/img_5.jpg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
e69e3152-48f0-4f66-8884-b87d96604458	2926ca3b-74ce-4b92-ba40-6ca99308412e	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/2926ca3b-74ce-4b92-ba40-6ca99308412e/img_1.jpg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
02b122e3-c877-4346-a54c-451b56d2ddeb	2926ca3b-74ce-4b92-ba40-6ca99308412e	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/2926ca3b-74ce-4b92-ba40-6ca99308412e/img_2.jpg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
addb4779-4940-49e8-ac0b-6322eb499ff7	2926ca3b-74ce-4b92-ba40-6ca99308412e	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/2926ca3b-74ce-4b92-ba40-6ca99308412e/img_3.jpg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
60cff2d0-a0c3-4c9e-9f0f-708be3d925bd	c021316c-4b9c-4452-a48a-17b78329f033	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/c021316c-4b9c-4452-a48a-17b78329f033/img_3.jpg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
a269cd12-0eec-4a5c-a94c-4e184bfd9d44	c021316c-4b9c-4452-a48a-17b78329f033	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/c021316c-4b9c-4452-a48a-17b78329f033/img_4.jpg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
c0cc6bc5-05c4-4152-aefc-9a0735862455	c021316c-4b9c-4452-a48a-17b78329f033	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/c021316c-4b9c-4452-a48a-17b78329f033/img_5.jpg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
ef309dbd-0c9c-4ed9-a825-55c14b2d9028	7465d99a-8cdb-4289-9ce0-0f7cd8185bb1	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/7465d99a-8cdb-4289-9ce0-0f7cd8185bb1/img_1.jpg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
3009fa46-774f-47e1-a4e6-780c420b6e5d	7465d99a-8cdb-4289-9ce0-0f7cd8185bb1	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/7465d99a-8cdb-4289-9ce0-0f7cd8185bb1/img_2.jpg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
eedf92b0-85fb-44a8-a3a1-1ca1b9cfc2d8	7465d99a-8cdb-4289-9ce0-0f7cd8185bb1	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/7465d99a-8cdb-4289-9ce0-0f7cd8185bb1/img_3.jpeg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
1bd78ce4-3e04-47c3-be26-d7c673e65040	7465d99a-8cdb-4289-9ce0-0f7cd8185bb1	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/7465d99a-8cdb-4289-9ce0-0f7cd8185bb1/img_4.jpg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
9a5e5dd1-6102-4926-b5f5-16aa1aa60b1c	7465d99a-8cdb-4289-9ce0-0f7cd8185bb1	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/7465d99a-8cdb-4289-9ce0-0f7cd8185bb1/img_5.jpg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
4b1ca35b-ea56-477f-93b9-ad3a8c309bc3	fcc1ad1e-e8a1-4130-8f99-16101cab1bef	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/fcc1ad1e-e8a1-4130-8f99-16101cab1bef/img_1.jpg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
ca573f56-2fda-4e6b-8e27-1f48e0b2bb32	fcc1ad1e-e8a1-4130-8f99-16101cab1bef	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/fcc1ad1e-e8a1-4130-8f99-16101cab1bef/img_2.jpg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
0312c995-8f86-4d6f-b5f9-052709ac1e0d	fcc1ad1e-e8a1-4130-8f99-16101cab1bef	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/fcc1ad1e-e8a1-4130-8f99-16101cab1bef/img_3.jpg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
e03b65e4-15ff-4e49-95dd-9297cd31d0c3	fcc1ad1e-e8a1-4130-8f99-16101cab1bef	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/fcc1ad1e-e8a1-4130-8f99-16101cab1bef/img_4.png	Imagen 4	4	f	2025-07-29 06:06:00+00	f
79d8f087-71b1-4fda-b7e6-df885473f61f	fcc1ad1e-e8a1-4130-8f99-16101cab1bef	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/fcc1ad1e-e8a1-4130-8f99-16101cab1bef/img_5.jpeg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
eb5c0191-ea90-4891-8de0-11f886e30144	bf83f949-536a-4b0f-897a-39d680870634	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/bf83f949-536a-4b0f-897a-39d680870634/img_1.jpg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
25414d8a-b7de-4448-b122-99bfccf374eb	bf83f949-536a-4b0f-897a-39d680870634	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/bf83f949-536a-4b0f-897a-39d680870634/img_2.jpg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
5e0a43a1-a29f-4b8a-b1f5-64def98484b5	bf83f949-536a-4b0f-897a-39d680870634	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/bf83f949-536a-4b0f-897a-39d680870634/img_3.jpg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
11986dc7-86a2-4d7f-bafc-0fbb55da58cf	bf83f949-536a-4b0f-897a-39d680870634	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/bf83f949-536a-4b0f-897a-39d680870634/img_4.jpg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
c7c6f9e0-7cb1-4087-ad6c-74a0efcc1a9c	bf83f949-536a-4b0f-897a-39d680870634	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/bf83f949-536a-4b0f-897a-39d680870634/img_5.jpg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
93f223d8-4bc9-4fd3-9a99-4e115e7cfe03	b1db139f-3ab9-4958-a8e5-dbec4b662b01	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/b1db139f-3ab9-4958-a8e5-dbec4b662b01/img_1.jpeg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
e387af63-bedb-4f34-9476-a3a6a261013c	b1db139f-3ab9-4958-a8e5-dbec4b662b01	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/b1db139f-3ab9-4958-a8e5-dbec4b662b01/img_2.jpeg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
6fbea064-6319-4d8e-b574-0b0eb6a1260c	b1db139f-3ab9-4958-a8e5-dbec4b662b01	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/b1db139f-3ab9-4958-a8e5-dbec4b662b01/img_3.jpeg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
73db7e35-8c63-4fdb-916e-df87e5bd16c9	b1db139f-3ab9-4958-a8e5-dbec4b662b01	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/b1db139f-3ab9-4958-a8e5-dbec4b662b01/img_4.jpg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
300e7b86-a327-491b-a993-09c28f715f44	019f2d43-8fa0-4414-80f5-fe2180942fe5	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/019f2d43-8fa0-4414-80f5-fe2180942fe5/img_1.png	Imagen 1	1	f	2025-07-29 06:06:00+00	f
285aa46d-3e8c-474e-b9db-8b67b549de3a	019f2d43-8fa0-4414-80f5-fe2180942fe5	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/019f2d43-8fa0-4414-80f5-fe2180942fe5/img_2.jpg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
7f9bfe65-cdb4-4b8b-b555-77ca61e5dee9	019f2d43-8fa0-4414-80f5-fe2180942fe5	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/019f2d43-8fa0-4414-80f5-fe2180942fe5/img_3.jpg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
7270ee6f-ac40-4602-b2b1-813b2d618edc	019f2d43-8fa0-4414-80f5-fe2180942fe5	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/019f2d43-8fa0-4414-80f5-fe2180942fe5/img_4.jpg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
9916ff2e-726b-4457-9c18-cb2277d1ff81	019f2d43-8fa0-4414-80f5-fe2180942fe5	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/019f2d43-8fa0-4414-80f5-fe2180942fe5/img_5.jpeg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
c70d743d-a8f1-4a95-b06f-1dec20c24e9d	b1db139f-3ab9-4958-a8e5-dbec4b662b01	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/b1db139f-3ab9-4958-a8e5-dbec4b662b01/img_5.jpg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
9a372252-42e3-4700-b282-250c68fe5401	825a0035-0426-4489-9a25-2c4bb5eed93c	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/825a0035-0426-4489-9a25-2c4bb5eed93c/img_1.jpeg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
a7b8ccca-07d9-44be-aa0b-2d14d075aee3	825a0035-0426-4489-9a25-2c4bb5eed93c	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/825a0035-0426-4489-9a25-2c4bb5eed93c/img_2.jpg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
1f6c914c-158a-4a7b-a086-0419d1835706	825a0035-0426-4489-9a25-2c4bb5eed93c	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/825a0035-0426-4489-9a25-2c4bb5eed93c/img_3.jpg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
980f7d31-9b35-417e-86cc-fd5a09be1aaa	825a0035-0426-4489-9a25-2c4bb5eed93c	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/825a0035-0426-4489-9a25-2c4bb5eed93c/img_4.jpg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
fb538992-f6e1-41fe-bd99-1113d84c1e4b	825a0035-0426-4489-9a25-2c4bb5eed93c	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/825a0035-0426-4489-9a25-2c4bb5eed93c/img_5.jpg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
6f8a5b67-ead5-4716-ab1b-e1c401bccbfa	e2a0dc86-3905-4d13-866a-00cb826cc7a3	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/e2a0dc86-3905-4d13-866a-00cb826cc7a3/img_1.jpg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
aa765113-5d0d-4475-b76f-d32a8b0bda1b	e2a0dc86-3905-4d13-866a-00cb826cc7a3	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/e2a0dc86-3905-4d13-866a-00cb826cc7a3/img_2.jpg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
ebedea20-9336-4830-beed-c150732076de	e2a0dc86-3905-4d13-866a-00cb826cc7a3	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/e2a0dc86-3905-4d13-866a-00cb826cc7a3/img_3.jpg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
c0866755-2170-432c-8046-db241bcb4b09	e2a0dc86-3905-4d13-866a-00cb826cc7a3	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/e2a0dc86-3905-4d13-866a-00cb826cc7a3/img_4.jpg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
a3b6153c-5bbd-4270-a7e4-25a1e9c5082c	e2a0dc86-3905-4d13-866a-00cb826cc7a3	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/e2a0dc86-3905-4d13-866a-00cb826cc7a3/img_5.jpg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
f7ac8678-08e5-4d77-a1f2-a6b0792e75c1	0ac1364c-1e81-4166-8162-e3bc35ff4320	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/0ac1364c-1e81-4166-8162-e3bc35ff4320/img_1.jpg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
91c173e3-6a94-4674-a10f-0cc2a3f4669b	0ac1364c-1e81-4166-8162-e3bc35ff4320	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/0ac1364c-1e81-4166-8162-e3bc35ff4320/img_2.jpeg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
d159f3e9-3f4f-4d71-9825-0c4cc63e10ff	0ac1364c-1e81-4166-8162-e3bc35ff4320	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/0ac1364c-1e81-4166-8162-e3bc35ff4320/img_3.jpg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
af040a6d-df97-4b51-9ea5-1b1bca33809b	0ac1364c-1e81-4166-8162-e3bc35ff4320	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/0ac1364c-1e81-4166-8162-e3bc35ff4320/img_4.jpeg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
b7191c7d-e090-4467-ad6b-83d4a0044105	0ac1364c-1e81-4166-8162-e3bc35ff4320	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/0ac1364c-1e81-4166-8162-e3bc35ff4320/img_5.jpg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
6002c862-ca01-47ba-b28b-0c916bc8105b	3805fdc3-1e10-4958-bc84-f293469f6e7c	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/3805fdc3-1e10-4958-bc84-f293469f6e7c/img_1.jpg	Imagen 1	1	f	2025-07-29 06:06:00+00	f
7334d1ba-51fb-4f8b-9312-0fcc0a969ffd	3805fdc3-1e10-4958-bc84-f293469f6e7c	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/3805fdc3-1e10-4958-bc84-f293469f6e7c/img_2.jpg	Imagen 2	2	f	2025-07-29 06:06:00+00	f
cc4bdce4-ddbb-4aa9-a8e7-7cbe330c6023	3805fdc3-1e10-4958-bc84-f293469f6e7c	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/3805fdc3-1e10-4958-bc84-f293469f6e7c/img_3.jpg	Imagen 3	3	f	2025-07-29 06:06:00+00	f
4d1d7e8e-1b9a-49f3-bbff-948aaa01cfaf	3805fdc3-1e10-4958-bc84-f293469f6e7c	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/3805fdc3-1e10-4958-bc84-f293469f6e7c/img_4.jpg	Imagen 4	4	f	2025-07-29 06:06:00+00	f
6dd6d8d5-03e8-4ea0-a980-3b79836ec09e	3805fdc3-1e10-4958-bc84-f293469f6e7c	https://bucket-foto-reservat-qa.s3.us-east-1.amazonaws.com/img/3805fdc3-1e10-4958-bc84-f293469f6e7c/img_5.jpg	Imagen 5	5	f	2025-07-29 06:06:00+00	f
\.


--
-- TOC entry 4447 (class 0 OID 16745)
-- Dependencies: 228
-- Data for Name: hoteles; Type: TABLE DATA; Schema: usr_app; Owner: postgres
--

COPY usr_app.hoteles (id_hotel, estrellas, numero_habitaciones, servicios_incluidos, check_in, check_out, admite_mascotas, tiene_estacionamiento, tipo_habitacion, precio_ascendente, servicio_restaurante, recepcion_24_horas, bar, room_service, asensor, rampa_discapacitado, pet_friendly, auditorio, parqueadero, piscina, planta_energia) FROM stdin;
a98d6834-9795-4f37-93d9-15212419fba9	5	20	WIFI, AC, Baños privados.	14:00:00	12:00:00	t	t	Standard	400000.00	t	t	t	f	f	t	t	f	t	t	f
887c7ed8-98c8-4017-8968-aeb68c9ddefa	5	12	Desayuno, WIFI	14:00:00	12:00:00	f	t	Standard	450000.00	t	t	t	f	f	f	f	f	f	t	f
\.


--
-- TOC entry 4450 (class 0 OID 16809)
-- Dependencies: 231
-- Data for Name: mayoristas; Type: TABLE DATA; Schema: usr_app; Owner: postgres
--

COPY usr_app.mayoristas (id, nombre, apellidos, descripcion, email, telefono, direccion, ciudad, pais, recurente, usuario_creador, verificado, fecha_creacion, intereses, tipo_documento, numero_documento, activo, fecha_actualizacion) FROM stdin;
32694fd8-bde4-4614-8810-b4cadb50ff03	luis Gabriel	Quiceno Espitia	Comprador independiente	mayorista@gmail.comm	3216253312	Calle 47 # 14 - 40	Montería	Colombia	t	admin	t	2025-07-30 02:17:50.177197+00	Hoteles	RUT	32132312	t	2025-07-30 02:17:50.177201+00
f14c86ff-5c5e-4fe2-baf6-331aca71d4aa	luis Gabriel	Quiceno Espitia	Comprador independiente	mayorista@gmail.com	3216253312	Calle 47 # 14 - 40	Montería	Colombia	t	admin	t	2025-07-30 02:18:09.497269+00	Hoteles	RUT	32132312	t	2025-07-30 02:18:09.497274+00
\.


--
-- TOC entry 4440 (class 0 OID 16607)
-- Dependencies: 220
-- Data for Name: proveedores; Type: TABLE DATA; Schema: usr_app; Owner: postgres
--

COPY usr_app.proveedores (id_proveedor, tipo, nombre, descripcion, email, telefono, direccion, ciudad, pais, sitio_web, rating_promedio, verificado, fecha_registro, ubicacion, redes_sociales, relevancia, usuario_creador, tipo_documento, numero_documento, activo) FROM stdin;
a98d6834-9795-4f37-93d9-15212419fba9	hotel	Hotel Landmark	Desde una taza de café recién hecho hasta una deliciosa cena. En Landmark ofrecemos una experiencia gastronómica completa marcada por nuestro concepto de productos saludables, locales y orgánicos con el ambiente informal que sólo Landmark puede ofrecer. ¡Smash General y Cierto te están esperando!\n\nEl hotel ofrece una variedad de habitaciones y suites modernas, elegantes y confortables. Cuenta con los restaurantes Cierto, General y Smash, gimnasio, spa y estudio de yoga, bar terraza y piscina con vista panorámica de la ciudad.	asesor@landmark.com	 +57 304 2343158	Calle 14 # 43D 85	Medellin	Colombia	https://landmarkmedellin.com/es/inicio/	4.00	t	2025-07-29 04:50:29.526+00	El Poblado		Alto	admin	RUT	111413	t
887c7ed8-98c8-4017-8968-aeb68c9ddefa	hotel	Hotel Boutique Don Pepe	Don Pepe, Hotel Boutique su Hotel en Santa Marta Colombia, ofrece a sus huéspedes experiencias de viaje que combinan descanso , historia y tradición en la ciudad más antigua de América. Cerca de una de las bahías más atractivas del Caribe, rodeada por la Sierra Nevada, el corazón del mundo según los ancestros, enmarcada en una construcción con siglos de historia, Don pepe se convierte en la opción mas representativa del Hotel de lujo en Santa Marta. 12 habitaciones, cuidadosamente detalladas, terrazas privadas, un Spa de terapias de lujo, el restaurante Bacota con una oferta gastronómica que combina sabores del mundo y la mejor atención de un personal calificado y comprometido lo esperan para atenderlo como usted merece.	asesor@hotelboutiquedonpepe.com	 +57 3218291777	Cl 16 # 1c – 92 Barrio Centro. Santa Marta	Santa Marta	Colombia	https://hotelboutiquedonpepe.com/	5.00	t	2025-07-29 05:10:17.288+00	Centro		Alto	admin	NIT	900433951	t
920235c4-ee96-43fb-9c32-00ea167a34b5	restaurante	Marmi Ristorante	Marmi Ristorante es un lugar innovador inspirado en la cocina italiana con fusiones francesas. Cada detalle de este sitio está planificado, lo que hace que su experiencia desde la entrada sea magnifica, acogedora e inolvidable. El sabor de sus platos y las deliciosas fusiones son la especialidad de la casa. Bienvenidos!	asesor@marmi.com	+57 317 7506407	Carrera 4 No. 26- 40 Locales 113 – 114 - 115	Santa Marta	Colombia	https://marmi.precompro.com/	5.00	t	2025-07-29 05:13:28.064+00	Prado Plaza	marmiristorantebar	media	admin	RUT	255542	t
c4845980-6a2f-4b6c-95ff-b3a988e22669	restaurante	Agua De Rio Café & Bistro	Agua de Río es un estado mental en el cual reina la libertad; donde hay espacio para que todos podamos fluir con la energía de la naturaleza y nos dejemos llevar por la interminable corriente de los ríos que nacen en la Sierra Nevada de Santa Marta. Aquí, el abundante verde de las plantas nos invita a dar un respiro del ritmo acelerado en el que vivimos, para sintonizarnos con la serenidad y el “easy-going” que caracteriza la vida samaria.\n\nEste un espacio donde la diversidad se abraza con entusiasmo y curiosidad, porque entendemos que nuestro valor yace en eso que nos hace únicos, así como en la naturaleza, cada organismo tiene una función para poder mantener el equilibrio y la armonía.\n\nEn Agua de Río buscamos resaltar el valor de local, lo nuestro. Reconocemos la sabiduría que habita en el campo y nos apasiona explorar las tradiciones de nuestra comunidad, experimentando con respeto y cuidado. Aquí abunda la curiosidad, sin embargo, sabemos que lo local es nuestro mayor tesoro.	asesor@aguaderio.com.co	+57 314 - 515 - 9599	Carrera 2 #16 - 47, Centro Histórico	Santa Marta	Colombia	https://aguaderio.com.co/	5.00	t	2025-07-29 05:28:07.78+00	Centro Histórico	aguaderio_smr	media	admin	NIT	806015647-5	t
4a49fc05-fa00-469b-ad9f-b51d92f5c050	tour	Agencia Colombia Experience	Somos una empresa que ofrecemos las mejores experiencias en Turismo, con un componente social asociados a la sostenibilidad del entorno y seguridad a nuestros clientes, superamos las expectativas y cumplimos sueños.\n\nContamos con equipo de colaboradores, profesionales y expertos en servicio al clientes dispuestos a brindar las mejores alternativas de descanso y entretenimiento.	asesor@colombiaexperience.co	(+57) 311-816-1350	Centro Comercial Pasaje Leclerc – Local 7	Cartagena	Colombia	https://colombiaexperience.co/	4.00	t	2025-07-29 04:37:32.98+00			MEDIA	admin	NIT		t
8a0f251f-864a-489b-8a8c-3c9f4f2be408	tour	Asesor	AGENCIA DE VIAJES OPERADORAS	asesor@xperiences.com.co	313 305 2017	CR 44 NO. 58 A 13 SUR	Bogota	Colombia	https://xperiencia.com.co/	4.00	t	2025-07-29 05:47:14.483+00			MEDIA	admin	NIT		t
\.


--
-- TOC entry 4451 (class 0 OID 17022)
-- Dependencies: 233
-- Data for Name: reservas; Type: TABLE DATA; Schema: usr_app; Owner: postgres
--

COPY usr_app.reservas (id_reserva, id_proveedor, id_servicio, id_mayorista, nombre_servicio, descripcion, tipo_servicio, precio, ciudad, activo, estado, observaciones, fecha_creacion, cantida) FROM stdin;
\.


--
-- TOC entry 4448 (class 0 OID 16758)
-- Dependencies: 229
-- Data for Name: restaurantes; Type: TABLE DATA; Schema: usr_app; Owner: postgres
--

COPY usr_app.restaurantes (id_restaurante, tipo_cocina, horario_apertura, horario_cierre, capacidad, menu_url, tiene_terraza, apto_celiacos, apto_vegetarianos, reservas_requeridas, entrega_a_domicilio, wifi, zonas_comunes, auditorio, pet_friendly, eventos, menu_vegana, bufete, catering, menu_infantil, parqueadero, terraza, sillas_bebe, decoraciones_fechas_especiales, rampa_discapacitados, aforo_maximo, tipo_comida, precio_ascendente) FROM stdin;
920235c4-ee96-43fb-9c32-00ea167a34b5	Italiana	12:01:00	22:00:00	50	https://marmi.precompro.com/	f	f	f	t	t	t	f	f	f	f	f	f	f	t	f	t	f	t	f	100	Gourmet	32000.00
c4845980-6a2f-4b6c-95ff-b3a988e22669	Bar Café	08:00:00	22:30:00	20	https://menupp.co/aguaderio	f	f	f	f	t	t	t	f	f	t	f	f	f	f	f	t	f	t	f	20	Colombiana	21000.00
\.


--
-- TOC entry 4443 (class 0 OID 16687)
-- Dependencies: 224
-- Data for Name: rutas; Type: TABLE DATA; Schema: usr_app; Owner: postgres
--

COPY usr_app.rutas (id, nombre, descripcion, puntos_interes, recomendada, origen, destino, precio, duracion_estimada, activo) FROM stdin;
\.


--
-- TOC entry 4441 (class 0 OID 16634)
-- Dependencies: 221
-- Data for Name: servicios; Type: TABLE DATA; Schema: usr_app; Owner: postgres
--

COPY usr_app.servicios (id_servicio, proveedor_id, nombre, descripcion, tipo_servicio, precio, moneda, activo, fecha_creacion, fecha_actualizacion, relevancia, ciudad, departamento, ubicacion, detalles_del_servicio) FROM stdin;
eae51613-f27e-41a5-88b0-59ec02c01684	4a49fc05-fa00-469b-ad9f-b51d92f5c050	Pasadía en Isla Kokomo	DeIncluye: Almuerzo típico, Cóctel de bienvenida	experiencias	79.00	USD	t	2025-07-29 06:48:46.078+00	2025-07-29 06:48:46.078+00	MEDIA	Cartagena	Bolivar		{"tipo_tour":"Cultural","duracion":"Día completo","grupo_objetivo":"Individual","incluye":{"transporte":true,"guia":true,"alimentacion":true,"entradas_sitios":true},"dificultad":"Media","disponibilidad":{"fechas":"Todos los dias","horarios":"08:00 a 17:00"},"idiomas":{"espanol":true,"ingles":true,"otros":""},"extras":{"fotografias_profesionales":false,"seguros_viaje":true},"parqueadero":true,"pet_friendly":true,"grupo_maximo":10,"equipamiento_requerido":"Ropa Comda","punto_de_encuentro":"Club"}
b975406c-3ae6-4105-9e74-15bef4477450	887c7ed8-98c8-4017-8968-aeb68c9ddefa	Habitación Don Pepe Estandar	encantadoras habitaciones de 23 metros cuadrados ubicadas en la parte baja del hotel, equipadas con lo necesario para hacer de su estancia la mas amena de sus experiencias.	alojamiento	200000.00	COP	t	2025-07-29 06:31:56.81+00	2025-07-30 01:41:31.007+00	ALTA	Santa Marta	Magdalena	Cl 16 # 1c – 92 Barrio Centro	{"tipo_alojamiento":"Hotel","habitacion":"Estándar","capacidad":2,"servicios_incluidos":{"desayuno":false,"wifi":true,"aire_acondicionado":true,"tv":true,"caja_fuerte":false,"piscina":false,"parqueadero":false,"pet_friendly":false,"room_service":false,"ascensor":false,"planta_energia":false},"politica_reservas":{"check_in":"15:00","check_out":"12:00","cancelaciones":"Cancelación gratuita hasta 24 horas antes"},"precios":{"por_noche":true,"por_persona":false,"paquetes_especiales":false},"extras":{"transporte_aeropuerto":false,"actividades_hotel":false,"spa":false,"gimnasio":false}}
7465d99a-8cdb-4289-9ce0-0f7cd8185bb1	4a49fc05-fa00-469b-ad9f-b51d92f5c050	Pasadía todo incluido Isla Bora Bora	Desconéctate y vive un relajante día de playa en este paraíso! Bora Bora Beach Club es realmente una encantadora isla club para relajarse al ritmo de la música chill out, bajo el radiante sol y disfrutando de un delicioso cóctel a la orilla del mar.\n\n\n	experiencias	95.00	USD	t	2025-07-29 06:48:46.078+00	2025-07-29 06:48:46.078+00	MEDIA	Cartagena	Bolivar		{"tipo_tour":"Cultural","duracion":"Día completo","grupo_objetivo":"Individual","incluye":{"transporte":true,"guia":true,"alimentacion":true,"entradas_sitios":true},"dificultad":"Media","disponibilidad":{"fechas":"Todos los dias","horarios":"08:00 a 17:00"},"idiomas":{"espanol":true,"ingles":true,"otros":""},"extras":{"fotografias_profesionales":false,"seguros_viaje":true},"parqueadero":true,"pet_friendly":true,"grupo_maximo":10,"equipamiento_requerido":"Ropa Comda","punto_de_encuentro":"Club"}
3d3551fa-4202-4452-bc3d-87dd8835f77b	a98d6834-9795-4f37-93d9-15212419fba9	Habitación Duplex King Suite	La Duplex King Suite es la mejor habitación para aquellos que buscan una estadía lujosa y espaciosa en Medellín. Esta suite de dos pisos cuenta con una cama tamaño king, baño completo y balcón en el piso inferior. En el piso superior, encontrará una cama tamaño queen, baño completo, estudio, amplia sala de estar y jacuzzi, lo que la hace perfecta para familias numerosas..	alojamiento	700000.00	COP	t	2025-07-29 06:19:04.378+00	2025-07-29 21:07:51.864+00	MEDIA	Medellín	Antioquia	Calle 14 # 43D 85	{"tipo_alojamiento":"Hotel","habitacion":"Suite","capacidad":2,"servicios_incluidos":{"desayuno":true,"wifi":true,"aire_acondicionado":true,"tv":true,"caja_fuerte":false,"piscina":false,"parqueadero":false,"pet_friendly":false,"room_service":false,"ascensor":false,"planta_energia":false},"politica_reservas":{"check_in":"15:00","check_out":"12:00","cancelaciones":"Cancelación gratuita hasta 24 horas antes"},"precios":{"por_noche":true,"por_persona":false,"paquetes_especiales":false},"extras":{"transporte_aeropuerto":false,"actividades_hotel":true,"spa":false,"gimnasio":false}}
019f2d43-8fa0-4414-80f5-fe2180942fe5	920235c4-ee96-43fb-9c32-00ea167a34b5	Cena Amor y Amistad	Musica en vivo, Celebración de Amor y Amistad. Combo Cena + Bebida	restaurante	200000.00	COP	t	2025-07-29 06:05:27.468+00	2025-07-29 21:08:51.803+00	ALTA	Santa Marta	Magdalena	Carrera 4 # 26 - 40 Prado Plaza, Santa Marta, Magdalena	{"tipo_establecimiento":"Restaurante gourmet","estilo_gastronomico":"Fusión","capacidad":20,"servicios":{"comida_en_mesa":true,"para_llevar":false,"domicilio":false,"buffet":false,"catering":false},"horarios":{"desayuno":false,"almuerzo":true,"cena":false,"veinticuatro_horas":false},"extras":{"musica_en_vivo":true,"catas_de_vinos":false,"maridajes":false,"menu_degustacion":false},"promociones":{"happy_hour":false,"descuentos_por_grupo":false,"menu":true},"servicios_adicionales":{"piscina":false,"parqueadero":false,"pet_friendly":false,"room_service":false,"ascensor":false,"planta_energia":false,"rampa_discapacitados":false}}
0ac1364c-1e81-4166-8162-e3bc35ff4320	a98d6834-9795-4f37-93d9-15212419fba9	Habitación Deluxe Queen	La habitación Deluxe Queen con vista al jardín cuenta con vista a nuestro patio interior, lo que le da a la habitación un ambiente fresco y tranquilo que lo ayudará a relajarse y descansar después de explorar la ciudad. Perfecto para personas que viajan solas o parejas que desean un lugar tranquilo mientras disfrutan de una ubicación central.	alojamiento	450000.00	COP	t	2025-07-29 06:19:04.378+00	2025-07-29 21:10:07.525+00	MEDIA	Medellín	Antioquia	Calle 14 # 43D 85	{"tipo_alojamiento":"Hotel","habitacion":"Suite","capacidad":2,"servicios_incluidos":{"desayuno":true,"wifi":true,"aire_acondicionado":true,"tv":true,"caja_fuerte":false,"piscina":false,"parqueadero":false,"pet_friendly":false,"room_service":false,"ascensor":false,"planta_energia":false},"politica_reservas":{"check_in":"15:00","check_out":"12:00","cancelaciones":"Cancelación gratuita hasta 24 horas antes"},"precios":{"por_noche":true,"por_persona":false,"paquetes_especiales":false},"extras":{"transporte_aeropuerto":false,"actividades_hotel":true,"spa":false,"gimnasio":false}}
fcc1ad1e-e8a1-4130-8f99-16101cab1bef	920235c4-ee96-43fb-9c32-00ea167a34b5	Pizza  Napolitana	Disfruta de unas pizza original napolitana, hechas por un chef italiano especializado	restaurante	50000.00	COP	t	2025-07-29 06:08:32.666+00	2025-07-29 06:08:32.666+00	ALTA	Santa Marta	Magdalena	Carrera 4 # 26 - 40 Prado Plaza, Santa Marta, Magdalena	{"tipo_establecimiento":"Restaurante gourmet","estilo_gastronomico":"Internacional","capacidad":20,"servicios":{"comida_en_mesa":true,"para_llevar":false,"domicilio":false,"buffet":false,"catering":false},"horarios":{"desayuno":true,"almuerzo":true,"cena":true,"veinticuatro_horas":false},"extras":{"musica_en_vivo":true,"catas_de_vinos":false,"maridajes":false,"menu_degustacion":false},"promociones":{"happy_hour":false,"descuentos_por_grupo":false,"menu":true},"servicios_adicionales":{"piscina":false,"parqueadero":true,"pet_friendly":false,"room_service":false,"ascensor":false,"planta_energia":false,"rampa_discapacitados":false}}
b1db139f-3ab9-4958-a8e5-dbec4b662b01	920235c4-ee96-43fb-9c32-00ea167a34b5	Pastas Alfredo	Disfruta de unas pastas alfredo únicas, hechas por un chef italiano especializado	restaurante	30000.00	COP	t	2025-07-29 06:08:32.666+00	2025-07-29 06:08:32.666+00	MEDIA	Santa Marta	Magdalena	Carrera 4 # 26 - 40 Prado Plaza, Santa Marta, Magdalena	{"tipo_establecimiento":"Restaurante gourmet","estilo_gastronomico":"Internacional","capacidad":20,"servicios":{"comida_en_mesa":true,"para_llevar":false,"domicilio":false,"buffet":false,"catering":false},"horarios":{"desayuno":true,"almuerzo":true,"cena":true,"veinticuatro_horas":false},"extras":{"musica_en_vivo":true,"catas_de_vinos":false,"maridajes":false,"menu_degustacion":false},"promociones":{"happy_hour":false,"descuentos_por_grupo":false,"menu":true},"servicios_adicionales":{"piscina":false,"parqueadero":true,"pet_friendly":false,"room_service":false,"ascensor":false,"planta_energia":false,"rampa_discapacitados":false}}
bf83f949-536a-4b0f-897a-39d680870634	920235c4-ee96-43fb-9c32-00ea167a34b5	Pizza  Vegetariana	Para ti que estas en el mundo vegano, tenemos esta unica opcion para satisfacer	restaurante	60000.00	COP	t	2025-07-29 06:08:32.666+00	2025-07-29 06:08:32.666+00	BAJA	Santa Marta	Magdalena	Carrera 4 # 26 - 40 Prado Plaza, Santa Marta, Magdalena	{"tipo_establecimiento":"Restaurante gourmet","estilo_gastronomico":"Internacional","capacidad":20,"servicios":{"comida_en_mesa":true,"para_llevar":false,"domicilio":false,"buffet":false,"catering":false},"horarios":{"desayuno":true,"almuerzo":true,"cena":true,"veinticuatro_horas":false},"extras":{"musica_en_vivo":true,"catas_de_vinos":false,"maridajes":false,"menu_degustacion":false},"promociones":{"happy_hour":false,"descuentos_por_grupo":false,"menu":true},"servicios_adicionales":{"piscina":false,"parqueadero":true,"pet_friendly":false,"room_service":false,"ascensor":false,"planta_energia":false,"rampa_discapacitados":false}}
825a0035-0426-4489-9a25-2c4bb5eed93c	a98d6834-9795-4f37-93d9-15212419fba9	Habitación Suite	Habitación Suite	alojamiento	200000.00	COP	t	2025-07-29 06:19:04.378+00	2025-07-29 06:19:04.378+00	MEDIA	Medellín	Antioquia	Calle 14 # 43D 85	{"tipo_alojamiento":"Hotel","habitacion":"Suite","capacidad":2,"servicios_incluidos":{"desayuno":true,"wifi":true,"aire_acondicionado":true,"tv":true,"caja_fuerte":false,"piscina":false,"parqueadero":false,"pet_friendly":false,"room_service":false,"ascensor":false,"planta_energia":false},"politica_reservas":{"check_in":"15:00","check_out":"12:00","cancelaciones":"Cancelación gratuita hasta 24 horas antes"},"precios":{"por_noche":true,"por_persona":false,"paquetes_especiales":false},"extras":{"transporte_aeropuerto":false,"actividades_hotel":true,"spa":false,"gimnasio":false}}
3805fdc3-1e10-4958-bc84-f293469f6e7c	a98d6834-9795-4f37-93d9-15212419fba9	Habitación Estandar	Habitación Estandar	alojamiento	400000.00	COP	t	2025-07-29 06:19:04.378+00	2025-07-29 06:19:04.378+00	MEDIA	Medellín	Antioquia	Calle 14 # 43D 85	{"tipo_alojamiento":"Hotel","habitacion":"Suite","capacidad":2,"servicios_incluidos":{"desayuno":true,"wifi":true,"aire_acondicionado":true,"tv":true,"caja_fuerte":false,"piscina":false,"parqueadero":false,"pet_friendly":false,"room_service":false,"ascensor":false,"planta_energia":false},"politica_reservas":{"check_in":"15:00","check_out":"12:00","cancelaciones":"Cancelación gratuita hasta 24 horas antes"},"precios":{"por_noche":true,"por_persona":false,"paquetes_especiales":false},"extras":{"transporte_aeropuerto":false,"actividades_hotel":true,"spa":false,"gimnasio":false}}
13a832f8-0ab0-4e3a-a9b5-cbfe9a608c2b	920235c4-ee96-43fb-9c32-00ea167a34b5	Servicio de prueba	alojamiento 	alojamiento	32999.00	COP	f	2025-07-29 06:26:50.331+00	2025-07-29 06:26:50.331+00	Baja	Monteria 	Cordoba	por hi 	wef w4t w4ta
c021316c-4b9c-4452-a48a-17b78329f033	8a0f251f-864a-489b-8a8c-3c9f4f2be408	Parapente en la Calera	Parapente en La Calera: Vuela Sobre los Andes Colombianos\nSi buscas una experiencia llena de emoción y paisajes impresionantes, el parapente en La Calera es la aventura perfecta. Siente la libertad de volar mientras disfrutas de una vista panorámica única de Bogotá, los cerros orientales y los verdes valles que rodean la región.\n\n	experiencias	250000.00	COP	t	2025-07-29 06:59:56.05+00	2025-07-29 06:59:56.05+00	ALTA	Bogotá	Cundinamarca	Calle 100 # 15-20	{"tipo_tour":"Aventura","duracion":"Medio día","grupo_objetivo":"Individual","incluye":{"transporte":true,"guia":true,"alimentacion":false,"entradas_sitios":false},"dificultad":"Alta","disponibilidad":{"fechas":"Todos los dias","horarios":"08:00 a 17:00"},"idiomas":{"espanol":true,"ingles":true,"otros":" "},"extras":{"fotografias_profesionales":false,"seguros_viaje":false},"parqueadero":false,"pet_friendly":false,"grupo_maximo":10,"equipamiento_requerido":"\\nRopa cómoda y bastante abrigada (Chaqueta, saco, guantes).\\nZapatos cómodos de amarrar, preferiblemente tenis o botas (no sandalias, no tacones).\\nProtector solar, gafas para sol, sombrilla.\\nLlevar bebidas (hidratantes) y sus propios alimentos (refrigerio, almuerzo, pasabocas).","punto_de_encuentro":"Club"}
991c3412-f883-42f8-b61f-0051b9af4e50	8a0f251f-864a-489b-8a8c-3c9f4f2be408	Cordillera Blanca Perú	La Cordillera Blanca es un destino de montaña situado en la ciudad de Huaraz, en el norte de Perú. Es una de las cadenas montañosas más espectaculares del mundo, con más de 50 picos que superan los 5.000 metros de altura. Esta majestuosa cordillera se encuentra dentro del Parque Nacional Huascarán y es el hogar de la montaña más alta de Perú.	experiencias	4800000.00	COP	t	2025-07-29 07:03:45.014+00	2025-07-29 07:03:45.014+00	ALTA	Haruaz	Haruaz	Haruaz - PERU 	{"tipo_tour":"Aventura","duracion":"Varios días","grupo_objetivo":"Individual","incluye":{"transporte":true,"guia":true,"alimentacion":true,"entradas_sitios":true},"dificultad":"Alta","disponibilidad":{"fechas":"Todos los dias","horarios":"08:00 a 17:00"},"idiomas":{"espanol":false,"ingles":false,"otros":""},"extras":{"fotografias_profesionales":true,"seguros_viaje":true},"parqueadero":true,"pet_friendly":false,"grupo_maximo":11,"equipamiento_requerido":"Chaqueta y pantalón capa externa\\nGuantes bajas temperaturas (-20°)\\nGorro\\n3 pares de medias térmicas\\nChaqueta impermeable\\nPantalón de secado rápido\\nPantalón impermeable\\nSaco polar o chaqueta de plumas\\nLicra camiseta\\nCamiseta térmica\\nKit de aseo personal\\nCantimplora o camel back\\nGafas con protección UV\\nLinterna frontal (con baterías de repuesto)\\nBastones de caminata\\nCámara fotográfica\\nPilas extras\\nTener experiencia en alta montaña (caminata sobre glaciar)\\nBuen estado físico\\nDinero extra para gastos no estipulados\\nLa mejor actitud.","punto_de_encuentro":"Parque Principal"}
2926ca3b-74ce-4b92-ba40-6ca99308412e	887c7ed8-98c8-4017-8968-aeb68c9ddefa	Habitación Luxury	Habitaciones de mayor tamaño. 29 metros aproximadamente que permiten acomodación triple en tres de ellas. Los balcones y terrazas hacen parte de algunas habitaciones de esta categoría.  Ubicadas en la primera o segunda planta .	alojamiento	300000.00	COP	t	2025-07-29 06:33:10.744+00	2025-07-29 21:08:34.864+00	MEDIA	Santa Marta	Magdalena	Cl 16 # 1c – 92 Barrio Centro	{"tipo_alojamiento":"Hotel","habitacion":"Premium","capacidad":"3","servicios_incluidos":{"desayuno":false,"wifi":true,"aire_acondicionado":true,"tv":true,"caja_fuerte":false,"piscina":false,"parqueadero":false,"pet_friendly":true,"room_service":true,"ascensor":false,"planta_energia":false},"politica_reservas":{"check_in":"15:00","check_out":"12:00","cancelaciones":"Cancelación gratuita hasta 24 horas antes"},"precios":{"por_noche":true,"por_persona":false,"paquetes_especiales":false},"extras":{"transporte_aeropuerto":false,"actividades_hotel":false,"spa":false,"gimnasio":false}}
750cad05-1f81-4f7e-97c3-4e2e96190f47	887c7ed8-98c8-4017-8968-aeb68c9ddefa	Habitación Luxury Twin	Una linda habitación con un tamaño de 32 metros aproximadamente que permiten acomodación doble o triple, cuenta con 2 Camas Semi dobles con opción de añadir 1 Cama sencilla adicional. Ubicada en la primera planta	alojamiento	350000.00	COP	t	2025-07-29 06:34:28.191+00	2025-07-30 01:41:56.079+00	ALTA	Santa Marta	Magdalena	Cl 16 # 1c – 92 Barrio Centro	{"tipo_alojamiento":"Hotel","habitacion":"Suite","capacidad":"3","servicios_incluidos":{"desayuno":true,"wifi":true,"aire_acondicionado":true,"tv":true,"caja_fuerte":false,"piscina":false,"parqueadero":false,"pet_friendly":true,"room_service":false,"ascensor":false,"planta_energia":false},"politica_reservas":{"check_in":"15:00","check_out":"12:00","cancelaciones":"Cancelación gratuita hasta 24 horas antes"},"precios":{"por_noche":true,"por_persona":false,"paquetes_especiales":false},"extras":{"transporte_aeropuerto":false,"actividades_hotel":false,"spa":false,"gimnasio":false}}
e2a0dc86-3905-4d13-866a-00cb826cc7a3	a98d6834-9795-4f37-93d9-15212419fba9	Habitación Doble Queen con Balcón	La Doble Queen con balcón tiene una cama adicional y es ideal para amigos que viajan juntos o familias que necesitan un poco más de espacio. Además, cuenta con un balcón desde el que se puede disfrutar del clima templado de Medellín.	alojamiento	450000.00	COP	t	2025-07-29 06:19:04.378+00	2025-07-30 01:42:14.931+00	MEDIA	Medellín	Antioquia	Calle 14 # 43D 85	{"tipo_alojamiento":"Hotel","habitacion":"Suite","capacidad":2,"servicios_incluidos":{"desayuno":true,"wifi":true,"aire_acondicionado":true,"tv":true,"caja_fuerte":false,"piscina":false,"parqueadero":false,"pet_friendly":false,"room_service":false,"ascensor":false,"planta_energia":false},"politica_reservas":{"check_in":"15:00","check_out":"12:00","cancelaciones":"Cancelación gratuita hasta 24 horas antes"},"precios":{"por_noche":true,"por_persona":false,"paquetes_especiales":false},"extras":{"transporte_aeropuerto":false,"actividades_hotel":true,"spa":false,"gimnasio":false}}
\.


--
-- TOC entry 4446 (class 0 OID 16730)
-- Dependencies: 227
-- Data for Name: transportes; Type: TABLE DATA; Schema: usr_app; Owner: postgres
--

COPY usr_app.transportes (id_transporte, tipo_vehiculo, modelo, anio, placa, capacidad, aire_acondicionado, wifi, disponible, combustible, seguro_vigente, fecha_mantenimiento) FROM stdin;
\.


--
-- TOC entry 4439 (class 0 OID 16595)
-- Dependencies: 219
-- Data for Name: usuarios; Type: TABLE DATA; Schema: usr_app; Owner: postgres
--

COPY usr_app.usuarios (id, nombre, apellido, email, "contraseña", fecha_registro, ultimo_login, activo, tipo_usuario) FROM stdin;
f647ef5e-a997-452f-88b4-a49482fe1e63	Guillermo	Bedoya Ortega	guillermobedoya104@gmail.com	$2b$12$aR1WovS5AiD3BYAPow7mP.FaMV6E4xt99CPRBdQx8ytjTNV8mNqyu	2025-07-07 22:41:05.796699+00	2025-07-31 00:16:04.792506+00	t	admin
01a8ada7-5bd3-4cf2-b423-3b396f9725c2	Asesor	Agua de Río	asesor@aguaderio.com.co	$2b$12$CUOxgRGj0YwmWgNA0Fgw4OBfTAOOtxlDIz4PfAaqREc28FBSD2f6y	2025-07-29 04:32:16.270071+00	2025-08-08 21:13:55.086621+00	t	proveedor
25082cdb-48c1-4f14-aa4a-dcc05211e184	Asesor	hotelboutiquedonpepe	asesor@hotelboutiquedonpepe.com	$2b$12$qPfxui2qqBz9gOenu6qBQexvTwKw7b15LmmpOGwXrSTgPreIkWzmm	2025-07-29 04:08:43.254988+00	2025-08-08 21:14:28.420519+00	t	proveedor
335daa2b-5761-46b2-92f5-a65ffff03277	Luis gabriel	Quiceno espitia	quiceno@email.com	$2b$12$zg9Di/Upb/mecp6UHXzhRuyh.MeHKg4PRqA1tbnuEwDMNUhc5Za1e	2025-02-07 02:21:14.915+00	2025-08-08 23:14:49.921259+00	t	admin
bf005c77-72aa-4771-aed9-b35d46a56ef0	Asesor	Xperience	asesor@xperiences.com.co	$2b$12$XGjXqr.rNFHiuw5SRP7Hpe53gZecFQ3FUSUFgYP61nzBi6vUVAisi	2025-07-29 04:52:49.81493+00	2025-08-08 23:16:06.903228+00	t	proveedor
8140adb9-85ec-4817-b340-0213ec6e9de9	Asesor	marmi	asesor@marmi.com	$2b$12$6GhqDVLHe2OKqtoJfpnWLOCCG74XjEpWAZ0KBnH/HnJf/2f2HeyY6	2025-07-29 04:17:36.179405+00	2025-07-29 05:58:41.528882+00	t	proveedor
543d6f47-61cc-411f-90e9-da09cf470b87	mayorista	de prueba	mayorista@gmail.com	$2b$12$Rs.bco4iZqiUbjV1ru5fteA7rnxaHE2kmewxOUJ6JepHjYCm7N1RK	2025-07-29 05:47:15.665239+00	2025-07-31 00:14:18.539951+00	t	mayorista
164fe8d0-aca7-4421-a5b2-0f20ed4be367	Asesor	Landmark	asesor@landmark.com	$2b$12$clYakNP.DlSCIwSGnnR7AuCs07Z9PIIbmOoyWdizms3oxLy5XDST2	2025-07-29 03:44:47.917404+00	2025-07-31 00:19:19.465076+00	t	proveedor
d09bb133-1a3e-443f-85e4-9fe791870c9b	Asesor	Colombia Experience	asesor@colombiaexperience.co	$2b$12$9wEL2nf6eXB9nXDm9OF/tuKUXHf1wBxgyo63y7Kp0KKmX9S0GhaXC	2025-07-29 04:44:43.03009+00	2025-07-29 06:44:28.542692+00	t	proveedor
\.


--
-- TOC entry 4444 (class 0 OID 16696)
-- Dependencies: 225
-- Data for Name: viajes; Type: TABLE DATA; Schema: usr_app; Owner: postgres
--

COPY usr_app.viajes (id, ruta_id, fecha_inicio, fecha_fin, capacidad_total, capacidad_disponible, precio, guia_asignado, estado, id_transportador, activo) FROM stdin;
\.


--
-- TOC entry 4285 (class 2606 OID 16776)
-- Name: experiencias experiencias_pkey; Type: CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.experiencias
    ADD CONSTRAINT experiencias_pkey PRIMARY KEY (id_experiencia);


--
-- TOC entry 4276 (class 2606 OID 16719)
-- Name: fechas_bloqueadas fechas_bloqueadas_pkey; Type: CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.fechas_bloqueadas
    ADD CONSTRAINT fechas_bloqueadas_pkey PRIMARY KEY (id);


--
-- TOC entry 4269 (class 2606 OID 16681)
-- Name: fotos fotos_pkey; Type: CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.fotos
    ADD CONSTRAINT fotos_pkey PRIMARY KEY (id);


--
-- TOC entry 4281 (class 2606 OID 16752)
-- Name: hoteles hoteles_pkey; Type: CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.hoteles
    ADD CONSTRAINT hoteles_pkey PRIMARY KEY (id_hotel);


--
-- TOC entry 4262 (class 2606 OID 16620)
-- Name: proveedores proveedores_email_key; Type: CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.proveedores
    ADD CONSTRAINT proveedores_email_key UNIQUE (email);


--
-- TOC entry 4264 (class 2606 OID 16618)
-- Name: proveedores proveedores_pkey; Type: CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.proveedores
    ADD CONSTRAINT proveedores_pkey PRIMARY KEY (id_proveedor);


--
-- TOC entry 4283 (class 2606 OID 16764)
-- Name: restaurantes restaurantes_pkey; Type: CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.restaurantes
    ADD CONSTRAINT restaurantes_pkey PRIMARY KEY (id_restaurante);


--
-- TOC entry 4272 (class 2606 OID 16695)
-- Name: rutas rutas_pkey; Type: CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.rutas
    ADD CONSTRAINT rutas_pkey PRIMARY KEY (id);


--
-- TOC entry 4267 (class 2606 OID 16644)
-- Name: servicios servicios_pkey; Type: CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.servicios
    ADD CONSTRAINT servicios_pkey PRIMARY KEY (id_servicio);


--
-- TOC entry 4279 (class 2606 OID 16739)
-- Name: transportes transportes_pkey; Type: CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.transportes
    ADD CONSTRAINT transportes_pkey PRIMARY KEY (id_transporte);


--
-- TOC entry 4258 (class 2606 OID 16606)
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- TOC entry 4260 (class 2606 OID 16604)
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- TOC entry 4274 (class 2606 OID 16705)
-- Name: viajes viajes_pkey; Type: CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.viajes
    ADD CONSTRAINT viajes_pkey PRIMARY KEY (id);


--
-- TOC entry 4277 (class 1259 OID 16729)
-- Name: idx_fechas_bloqueadas_servicio; Type: INDEX; Schema: usr_app; Owner: postgres
--

CREATE INDEX idx_fechas_bloqueadas_servicio ON usr_app.fechas_bloqueadas USING btree (servicio_id);


--
-- TOC entry 4270 (class 1259 OID 16728)
-- Name: idx_fotos_servicio; Type: INDEX; Schema: usr_app; Owner: postgres
--

CREATE INDEX idx_fotos_servicio ON usr_app.fotos USING btree (servicio_id);


--
-- TOC entry 4265 (class 1259 OID 16725)
-- Name: idx_servicios_proveedor; Type: INDEX; Schema: usr_app; Owner: postgres
--

CREATE INDEX idx_servicios_proveedor ON usr_app.servicios USING btree (proveedor_id);


--
-- TOC entry 4293 (class 2606 OID 16777)
-- Name: experiencias experiencias_id_fkey; Type: FK CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.experiencias
    ADD CONSTRAINT experiencias_id_fkey FOREIGN KEY (id_experiencia) REFERENCES usr_app.proveedores(id_proveedor) ON DELETE CASCADE;


--
-- TOC entry 4289 (class 2606 OID 16720)
-- Name: fechas_bloqueadas fechas_bloqueadas_servicio_id_fkey; Type: FK CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.fechas_bloqueadas
    ADD CONSTRAINT fechas_bloqueadas_servicio_id_fkey FOREIGN KEY (servicio_id) REFERENCES usr_app.servicios(id_servicio) ON DELETE CASCADE;


--
-- TOC entry 4287 (class 2606 OID 16682)
-- Name: fotos fotos_servicio_id_fkey; Type: FK CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.fotos
    ADD CONSTRAINT fotos_servicio_id_fkey FOREIGN KEY (servicio_id) REFERENCES usr_app.servicios(id_servicio) ON DELETE CASCADE;


--
-- TOC entry 4291 (class 2606 OID 16753)
-- Name: hoteles hoteles_id_fkey; Type: FK CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.hoteles
    ADD CONSTRAINT hoteles_id_fkey FOREIGN KEY (id_hotel) REFERENCES usr_app.proveedores(id_proveedor) ON DELETE CASCADE;


--
-- TOC entry 4292 (class 2606 OID 16765)
-- Name: restaurantes restaurantes_id_fkey; Type: FK CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.restaurantes
    ADD CONSTRAINT restaurantes_id_fkey FOREIGN KEY (id_restaurante) REFERENCES usr_app.proveedores(id_proveedor) ON DELETE CASCADE;


--
-- TOC entry 4286 (class 2606 OID 16645)
-- Name: servicios servicios_proveedor_id_fkey; Type: FK CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.servicios
    ADD CONSTRAINT servicios_proveedor_id_fkey FOREIGN KEY (proveedor_id) REFERENCES usr_app.proveedores(id_proveedor) ON DELETE CASCADE;


--
-- TOC entry 4290 (class 2606 OID 16740)
-- Name: transportes transportes_id_fkey; Type: FK CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.transportes
    ADD CONSTRAINT transportes_id_fkey FOREIGN KEY (id_transporte) REFERENCES usr_app.proveedores(id_proveedor) ON DELETE CASCADE;


--
-- TOC entry 4288 (class 2606 OID 16706)
-- Name: viajes viajes_ruta_id_fkey; Type: FK CONSTRAINT; Schema: usr_app; Owner: postgres
--

ALTER TABLE ONLY usr_app.viajes
    ADD CONSTRAINT viajes_ruta_id_fkey FOREIGN KEY (ruta_id) REFERENCES usr_app.rutas(id) ON DELETE CASCADE;


-- Completed on 2025-08-09 15:15:09 -05

--
-- PostgreSQL database dump complete
--

