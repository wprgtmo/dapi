ALTER TABLE IF EXISTS enterprise.profile_single_player DROP COLUMN IF EXISTS ranking;
ALTER TABLE IF EXISTS enterprise.profile_pair_player DROP COLUMN IF EXISTS ranking;
ALTER TABLE IF EXISTS enterprise.profile_team_player DROP COLUMN IF EXISTS ranking;

ALTER TABLE IF EXISTS events.players DROP COLUMN IF EXISTS ranking;
ALTER TABLE IF EXISTS enterprise.users DROP COLUMN IF EXISTS ranking;
