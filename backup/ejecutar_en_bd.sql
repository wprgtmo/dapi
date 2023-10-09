
--DROP TABLE IF EXISTS events.domino_tables;

CREATE TABLE IF NOT EXISTS events.domino_tables
(
    id character varying COLLATE pg_catalog."default" NOT NULL,
    tourney_id character varying COLLATE pg_catalog."default" NOT NULL,
    table_number integer NOT NULL,
    is_smart boolean NOT NULL,
    amount_bonus integer NOT NULL,
    image text COLLATE pg_catalog."default",
    is_active boolean NOT NULL,
    created_by character varying COLLATE pg_catalog."default" NOT NULL,
    created_date date NOT NULL,
    updated_by character varying COLLATE pg_catalog."default",
    updated_date date NOT NULL,
    CONSTRAINT domino_tables_pkey PRIMARY KEY (id),
    CONSTRAINT idx_number_table UNIQUE (tourney_id, table_number),
    CONSTRAINT domino_tables_created_by_fkey FOREIGN KEY (created_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT domino_tables_tourney_id_fkey FOREIGN KEY (tourney_id)
        REFERENCES events.tourney (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT domino_tables_updated_by_fkey FOREIGN KEY (updated_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS events.domino_tables
    OWNER to postgres;

--DROP TABLE IF EXISTS events.files_tables;

CREATE TABLE IF NOT EXISTS events.files_tables
(
    id character varying COLLATE pg_catalog."default" NOT NULL,
    table_id character varying COLLATE pg_catalog."default" NOT NULL,
    "position" integer NOT NULL,
    is_ready boolean NOT NULL,
    CONSTRAINT files_tables_pkey PRIMARY KEY (id),
    CONSTRAINT files_tables_table_id_fkey FOREIGN KEY (table_id)
        REFERENCES events.domino_tables (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS events.files_tables
    OWNER to postgres;



CREATE TABLE IF NOT EXISTS events.domino_rounds
(
    id character varying COLLATE pg_catalog."default" NOT NULL,
    tourney_id character varying COLLATE pg_catalog."default" NOT NULL,
    round_number integer NOT NULL,
    summary text COLLATE pg_catalog."default",
    start_date timestamp without time zone NOT NULL,
    close_date timestamp without time zone NOT NULL,
    status_id integer NOT NULL,
    created_by character varying COLLATE pg_catalog."default" NOT NULL,
    created_date date NOT NULL,
    updated_by character varying COLLATE pg_catalog."default",
    updated_date date NOT NULL,
    CONSTRAINT domino_rounds_pkey PRIMARY KEY (id),
    CONSTRAINT idx_number_rounds UNIQUE (tourney_id, round_number),
    CONSTRAINT domino_rounds_created_by_fkey FOREIGN KEY (created_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT domino_rounds_status_id_fkey FOREIGN KEY (status_id)
        REFERENCES resources.entities_status (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT domino_rounds_tourney_id_fkey FOREIGN KEY (tourney_id)
        REFERENCES events.tourney (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT domino_rounds_updated_by_fkey FOREIGN KEY (updated_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS events.domino_rounds
    OWNER to postgres;


--Para borrar configuracion de un torneo
DELETE FROM events.files_tables 
where table_id IN (Select id from events.domino_tables where tourney_id = 'ce894036-e52f-4dbf-a07a-21a802948612')

DELETE FROM events.domino_tables where tourney_id = 'ce894036-e52f-4dbf-a07a-21a802948612'

DELETE FROM events.domino_rounds where tourney_id = 'ce894036-e52f-4dbf-a07a-21a802948612'

DELETE FROM events.setting_tourney where tourney_id = 'ce894036-e52f-4dbf-a07a-21a802948612'

update events.tourney
SET status_id = 1
where id = 'ce894036-e52f-4dbf-a07a-21a802948612'