

--Para borrar configuracion de un torneo
DELETE FROM events.files_tables 
where table_id IN (Select id from events.domino_tables where tourney_id = 'ce894036-e52f-4dbf-a07a-21a802948612')

DELETE FROM events.domino_tables where tourney_id = 'ce894036-e52f-4dbf-a07a-21a802948612'

DELETE FROM events.domino_rounds where tourney_id = 'ce894036-e52f-4dbf-a07a-21a802948612'

DELETE FROM events.setting_tourney where tourney_id = 'ce894036-e52f-4dbf-a07a-21a802948612'

update events.tourney
SET status_id = 1
where id = 'ce894036-e52f-4dbf-a07a-21a802948612'