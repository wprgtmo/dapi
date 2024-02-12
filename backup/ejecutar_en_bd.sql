CREATE TABLE IF NOT EXISTS events.domino_boletus_penalties
(
    id character varying COLLATE pg_catalog."default" NOT NULL,
    boletus_id character varying COLLATE pg_catalog."default",
    pair_id character varying COLLATE pg_catalog."default",
    player_id character varying COLLATE pg_catalog."default",
    single_profile_id character varying COLLATE pg_catalog."default",
    penalty_type character varying COLLATE pg_catalog."default",
    penalty_amount integer,
    penalty_value integer,
    apply_points boolean,
    CONSTRAINT domino_boletus_penalties_pkey PRIMARY KEY (id),
    CONSTRAINT domino_boletus_penalties_boletus_id_fkey FOREIGN KEY (boletus_id)
        REFERENCES events.domino_boletus (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT domino_boletus_penalties_pair_id_fkey FOREIGN KEY (pair_id)
        REFERENCES events.domino_rounds_pairs (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS events.domino_boletus_penalties
    OWNER to postgres;
    