ALTER TABLE IF EXISTS enterprise.users DROP COLUMN IF EXISTS sex;
	ALTER TABLE IF EXISTS enterprise.users DROP COLUMN IF EXISTS birthdate;
	ALTER TABLE IF EXISTS enterprise.users DROP COLUMN IF EXISTS alias;
	ALTER TABLE IF EXISTS enterprise.users DROP COLUMN IF EXISTS job;
	ALTER TABLE IF EXISTS enterprise.users DROP COLUMN IF EXISTS city_id;
	ALTER TABLE IF EXISTS enterprise.users DROP COLUMN IF EXISTS photo;
	ALTER TABLE IF EXISTS enterprise.users DROP COLUMN IF EXISTS elo;
	ALTER TABLE IF EXISTS enterprise.users DROP COLUMN IF EXISTS receive_notifications;

----Sabado 16    

ALTER TABLE IF EXISTS events.players_users
ADD COLUMN position_number_at_end integer;

*******


ALTER TABLE IF EXISTS events.tourney DROP CONSTRAINT IF EXISTS tourney_event_id_fkey;
ALTER TABLE IF EXISTS events.tourney DROP COLUMN IF EXISTS event_id;

ALTER TABLE IF EXISTS events.tourney
ADD COLUMN federation_id integer;
ALTER TABLE IF EXISTS events.tourney
    ADD CONSTRAINT tourney_federation_by_fley FOREIGN KEY (federation_id)
    REFERENCES federations.federations (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS events.tourney
ADD COLUMN main_location character varying(255);
ALTER TABLE IF EXISTS events.tourney
ADD COLUMN city_id integer;

ALTER TABLE IF EXISTS events.tourney
    ADD CONSTRAINT tourney_city_by_fkey FOREIGN KEY (city_id)
    REFERENCES resources.city (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS events.tourney
ADD COLUMN inscription_import double precision;
