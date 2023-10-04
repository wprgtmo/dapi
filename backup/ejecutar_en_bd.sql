API_URI=http://127.0.0.1:5000

-- DROP TABLE IF EXISTS events.setting_tourney;

CREATE TABLE IF NOT EXISTS events.setting_tourney
(
    tourney_id character varying COLLATE pg_catalog."default" NOT NULL,
    amount_tables integer NOT NULL,
    amount_smart_tables integer NOT NULL,
    amount_bonus_tables integer NOT NULL,
    amount_bonus_points integer NOT NULL,
    number_bonus_round integer NOT NULL,
    image text COLLATE pg_catalog."default",
    amount_rounds integer NOT NULL,
    number_points_to_win integer NOT NULL,
    time_to_win integer NOT NULL,
    game_system character varying(120) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT setting_tourney_pkey PRIMARY KEY (tourney_id),
    CONSTRAINT setting_tourney_tourney_id_fkey FOREIGN KEY (tourney_id)
        REFERENCES events.tourney (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS events.setting_tourney
    OWNER to postgres;