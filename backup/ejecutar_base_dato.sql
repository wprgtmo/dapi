-- Table: events.players

DROP TABLE IF EXISTS events.players;
CREATE TABLE IF NOT EXISTS events.players
(
    tourney_id character varying COLLATE pg_catalog."default" NOT NULL,
    user_id character varying COLLATE pg_catalog."default" NOT NULL,
    nivel character varying(50) COLLATE pg_catalog."default",
    created_by character varying COLLATE pg_catalog."default" NOT NULL,
    created_date date NOT NULL,
    updated_by character varying COLLATE pg_catalog."default" NOT NULL,
    updated_date date NOT NULL,
    is_active boolean NOT NULL,
    CONSTRAINT players_pkey PRIMARY KEY (tourney_id, user_id),
    CONSTRAINT players_created_by_fkey FOREIGN KEY (created_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT players_tourney_id_fkey FOREIGN KEY (tourney_id)
        REFERENCES events.tourney (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT players_updated_by_fkey FOREIGN KEY (updated_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT players_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES enterprise.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS events.players
    OWNER to postgres;


-- Table: events.referees

DROP TABLE IF EXISTS events.referees;
CREATE TABLE IF NOT EXISTS events.referees
(
    tourney_id character varying COLLATE pg_catalog."default" NOT NULL,
    user_id character varying COLLATE pg_catalog."default" NOT NULL,
    created_by character varying COLLATE pg_catalog."default" NOT NULL,
    created_date date NOT NULL,
    updated_by character varying COLLATE pg_catalog."default" NOT NULL,
    updated_date date NOT NULL,
    is_active boolean NOT NULL,
    CONSTRAINT referees_pkey PRIMARY KEY (tourney_id, user_id),
    CONSTRAINT referees_created_by_fkey FOREIGN KEY (created_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT referees_tourney_id_fkey FOREIGN KEY (tourney_id)
        REFERENCES events.tourney (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT referees_updated_by_fkey FOREIGN KEY (updated_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT referees_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES enterprise.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS events.referees
    OWNER to postgres;


-- Table: events.invitations

DROP TABLE IF EXISTS events.invitations;
CREATE TABLE IF NOT EXISTS events.invitations
(
    id character varying COLLATE pg_catalog."default" NOT NULL,
    tourney_id character varying COLLATE pg_catalog."default" NOT NULL,
    user_name character varying COLLATE pg_catalog."default" NOT NULL,
    rolevent_name character varying COLLATE pg_catalog."default" NOT NULL,
    status_name character varying COLLATE pg_catalog."default" NOT NULL,
    created_by character varying COLLATE pg_catalog."default" NOT NULL,
    created_date date NOT NULL,
    updated_by character varying COLLATE pg_catalog."default",
    updated_date date NOT NULL,
    CONSTRAINT invitations_pkey PRIMARY KEY (id),
    CONSTRAINT invitations_created_by_fkey FOREIGN KEY (created_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT invitations_rolevent_name_fkey FOREIGN KEY (rolevent_name)
        REFERENCES resources.event_roles (name) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT invitations_status_name_fkey FOREIGN KEY (status_name)
        REFERENCES resources.entities_status (name) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT invitations_tourney_id_fkey FOREIGN KEY (tourney_id)
        REFERENCES events.tourney (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT invitations_updated_by_fkey FOREIGN KEY (updated_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT invitations_user_name_fkey FOREIGN KEY (user_name)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS events.invitations
    OWNER to postgres;