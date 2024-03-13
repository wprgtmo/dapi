ALTER TABLE IF EXISTS enterprise.profile_event_admon
ADD COLUMN federation_id integer;
ALTER TABLE IF EXISTS enterprise.profile_federated
ADD COLUMN federation_id integer;
ALTER TABLE IF EXISTS enterprise.profile_referee
ADD COLUMN federation_id integer;

ALTER TABLE IF EXISTS enterprise.profile_single_player
ADD COLUMN club_id integer;
ALTER TABLE IF EXISTS enterprise.profile_pair_player
ADD COLUMN club_id integer;
ALTER TABLE IF EXISTS enterprise.profile_team_player
ADD COLUMN club_id integer;
