

--Subiendo mas
DROP TABLE IF EXISTS events.setting_tourney;

CREATE TABLE IF NOT EXISTS events.setting_tourney
(
    tourney_id character varying COLLATE pg_catalog."default" NOT NULL,
    amount_tables integer NOT NULL,
    amount_smart_tables integer NOT NULL,
    amount_rounds integer NOT NULL,
    use_bonus boolean NOT NULL,
    amount_bonus_tables integer NOT NULL,
    amount_bonus_points integer NOT NULL,
    number_bonus_round integer NOT NULL,
    image text COLLATE pg_catalog."default",
    number_points_to_win integer NOT NULL,
    time_to_win integer NOT NULL,
    game_system character varying(120) COLLATE pg_catalog."default" NOT NULL,
    lottery_type character varying(120) COLLATE pg_catalog."default" NOT NULL,
    penalties_limit integer NOT NULL,
    CONSTRAINT setting_tourney_pkey PRIMARY KEY (tourney_id),
    CONSTRAINT setting_tourney_tourney_id_fkey FOREIGN KEY (tourney_id)
        REFERENCES events.tourney (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS events.setting_tourney
    OWNER to postgres;


--Para borrar configuracion de un torneo
DELETE FROM events.files_tables 
where table_id IN (Select id from events.domino_tables where tourney_id = 'ce894036-e52f-4dbf-a07a-21a802948612')

DELETE FROM events.domino_tables where tourney_id = 'ce894036-e52f-4dbf-a07a-21a802948612'

DELETE FROM events.domino_rounds where tourney_id = 'ce894036-e52f-4dbf-a07a-21a802948612'

DELETE FROM events.setting_tourney where tourney_id = 'ce894036-e52f-4dbf-a07a-21a802948612'

update events.tourney
SET status_id = 1
where id = 'ce894036-e52f-4dbf-a07a-21a802948612'

--Borrar base de datos
DELETE FROM events.files_tables; 
DELETE FROM events.domino_tables;
DELETE FROM events.domino_rounds;
DELETE FROM events.setting_tourney;
DELETE FROM events.players;
DELETE FROM events.referees;
DELETE FROM events.invitations;
DELETE FROM events.tourney;
DELETE FROM events.events;

DELETE FROM post.comment_comments;
DELETE FROM post.comment_likes;
DELETE FROM post.post_comments;
DELETE FROM post.post_files;
DELETE FROM post.post_likes;
DELETE FROM post.post;

DELETE FROM enterprise.profile_followers;
DELETE FROM enterprise.profile_event_admon;
DELETE FROM enterprise.profile_pair_player;
DELETE FROM enterprise.profile_team_player;
DELETE FROM enterprise.profile_single_player;
DELETE FROM enterprise.profile_referee;
DELETE FROM enterprise.profile_default_user;
DELETE FROM enterprise.profile_users;
DELETE FROM enterprise.member_users;
DELETE FROM enterprise.member_profile;
DELETE FROM enterprise.profile_member;
DELETE FROM enterprise.user_eventroles;
DELETE FROM enterprise.user_followers;
DELETE FROM enterprise.users;