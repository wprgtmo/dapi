ALTER TABLE IF EXISTS enterprise.profile_event_admon
ADD COLUMN profile_user_id character varying;
ALTER TABLE IF EXISTS enterprise.profile_federated
ADD COLUMN profile_user_id character varying;
ALTER TABLE IF EXISTS enterprise.profile_referee
ADD COLUMN profile_user_id character varying;
