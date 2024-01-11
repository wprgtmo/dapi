ALTER TABLE IF EXISTS events.domino_rounds_pairs
    ADD COLUMN games_won integer;
	ALTER TABLE IF EXISTS events.domino_rounds_pairs
    ADD COLUMN games_lost integer;
	ALTER TABLE IF EXISTS events.domino_rounds_pairs
    ADD COLUMN points_positive integer;
	ALTER TABLE IF EXISTS events.domino_rounds_pairs
    ADD COLUMN points_negative integer;
	ALTER TABLE IF EXISTS events.domino_rounds_pairs
    ADD COLUMN points_difference integer;
	ALTER TABLE IF EXISTS events.domino_rounds_pairs
    ADD COLUMN score_expected double precision;
	ALTER TABLE IF EXISTS events.domino_rounds_pairs
    ADD COLUMN score_obtained double precision;
	ALTER TABLE IF EXISTS events.domino_rounds_pairs
    ADD COLUMN elo_pair double precision;
	ALTER TABLE IF EXISTS events.domino_rounds_pairs
    ADD COLUMN elo_pair_opposing double precision;
	ALTER TABLE IF EXISTS events.domino_rounds_pairs
    ADD COLUMN acumulated_games_played integer;
	ALTER TABLE IF EXISTS events.domino_rounds_pairs
    ADD COLUMN k_value double precision;
	ALTER TABLE IF EXISTS events.domino_rounds_pairs
	ADD COLUMN elo_current double precision;
	ALTER TABLE IF EXISTS events.domino_rounds_pairs
	ADD COLUMN elo_at_end double precision;
	ALTER TABLE IF EXISTS events.domino_rounds_pairs
	ADD COLUMN bonus_points double precision;

    


