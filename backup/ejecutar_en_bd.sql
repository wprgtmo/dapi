ALTER TABLE IF EXISTS events.domino_rounds_scale
ADD COLUMN acumulated_games_won integer;
ALTER TABLE IF EXISTS events.domino_rounds_scale
ADD COLUMN acumulated_games_lost integer;

ALTER TABLE IF EXISTS events.domino_rounds_scale
ADD COLUMN acumulated_points_positive integer;
ALTER TABLE IF EXISTS events.domino_rounds_scale
ADD COLUMN acumulated_points_negative integer;
ALTER TABLE IF EXISTS events.domino_rounds_scale
ADD COLUMN acumulated_penalty_points integer;
ALTER TABLE IF EXISTS events.domino_rounds_scale
ADD COLUMN acumulated_bonus_points integer;

ALTER TABLE IF EXISTS events.domino_rounds_scale
ADD COLUMN acumulated_score_expected double precision;
ALTER TABLE IF EXISTS events.domino_rounds_scale
ADD COLUMN acumulated_score_obtained double precision;
ALTER TABLE IF EXISTS events.domino_rounds_scale
ADD COLUMN acumulated_elo_variable double precision;
ALTER TABLE IF EXISTS events.domino_rounds_scale
ADD COLUMN acumulated_elo_at_end double precision;

ALTER TABLE IF EXISTS events.domino_rounds_scale
ADD COLUMN position_number_at_end integer;



ALTER TABLE IF EXISTS events.domino_rounds_pairs
ADD COLUMN acumulated_games_won integer;
ALTER TABLE IF EXISTS events.domino_rounds_pairs
ADD COLUMN acumulated_games_lost integer;

ALTER TABLE IF EXISTS events.domino_rounds_pairs
ADD COLUMN acumulated_points_positive integer;
ALTER TABLE IF EXISTS events.domino_rounds_pairs
ADD COLUMN acumulated_points_negative integer;
ALTER TABLE IF EXISTS events.domino_rounds_pairs
ADD COLUMN acumulated_penalty_points integer;
ALTER TABLE IF EXISTS events.domino_rounds_pairs
ADD COLUMN acumulated_bonus_points integer;

ALTER TABLE IF EXISTS events.domino_rounds_pairs
ADD COLUMN acumulated_score_expected double precision;
ALTER TABLE IF EXISTS events.domino_rounds_pairs
ADD COLUMN acumulated_score_obtained double precision;
ALTER TABLE IF EXISTS events.domino_rounds_pairs
ADD COLUMN acumulated_elo_current double precision;
ALTER TABLE IF EXISTS events.domino_rounds_pairs
ADD COLUMN acumulated_elo_at_end double precision;



