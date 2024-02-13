ALTER TABLE IF EXISTS events.domino_boletus
    ADD COLUMN can_update boolean;
ALTER TABLE IF EXISTS events.domino_boletus
    ADD COLUMN motive_closed character varying;
ALTER TABLE IF EXISTS events.domino_boletus
    ADD COLUMN motive_closed_description character varying;

ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN points_for_absences integer;

ALTER TABLE IF EXISTS events.domino_boletus_position
    ADD COLUMN is_winner boolean;
ALTER TABLE IF EXISTS events.domino_boletus_position
    ADD COLUMN positive_points integer;
ALTER TABLE IF EXISTS events.domino_boletus_position
    ADD COLUMN negative_points integer;
ALTER TABLE IF EXISTS events.domino_boletus_position
    ADD COLUMN penalty_points integer;
ALTER TABLE IF EXISTS events.domino_boletus_position
    ADD COLUMN expelled boolean;
ALTER TABLE IF EXISTS events.domino_boletus_position
    ADD COLUMN pairs_id character varying;

    