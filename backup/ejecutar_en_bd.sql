CREATE TABLE IF NOT EXISTS events.inscriptions
(
    id character varying COLLATE pg_catalog."default" NOT NULL,
    tourney_id character varying COLLATE pg_catalog."default" NOT NULL,
    profile_id character varying COLLATE pg_catalog."default" NOT NULL,
    user_id character varying COLLATE pg_catalog."default",
    modality character varying(30) COLLATE pg_catalog."default" NOT NULL,
    was_pay boolean,
    payment_way character varying COLLATE pg_catalog."default",
    import_pay double precision,
    status_name character varying COLLATE pg_catalog."default" NOT NULL,
    created_by character varying COLLATE pg_catalog."default" NOT NULL,
    created_date date NOT NULL,
    updated_by character varying COLLATE pg_catalog."default",
    updated_date date NOT NULL,
    CONSTRAINT inscriptions_pkey PRIMARY KEY (id),
    CONSTRAINT inscriptions_created_by_fkey FOREIGN KEY (created_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT inscriptions_profile_id_fkey FOREIGN KEY (profile_id)
        REFERENCES enterprise.profile_member (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT inscriptions_status_name_fkey FOREIGN KEY (status_name)
        REFERENCES resources.entities_status (name) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT inscriptions_updated_by_fkey FOREIGN KEY (updated_by)
        REFERENCES enterprise.users (username) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS events.inscriptions
    OWNER to postgres;