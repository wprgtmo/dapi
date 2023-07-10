-- DROP TABLE IF EXISTS enterprise.profile_pair_player;

CREATE TABLE IF NOT EXISTS enterprise.profile_pair_player
(
    profile_id character varying COLLATE pg_catalog."default" NOT NULL,
    level character varying(60) COLLATE pg_catalog."default",
    updated_by character varying COLLATE pg_catalog."default" NOT NULL,
    updated_date date NOT NULL,
    CONSTRAINT profile_pair_player_pkey PRIMARY KEY (profile_id),
    CONSTRAINT profile_pair_player_profile_id_fkey FOREIGN KEY (profile_id)
        REFERENCES enterprise.profile_member (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT profile_pair_player_updated_by_fkey FOREIGN KEY (updated_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS enterprise.profile_pair_player
    OWNER to postgres;


-- Table: enterprise.profile_referee

-- DROP TABLE IF EXISTS enterprise.profile_referee;

CREATE TABLE IF NOT EXISTS enterprise.profile_referee
(
    profile_id character varying COLLATE pg_catalog."default" NOT NULL,
    level character varying(60) COLLATE pg_catalog."default",
    updated_by character varying COLLATE pg_catalog."default" NOT NULL,
    updated_date date NOT NULL,
    CONSTRAINT profile_referee_pkey PRIMARY KEY (profile_id),
    CONSTRAINT profile_referee_profile_id_fkey FOREIGN KEY (profile_id)
        REFERENCES enterprise.profile_member (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT profile_referee_updated_by_fkey FOREIGN KEY (updated_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS enterprise.profile_referee
    OWNER to postgres;



-- Table: enterprise.profile_team_player

-- DROP TABLE IF EXISTS enterprise.profile_team_player;

CREATE TABLE IF NOT EXISTS enterprise.profile_team_player
(
    profile_id character varying COLLATE pg_catalog."default" NOT NULL,
    level character varying(60) COLLATE pg_catalog."default",
    amount_members integer,
    updated_by character varying COLLATE pg_catalog."default" NOT NULL,
    updated_date date NOT NULL,
    CONSTRAINT profile_team_player_pkey PRIMARY KEY (profile_id),
    CONSTRAINT profile_team_player_profile_id_fkey FOREIGN KEY (profile_id)
        REFERENCES enterprise.profile_member (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT profile_team_player_updated_by_fkey FOREIGN KEY (updated_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS enterprise.profile_team_player
    OWNER to postgres;