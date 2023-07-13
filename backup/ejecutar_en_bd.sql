ALTER TABLE IF EXISTS enterprise.profile_users
    ADD COLUMN is_confirmed boolean DEFAULT False;