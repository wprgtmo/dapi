ALTER TABLE IF EXISTS events.domino_boletus
    ADD COLUMN status_id integer;
ALTER TABLE IF EXISTS events.domino_boletus
    ADD CONSTRAINT dfomino_boletus_status_id_fkey FOREIGN KEY (status_id)
    REFERENCES resources.entities_status (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS events.domino_boletus_pairs
    RENAME number_points TO positive_points;

ALTER TABLE IF EXISTS events.domino_boletus_pairs
    ADD COLUMN negative_points integer;

    
    
    


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


