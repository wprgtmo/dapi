ALTER TABLE IF EXISTS enterprise.users
    ADD COLUMN receive_notifications boolean DEFAULT False;

