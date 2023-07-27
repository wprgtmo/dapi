CREATE TABLE IF NOT EXISTS enterprise.profile_followers
(
    profile_id character varying COLLATE pg_catalog."default" NOT NULL,
    username character varying COLLATE pg_catalog."default" NOT NULL,
    profile_follow_id character varying COLLATE pg_catalog."default" NOT NULL,
    username_follow character varying COLLATE pg_catalog."default" NOT NULL,
    created_by character varying COLLATE pg_catalog."default" NOT NULL,
    created_date date NOT NULL,
    is_active boolean NOT NULL,
    CONSTRAINT profile_followers_pkey PRIMARY KEY (profile_id, profile_follow_id),
    CONSTRAINT profile_followers_profile_follow_id_fkey FOREIGN KEY (profile_follow_id)
        REFERENCES enterprise.profile_member (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT profile_followers_profile_id_fkey FOREIGN KEY (profile_id)
        REFERENCES enterprise.profile_member (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS enterprise.profile_followers
    OWNER to postgres;
