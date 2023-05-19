CREATE TABLE IF NOT EXISTS events.invitations
(
    id character varying COLLATE pg_catalog."default" NOT NULL,
    tourney_id character varying COLLATE pg_catalog."default" NOT NULL,
    user_name character varying COLLATE pg_catalog."default" NOT NULL,
    status_name character varying COLLATE pg_catalog."default" NOT NULL,
    created_by character varying COLLATE pg_catalog."default" NOT NULL,
    created_date date NOT NULL,
    updated_by character varying COLLATE pg_catalog."default",
    updated_date date,
    CONSTRAINT invitations_pkey PRIMARY KEY (id),
    CONSTRAINT invitations_created_by_fkey FOREIGN KEY (created_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
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
    CONSTRAINT invitations_user_name_fkey FOREIGN KEY (user_name)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS events.invitations
    OWNER to postgres;

