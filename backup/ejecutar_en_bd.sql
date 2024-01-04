
ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN constant_increase_elo double precision;
	
ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN points_penalty_yellow integer DEFAULT 0;
ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN points_penalty_red integer DEFAULT 0;
	
ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN round_ordering_one character varying(120);
ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN round_ordering_two character varying(120);	
ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN round_ordering_three character varying(120);
ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN round_ordering_four character varying(120);
ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN round_ordering_five character varying(120);


ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN event_ordering_one character varying(120);
ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN event_ordering_two character varying(120);	
ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN event_ordering_three character varying(120);
ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN event_ordering_four character varying(120);
ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN event_ordering_five character varying(120);



