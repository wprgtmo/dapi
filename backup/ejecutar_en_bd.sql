ALTER TABLE IF EXISTS enterprise.profile_users
        ADD COLUMN single_profile_id character varying;
ALTER TABLE IF EXISTS enterprise.profile_users
    ADD CONSTRAINT profile_id_single_profile_users_fkey FOREIGN KEY (single_profile_id)
    REFERENCES enterprise.profile_member (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

