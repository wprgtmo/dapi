ALTER TABLE IF EXISTS enterprise.users
    ADD COLUMN receive_notifications boolean DEFAULT False;

DROP TABLE IF EXISTS resources.event_roles;

CREATE TABLE IF NOT EXISTS resources.event_roles
(
    id integer NOT NULL DEFAULT nextval('resources.event_roles_id_seq'::regclass),
    name character varying(50) COLLATE pg_catalog."default" NOT NULL,
    description character varying(100) COLLATE pg_catalog."default" NOT NULL,
    created_by character varying(50) COLLATE pg_catalog."default" NOT NULL,
    created_date timestamp without time zone NOT NULL,
    CONSTRAINT event_roles_pkey PRIMARY KEY (id),
    CONSTRAINT event_roles_name_key UNIQUE (name)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS resources.event_roles
    OWNER to postgres;

    
INSERT INTO resources.event_roles(name, description, created_by, created_date)
		VALUES ('PLAYER', 'JUGADOR', 'miry', '2023-05-12 00:00:00');
	INSERT INTO resources.event_roles(name, description, created_by, created_date)
		VALUES ('REFEREE', 'ARBITRO', 'miry', '2023-05-12 00:00:00');
	INSERT INTO resources.event_roles(name, description, created_by, created_date)
		VALUES ('JOURNALIST', 'PERIODISTA', 'miry', '2023-05-12 00:00:00');