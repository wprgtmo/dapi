ALTER TABLE IF EXISTS events.domino_rounds_pairs
    ADD COLUMN scale_id_one_player character varying;
ALTER TABLE IF EXISTS events.domino_rounds_pairs
    ADD COLUMN scale_id_two_player character varying;   
    
    


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


