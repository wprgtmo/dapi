ALTER TABLE IF EXISTS events.tourney
    ADD COLUMN profile_id character varying;
ALTER TABLE IF EXISTS events.tourney
    ADD CONSTRAINT profile_id_tourney_fkey FOREIGN KEY (profile_id)
    REFERENCES enterprise.profile_member (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS post.post
    ADD COLUMN profile_id character varying;
ALTER TABLE IF EXISTS post.post
    ADD CONSTRAINT profile_id_psot_fkey FOREIGN KEY (profile_id)
    REFERENCES enterprise.profile_member (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS post.post_likes
    ADD COLUMN profile_id character varying;
ALTER TABLE IF EXISTS post.post_likes
    ADD CONSTRAINT profile_id_post_likes_fkey FOREIGN KEY (profile_id)
    REFERENCES enterprise.profile_member (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS post.post_comments
    ADD COLUMN profile_id character varying;
ALTER TABLE IF EXISTS post.post_comments
    ADD CONSTRAINT profile_id_post_comments_fkey FOREIGN KEY (profile_id)
    REFERENCES enterprise.profile_member (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS post.comment_likes
    ADD COLUMN profile_id character varying;
ALTER TABLE IF EXISTS post.comment_likes
    ADD CONSTRAINT profile_id_comment_likes_fkey FOREIGN KEY (profile_id)
    REFERENCES enterprise.profile_member (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;


ALTER TABLE IF EXISTS post.comment_comments
    ADD COLUMN profile_id character varying;
ALTER TABLE IF EXISTS post.comment_comments
    ADD CONSTRAINT profile_id_comment_comments_fkey FOREIGN KEY (profile_id)
    REFERENCES enterprise.profile_member (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;

ALTER TABLE IF EXISTS enterprise.profile_single_player
        ADD COLUMN level character varying(60);

ALTER TABLE IF EXISTS enterprise.profile_pair_player
        ADD COLUMN elo integer;
ALTER TABLE IF EXISTS enterprise.profile_pair_player
        ADD COLUMN ranking character varying(2);
        
ALTER TABLE IF EXISTS enterprise.profile_team_player
        ADD COLUMN elo integer;
ALTER TABLE IF EXISTS enterprise.profile_team_player
        ADD COLUMN ranking character varying(2);