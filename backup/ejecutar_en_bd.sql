
CREATE TABLE IF NOT EXISTS events.events_followers
(
    id character varying COLLATE pg_catalog."default" NOT NULL,
    profile_id character varying COLLATE pg_catalog."default",
    username character varying COLLATE pg_catalog."default" NOT NULL,
    element_type character varying(30) COLLATE pg_catalog."default" NOT NULL,
    element_id character varying COLLATE pg_catalog."default",
    created_by character varying COLLATE pg_catalog."default" NOT NULL,
    created_date date NOT NULL,
    is_active boolean NOT NULL,
    CONSTRAINT events_followers_pkey PRIMARY KEY (id),
    CONSTRAINT events_followers_profile_id_key UNIQUE (profile_id),
    CONSTRAINT events_followers_profile_id_fkey FOREIGN KEY (profile_id)
        REFERENCES enterprise.profile_member (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS events.events_followers
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

DELETE FROM events.files_tables 

DELETE FROM events.domino_tables

DELETE FROM events.domino_rounds

DELETE FROM events.setting_tourney

SELECT * FROM events.tourney

