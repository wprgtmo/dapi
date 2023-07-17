ALTER TABLE IF EXISTS events.events
    ADD COLUMN profile_id character varying;
ALTER TABLE IF EXISTS events.events
    ADD CONSTRAINT profile_id_fkey FOREIGN KEY (profile_id)
    REFERENCES enterprise.profile_member (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;