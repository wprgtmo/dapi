INSERT INTO enterprise.profile_type(
	id, name, description, created_by, created_date, by_default, is_active)
	VALUES (8, 'EVENTADMON', 'Administrador de Evento', 'miry', '2023-08-15 02:31:28.714478', false, true);


CREATE TABLE IF NOT EXISTS enterprise.profile_event_admon
(
    profile_id character varying COLLATE pg_catalog."default" NOT NULL,
    updated_by character varying COLLATE pg_catalog."default" NOT NULL,
    updated_date date NOT NULL,
    CONSTRAINT profile_event_admon_pkey PRIMARY KEY (profile_id),
    CONSTRAINT profile_event_admon_profile_id_fkey FOREIGN KEY (profile_id)
        REFERENCES enterprise.profile_member (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT profile_event_admon_updated_by_fkey FOREIGN KEY (updated_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
TABLESPACE pg_default;
ALTER TABLE IF EXISTS enterprise.profile_event_admon
    OWNER to postgres;



CREATE TABLE IF NOT EXISTS resources.ext_types
(
    id integer NOT NULL DEFAULT nextval('resources.ext_types_id_seq'::regclass),
    ext_code character varying(10) COLLATE pg_catalog."default" NOT NULL,
    type_file character varying(10) COLLATE pg_catalog."default" NOT NULL,
    created_by character varying(50) COLLATE pg_catalog."default" NOT NULL,
    created_date timestamp without time zone NOT NULL,
    CONSTRAINT ext_types_pkey PRIMARY KEY (id),
    CONSTRAINT ext_types_ext_code_key UNIQUE (ext_code)
)
TABLESPACE pg_default;
ALTER TABLE IF EXISTS resources.ext_types
    OWNER to postgres;


# restaurar backup de la tabla ext_type
# restaurar backup de las provincias de Cuba
