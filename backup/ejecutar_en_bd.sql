
ALTER TABLE IF EXISTS events.domino_boletus
ADD COLUMN motive_not_valid character varying;
ALTER TABLE IF EXISTS events.domino_boletus
ADD COLUMN motive_not_valid_description character varying;

ALTER TABLE IF EXISTS events.domino_boletus_position
ADD COLUMN is_guilty_closure boolean;

    