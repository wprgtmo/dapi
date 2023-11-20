ALTER TABLE IF EXISTS events.setting_tourney
    ADD COLUMN elo_min numeric(18, 4);
ALTER TABLE IF EXISTS events.setting_tourney
    ADD COLUMN elo_max numeric(18, 4);

--Crear tabla
DROP TABLE IF EXISTS events.domino_categories;

CREATE TABLE IF NOT EXISTS events.domino_categories
(
    id character varying COLLATE pg_catalog."default" NOT NULL,
    tourney_id character varying COLLATE pg_catalog."default" NOT NULL,
    category_number character varying(100) COLLATE pg_catalog."default" NOT NULL,
    position_number integer NOT NULL,
    elo_min double precision NOT NULL,
    elo_max double precision NOT NULL,
    CONSTRAINT domino_categories_pkey PRIMARY KEY (id),
    CONSTRAINT domino_categories_tourney_id_fkey FOREIGN KEY (tourney_id)
        REFERENCES events.tourney (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS events.domino_categories
    OWNER to postgres;



    
    


--Para borrar configuracion de un torneo
DELETE from events.domino_boletus_position
where boletus_id IN (SELECT id from events.domino_boletus where tourney_id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983');
DELETE FROM events.domino_boletus_pairs
where boletus_id IN (SELECT id from events.domino_boletus where tourney_id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983');
DELETE from events.domino_boletus_data
where boletus_id IN (SELECT id from events.domino_boletus where tourney_id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983');
DELETE from events.domino_boletus
where tourney_id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983';
DELETE from events.domino_rounds_pairs
where tourney_id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983';
DELETE from events.domino_rounds_scale 
where tourney_id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983';
Delete FROM events.trace_lottery_automaic
where tourney_id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983';
Delete FROM events.trace_lottery_manual
where tourney_id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983';
DELETE FROM events.domino_tables_files
where table_id IN (Select id FROM events.domino_tables dtab 
where tourney_id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983');
DELETE FROM events.domino_tables  
where tourney_id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983';
DELETE FROM events.domino_rounds 
where tourney_id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983';
DELETE FROM events.domino_categories
where tourney_id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983';
DELETE FROM events.setting_tourney
where tourney_id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983';
update events.tourney
SET status_id = 1
where id = '0fbe52e9-e9bc-4f6c-b99d-ac9a2208b983';


