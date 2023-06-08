TRUNCATE events.invitations;

ALTER TABLE IF EXISTS events.invitations DROP CONSTRAINT IF EXISTS invitations_user_name_fkey;
ALTER TABLE IF EXISTS events.invitations DROP COLUMN IF EXISTS user_name;
ALTER TABLE IF EXISTS events.invitations
    ADD COLUMN profile_id character varying NOT NULL;
ALTER TABLE IF EXISTS events.invitations
    ADD CONSTRAINT invitations_profile_id_fkey FOREIGN KEY (profile_id)
    REFERENCES enterprise.member_profile (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

TRUNCATE events.players;
ALTER TABLE IF EXISTS events.players DROP CONSTRAINT IF EXISTS players_user_id_fkey;
ALTER TABLE IF EXISTS events.players
    ADD COLUMN profile_id character varying NOT NULL;
	
ALTER TABLE IF EXISTS events.players
    ADD CONSTRAINT players_profile_id_fkey FOREIGN KEY (profile_id)
    REFERENCES enterprise.member_profile (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

TRUNCATE events.referees;
ALTER TABLE IF EXISTS events.referees DROP CONSTRAINT IF EXISTS referees_user_id_fkey;

ALTER TABLE IF EXISTS events.referees
    ADD COLUMN profile_id character varying NOT NULL;
	
ALTER TABLE IF EXISTS events.referees
    ADD CONSTRAINT referees_profile_id_fkey FOREIGN KEY (profile_id)
    REFERENCES enterprise.member_profile (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS enterprise.member_profile
    RENAME modality TO rolevent_name;
ALTER TABLE IF EXISTS enterprise.member_profile
    ADD CONSTRAINT member_profile_rolename_by_fkey FOREIGN KEY (rolevent_name)
    REFERENCES resources.event_roles (name) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;