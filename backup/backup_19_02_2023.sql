PGDMP         !                |            domino %   12.11 (Ubuntu 12.11-0ubuntu0.20.04.1) %   12.11 (Ubuntu 12.11-0ubuntu0.20.04.1) Q   L           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            M           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            N           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            O           1262    97058    domino    DATABASE     l   CREATE DATABASE domino WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'es_CU' LC_CTYPE = 'es_CU';
    DROP DATABASE domino;
                postgres    false                        2615    97059 
   enterprise    SCHEMA        CREATE SCHEMA enterprise;
    DROP SCHEMA enterprise;
                postgres    false            P           0    0    SCHEMA enterprise    COMMENT     7   COMMENT ON SCHEMA enterprise IS 'Gestion de usuarios';
                   postgres    false    5            
            2615    97060    events    SCHEMA        CREATE SCHEMA events;
    DROP SCHEMA events;
                postgres    false                        2615    97061    notifications    SCHEMA        CREATE SCHEMA notifications;
    DROP SCHEMA notifications;
                postgres    false            	            2615    97062    post    SCHEMA        CREATE SCHEMA post;
    DROP SCHEMA post;
                postgres    false                        2615    97063 	   resources    SCHEMA        CREATE SCHEMA resources;
    DROP SCHEMA resources;
                postgres    false            �            1259    97064    profile_default_user    TABLE     /  CREATE TABLE enterprise.profile_default_user (
    profile_id character varying NOT NULL,
    sex character varying(1),
    birthdate date,
    alias character varying(30),
    job character varying(120),
    city_id integer,
    updated_by character varying NOT NULL,
    updated_date date NOT NULL
);
 ,   DROP TABLE enterprise.profile_default_user;
    
   enterprise         heap    postgres    false    5            Q           0    0 #   COLUMN profile_default_user.city_id    COMMENT     a   COMMENT ON COLUMN enterprise.profile_default_user.city_id IS 'City to which the player belongs';
       
   enterprise          postgres    false    207            �            1259    97070    profile_event_admon    TABLE     �   CREATE TABLE enterprise.profile_event_admon (
    profile_id character varying NOT NULL,
    updated_by character varying NOT NULL,
    updated_date date NOT NULL
);
 +   DROP TABLE enterprise.profile_event_admon;
    
   enterprise         heap    postgres    false    5            �            1259    97076    profile_followers    TABLE     O  CREATE TABLE enterprise.profile_followers (
    profile_id character varying NOT NULL,
    username character varying NOT NULL,
    profile_follow_id character varying NOT NULL,
    username_follow character varying NOT NULL,
    created_by character varying NOT NULL,
    created_date date NOT NULL,
    is_active boolean NOT NULL
);
 )   DROP TABLE enterprise.profile_followers;
    
   enterprise         heap    postgres    false    5            �            1259    97082    profile_member    TABLE     �  CREATE TABLE enterprise.profile_member (
    id character varying NOT NULL,
    profile_type character varying NOT NULL,
    name character varying(300) NOT NULL,
    email character varying(300),
    photo character varying(255),
    city_id integer,
    created_by character varying NOT NULL,
    created_date date NOT NULL,
    updated_by character varying NOT NULL,
    updated_date date NOT NULL,
    receive_notifications boolean NOT NULL,
    is_ready boolean NOT NULL,
    is_active boolean NOT NULL
);
 &   DROP TABLE enterprise.profile_member;
    
   enterprise         heap    postgres    false    5            R           0    0    COLUMN profile_member.city_id    COMMENT     [   COMMENT ON COLUMN enterprise.profile_member.city_id IS 'City to which the player belongs';
       
   enterprise          postgres    false    210            �            1259    97088    profile_pair_player    TABLE     �   CREATE TABLE enterprise.profile_pair_player (
    profile_id character varying NOT NULL,
    level character varying(60),
    updated_by character varying NOT NULL,
    updated_date date NOT NULL,
    elo numeric(24,4)
);
 +   DROP TABLE enterprise.profile_pair_player;
    
   enterprise         heap    postgres    false    5            �            1259    97094    profile_referee    TABLE     �   CREATE TABLE enterprise.profile_referee (
    profile_id character varying NOT NULL,
    level character varying(60),
    updated_by character varying NOT NULL,
    updated_date date NOT NULL
);
 '   DROP TABLE enterprise.profile_referee;
    
   enterprise         heap    postgres    false    5            �            1259    97100    profile_single_player    TABLE       CREATE TABLE enterprise.profile_single_player (
    profile_id character varying NOT NULL,
    elo numeric(24,4),
    updated_by character varying NOT NULL,
    updated_date date NOT NULL,
    level character varying(60),
    profile_user_id character varying
);
 -   DROP TABLE enterprise.profile_single_player;
    
   enterprise         heap    postgres    false    5            �            1259    97106    profile_team_player    TABLE     �   CREATE TABLE enterprise.profile_team_player (
    profile_id character varying NOT NULL,
    level character varying(60),
    amount_members integer,
    updated_by character varying NOT NULL,
    updated_date date NOT NULL,
    elo numeric(24,4)
);
 +   DROP TABLE enterprise.profile_team_player;
    
   enterprise         heap    postgres    false    5            �            1259    97112    profile_type    TABLE     2  CREATE TABLE enterprise.profile_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(150) NOT NULL,
    created_by character varying(50) NOT NULL,
    created_date timestamp without time zone NOT NULL,
    by_default boolean,
    is_active boolean
);
 $   DROP TABLE enterprise.profile_type;
    
   enterprise         heap    postgres    false    5            �            1259    97115    profile_type_id_seq    SEQUENCE     �   CREATE SEQUENCE enterprise.profile_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE enterprise.profile_type_id_seq;
    
   enterprise          postgres    false    215    5            S           0    0    profile_type_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE enterprise.profile_type_id_seq OWNED BY enterprise.profile_type.id;
       
   enterprise          postgres    false    216            �            1259    97117    profile_users    TABLE     =  CREATE TABLE enterprise.profile_users (
    profile_id character varying NOT NULL,
    username character varying NOT NULL,
    is_principal boolean NOT NULL,
    created_by character varying NOT NULL,
    created_date date NOT NULL,
    is_confirmed boolean DEFAULT false,
    single_profile_id character varying
);
 %   DROP TABLE enterprise.profile_users;
    
   enterprise         heap    postgres    false    5            �            1259    97124    user_eventroles    TABLE     �   CREATE TABLE enterprise.user_eventroles (
    username character varying(50) NOT NULL,
    eventrol_id integer NOT NULL,
    created_by character varying NOT NULL,
    created_date timestamp without time zone NOT NULL
);
 '   DROP TABLE enterprise.user_eventroles;
    
   enterprise         heap    postgres    false    5            �            1259    97130    user_followers    TABLE     �   CREATE TABLE enterprise.user_followers (
    username character varying(50) NOT NULL,
    user_follow character varying(50) NOT NULL,
    created_date timestamp without time zone NOT NULL,
    is_active boolean NOT NULL
);
 &   DROP TABLE enterprise.user_followers;
    
   enterprise         heap    postgres    false    5            �            1259    97133    users    TABLE     �  CREATE TABLE enterprise.users (
    id character varying NOT NULL,
    username character varying(50) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100),
    email character varying(50),
    phone character varying(12),
    password character varying(255) NOT NULL,
    is_active boolean NOT NULL,
    country_id integer,
    security_code character varying(5),
    sex character varying(1),
    birthdate date,
    alias character varying(30),
    job character varying(120),
    city_id integer,
    photo character varying(255),
    elo integer,
    receive_notifications boolean DEFAULT false
);
    DROP TABLE enterprise.users;
    
   enterprise         heap    postgres    false    5            T           0    0    COLUMN users.city_id    COMMENT     R   COMMENT ON COLUMN enterprise.users.city_id IS 'City to which the player belongs';
       
   enterprise          postgres    false    220            �            1259    97140    domino_boletus    TABLE     �  CREATE TABLE events.domino_boletus (
    id character varying NOT NULL,
    tourney_id character varying NOT NULL,
    round_id character varying NOT NULL,
    table_id character varying NOT NULL,
    is_valid boolean NOT NULL,
    status_id integer NOT NULL,
    can_update boolean,
    motive_closed character varying,
    motive_closed_description character varying,
    motive_not_valid character varying,
    motive_not_valid_description character varying
);
 "   DROP TABLE events.domino_boletus;
       events         heap    postgres    false    10            �            1259    97146    domino_boletus_data    TABLE     �  CREATE TABLE events.domino_boletus_data (
    id character varying NOT NULL,
    boletus_id character varying,
    data_number integer NOT NULL,
    win_pair_id character varying,
    win_by_points boolean NOT NULL,
    win_by_time boolean NOT NULL,
    number_points integer,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone NOT NULL,
    duration double precision
);
 '   DROP TABLE events.domino_boletus_data;
       events         heap    postgres    false    10            �            1259    97152    domino_boletus_pairs    TABLE     �  CREATE TABLE events.domino_boletus_pairs (
    boletus_id character varying NOT NULL,
    pairs_id character varying NOT NULL,
    is_initiator boolean NOT NULL,
    is_winner boolean NOT NULL,
    positive_points integer,
    negative_points integer,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone NOT NULL,
    duration double precision,
    penalty_points integer
);
 (   DROP TABLE events.domino_boletus_pairs;
       events         heap    postgres    false    10                       1259    98164    domino_boletus_penalties    TABLE     T  CREATE TABLE events.domino_boletus_penalties (
    id character varying NOT NULL,
    boletus_id character varying,
    pair_id character varying,
    player_id character varying,
    single_profile_id character varying,
    penalty_type character varying,
    penalty_amount integer,
    penalty_value integer,
    apply_points boolean
);
 ,   DROP TABLE events.domino_boletus_penalties;
       events         heap    postgres    false    10            �            1259    97158    domino_boletus_position    TABLE     �  CREATE TABLE events.domino_boletus_position (
    boletus_id character varying NOT NULL,
    position_id integer NOT NULL,
    single_profile_id character varying,
    scale_number integer,
    is_winner boolean,
    positive_points integer,
    negative_points integer,
    penalty_points integer,
    expelled boolean,
    pairs_id character varying,
    is_guilty_closure boolean
);
 +   DROP TABLE events.domino_boletus_position;
       events         heap    postgres    false    10            �            1259    97164    domino_categories    TABLE     ^  CREATE TABLE events.domino_categories (
    id character varying NOT NULL,
    tourney_id character varying NOT NULL,
    category_number character varying(100) NOT NULL,
    position_number integer NOT NULL,
    elo_min double precision NOT NULL,
    elo_max double precision NOT NULL,
    amount_players integer NOT NULL,
    by_default boolean
);
 %   DROP TABLE events.domino_categories;
       events         heap    postgres    false    10            �            1259    97170    domino_rounds    TABLE     �  CREATE TABLE events.domino_rounds (
    id character varying NOT NULL,
    tourney_id character varying NOT NULL,
    round_number integer NOT NULL,
    summary text,
    start_date timestamp without time zone NOT NULL,
    close_date timestamp without time zone NOT NULL,
    is_first boolean NOT NULL,
    is_last boolean NOT NULL,
    use_segmentation boolean NOT NULL,
    use_bonus boolean NOT NULL,
    amount_bonus_tables integer NOT NULL,
    amount_bonus_points integer NOT NULL,
    created_by character varying NOT NULL,
    created_date date NOT NULL,
    updated_by character varying,
    updated_date date NOT NULL,
    status_id integer NOT NULL,
    amount_tables integer DEFAULT 0,
    amount_players_playing integer DEFAULT 0,
    amount_players_waiting integer DEFAULT 0,
    amount_players_pause integer DEFAULT 0,
    amount_players_expelled integer DEFAULT 0,
    amount_categories integer DEFAULT 0
);
 !   DROP TABLE events.domino_rounds;
       events         heap    postgres    false    10            �            1259    97182    domino_rounds_pairs    TABLE     �  CREATE TABLE events.domino_rounds_pairs (
    id character varying NOT NULL,
    tourney_id character varying,
    round_id character varying NOT NULL,
    position_number integer NOT NULL,
    one_player_id character varying,
    two_player_id character varying,
    name character varying(100),
    profile_type character varying NOT NULL,
    player_id character varying,
    created_by character varying NOT NULL,
    created_date date NOT NULL,
    updated_by character varying NOT NULL,
    updated_date date NOT NULL,
    is_active boolean NOT NULL,
    scale_number_one_player integer,
    scale_number_two_player integer,
    scale_id_one_player character varying,
    scale_id_two_player character varying,
    games_won integer,
    games_lost integer,
    points_positive integer,
    points_negative integer,
    points_difference integer,
    score_expected double precision,
    score_obtained double precision,
    elo_pair double precision,
    elo_pair_opposing double precision,
    acumulated_games_played integer,
    k_value double precision,
    elo_current double precision,
    elo_at_end double precision,
    bonus_points double precision,
    elo_ra double precision,
    penalty_points double precision
);
 '   DROP TABLE events.domino_rounds_pairs;
       events         heap    postgres    false    10            �            1259    97188    domino_rounds_scale    TABLE     B  CREATE TABLE events.domino_rounds_scale (
    id character varying NOT NULL,
    tourney_id character varying NOT NULL,
    round_id character varying NOT NULL,
    round_number integer NOT NULL,
    position_number integer NOT NULL,
    player_id character varying,
    elo double precision,
    elo_variable double precision,
    games_played integer,
    games_won integer,
    games_lost integer,
    points_positive integer,
    points_negative integer,
    points_difference integer,
    is_active boolean NOT NULL,
    category_id character varying,
    score_expected double precision,
    score_obtained double precision,
    acumulated_games_played integer,
    k_value double precision,
    elo_at_end double precision,
    bonus_points double precision,
    elo_ra double precision,
    penalty_points double precision
);
 '   DROP TABLE events.domino_rounds_scale;
       events         heap    postgres    false    10            �            1259    97194    domino_tables    TABLE     �  CREATE TABLE events.domino_tables (
    id character varying NOT NULL,
    tourney_id character varying NOT NULL,
    table_number integer NOT NULL,
    is_smart boolean NOT NULL,
    amount_bonus integer NOT NULL,
    image text,
    is_active boolean NOT NULL,
    created_by character varying NOT NULL,
    created_date date NOT NULL,
    updated_by character varying,
    updated_date date NOT NULL
);
 !   DROP TABLE events.domino_tables;
       events         heap    postgres    false    10            �            1259    97200    domino_tables_files    TABLE     �   CREATE TABLE events.domino_tables_files (
    id character varying NOT NULL,
    table_id character varying NOT NULL,
    "position" integer NOT NULL,
    is_ready boolean NOT NULL
);
 '   DROP TABLE events.domino_tables_files;
       events         heap    postgres    false    10            �            1259    97206    events    TABLE     8  CREATE TABLE events.events (
    id character varying NOT NULL,
    name character varying(100) NOT NULL,
    start_date date NOT NULL,
    close_date date NOT NULL,
    registration_date date NOT NULL,
    registration_price double precision,
    city_id integer NOT NULL,
    main_location character varying(255),
    summary text,
    image text,
    status_id integer NOT NULL,
    created_by character varying NOT NULL,
    created_date date NOT NULL,
    updated_by character varying NOT NULL,
    updated_date date NOT NULL,
    profile_id character varying
);
    DROP TABLE events.events;
       events         heap    postgres    false    10            �            1259    97212    events_followers    TABLE     U  CREATE TABLE events.events_followers (
    id character varying NOT NULL,
    profile_id character varying,
    username character varying NOT NULL,
    element_type character varying(30) NOT NULL,
    element_id character varying,
    created_by character varying NOT NULL,
    created_date date NOT NULL,
    is_active boolean NOT NULL
);
 $   DROP TABLE events.events_followers;
       events         heap    postgres    false    10            �            1259    97218 	   gamerules    TABLE     �   CREATE TABLE events.gamerules (
    tourney_id character varying NOT NULL,
    amount_points integer,
    amount_time integer
);
    DROP TABLE events.gamerules;
       events         heap    postgres    false    10            �            1259    97224    invitations    TABLE     �  CREATE TABLE events.invitations (
    id character varying NOT NULL,
    tourney_id character varying NOT NULL,
    profile_id character varying NOT NULL,
    modality character varying(30) NOT NULL,
    status_name character varying NOT NULL,
    created_by character varying NOT NULL,
    created_date date NOT NULL,
    updated_by character varying,
    updated_date date NOT NULL
);
    DROP TABLE events.invitations;
       events         heap    postgres    false    10            �            1259    97230    players    TABLE     �  CREATE TABLE events.players (
    id character varying NOT NULL,
    tourney_id character varying NOT NULL,
    profile_id character varying NOT NULL,
    invitation_id character varying NOT NULL,
    created_by character varying NOT NULL,
    created_date date NOT NULL,
    updated_by character varying NOT NULL,
    updated_date date NOT NULL,
    elo double precision,
    level character varying(60),
    status_id integer NOT NULL
);
    DROP TABLE events.players;
       events         heap    postgres    false    10            �            1259    97236    players_users    TABLE     �  CREATE TABLE events.players_users (
    player_id character varying NOT NULL,
    profile_id character varying NOT NULL,
    level character varying(60),
    elo double precision,
    elo_current double precision,
    elo_at_end double precision,
    games_played integer,
    games_won integer,
    games_lost integer,
    points_positive integer,
    points_negative integer,
    points_difference integer,
    score_expected double precision,
    score_obtained double precision,
    k_value double precision,
    penalty_yellow integer,
    penalty_red integer,
    penalty_total integer,
    bonus_points double precision,
    category_id character varying,
    category_number integer,
    elo_ra double precision
);
 !   DROP TABLE events.players_users;
       events         heap    postgres    false    10            �            1259    97242    referees    TABLE     ~  CREATE TABLE events.referees (
    id character varying NOT NULL,
    tourney_id character varying NOT NULL,
    profile_id character varying NOT NULL,
    invitation_id character varying NOT NULL,
    created_by character varying NOT NULL,
    created_date date NOT NULL,
    updated_by character varying NOT NULL,
    updated_date date NOT NULL,
    status_id integer NOT NULL
);
    DROP TABLE events.referees;
       events         heap    postgres    false    10            �            1259    97248    sponsors    TABLE     t   CREATE TABLE events.sponsors (
    id integer NOT NULL,
    tourney_id character varying,
    name text NOT NULL
);
    DROP TABLE events.sponsors;
       events         heap    postgres    false    10            �            1259    97254    sponsors_id_seq    SEQUENCE     �   CREATE SEQUENCE events.sponsors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE events.sponsors_id_seq;
       events          postgres    false    10    238            U           0    0    sponsors_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE events.sponsors_id_seq OWNED BY events.sponsors.id;
          events          postgres    false    239            �            1259    97256    tourney    TABLE     	  CREATE TABLE events.tourney (
    id character varying NOT NULL,
    event_id character varying NOT NULL,
    modality character varying(30) NOT NULL,
    name character varying(100),
    summary text,
    start_date date NOT NULL,
    close_date date,
    amount_tables integer NOT NULL,
    amount_smart_tables integer NOT NULL,
    amount_rounds integer NOT NULL,
    number_points_to_win integer NOT NULL,
    time_to_win integer NOT NULL,
    game_system character varying(120),
    lottery_type character varying(120),
    penalties_limit integer,
    image text,
    use_bonus boolean,
    use_segmentation boolean,
    amount_bonus_tables integer,
    amount_bonus_points integer,
    number_bonus_round integer,
    elo_min double precision,
    elo_max double precision,
    profile_id character varying NOT NULL,
    created_by character varying NOT NULL,
    created_date date NOT NULL,
    updated_date date NOT NULL,
    updated_by character varying NOT NULL,
    status_id integer NOT NULL,
    number_rounds integer,
    constant_increase_elo double precision,
    round_ordering_one character varying(120),
    round_ordering_two character varying(120),
    round_ordering_three character varying(120),
    round_ordering_four character varying(120),
    round_ordering_five character varying(120),
    event_ordering_one character varying(120),
    event_ordering_two character varying(120),
    event_ordering_three character varying(120),
    event_ordering_four character varying(120),
    event_ordering_five character varying(120),
    points_penalty_yellow integer DEFAULT 0,
    points_penalty_red integer DEFAULT 0,
    use_penalty boolean,
    amount_bonus_points_rounds integer,
    scope_tourney integer,
    level_tourney integer,
    round_ordering_dir_one character varying(5),
    round_ordering_dir_two character varying(5),
    round_ordering_dir_three character varying(5),
    round_ordering_dir_four character varying(5),
    round_ordering_dir_five character varying(5),
    event_ordering_dir_one character varying(5),
    event_ordering_dir_two character varying(5),
    event_ordering_dir_three character varying(5),
    event_ordering_dir_four character varying(5),
    event_ordering_dir_five character varying(5),
    points_for_absences integer,
    amount_segmentation_round integer
);
    DROP TABLE events.tourney;
       events         heap    postgres    false    10            �            1259    97264    trace_lottery_manual    TABLE       CREATE TABLE events.trace_lottery_manual (
    id character varying NOT NULL,
    tourney_id character varying,
    modality character varying(30) NOT NULL,
    position_number integer NOT NULL,
    player_id character varying NOT NULL,
    is_active boolean NOT NULL
);
 (   DROP TABLE events.trace_lottery_manual;
       events         heap    postgres    false    10            �            1259    97270    notifications    TABLE     �  CREATE TABLE notifications.notifications (
    id character varying NOT NULL,
    profile_id character varying NOT NULL,
    subject text,
    summary text,
    is_read boolean NOT NULL,
    created_by character varying NOT NULL,
    created_date timestamp without time zone NOT NULL,
    read_date timestamp without time zone NOT NULL,
    remove_date timestamp without time zone NOT NULL,
    is_active boolean NOT NULL
);
 (   DROP TABLE notifications.notifications;
       notifications         heap    postgres    false    12            �            1259    97276    comment_comments    TABLE       CREATE TABLE post.comment_comments (
    id character varying NOT NULL,
    comment_id character varying NOT NULL,
    summary text,
    created_by character varying NOT NULL,
    created_date timestamp without time zone NOT NULL,
    profile_id character varying
);
 "   DROP TABLE post.comment_comments;
       post         heap    postgres    false    9            �            1259    97282    comment_likes    TABLE     �   CREATE TABLE post.comment_likes (
    id character varying NOT NULL,
    comment_id character varying NOT NULL,
    created_by character varying NOT NULL,
    created_date timestamp without time zone NOT NULL,
    profile_id character varying
);
    DROP TABLE post.comment_likes;
       post         heap    postgres    false    9            �            1259    97288    post    TABLE     �  CREATE TABLE post.post (
    id character varying NOT NULL,
    summary text,
    created_by character varying NOT NULL,
    created_date timestamp without time zone NOT NULL,
    updated_by character varying,
    updated_date timestamp without time zone NOT NULL,
    is_active boolean NOT NULL,
    allow_comment boolean DEFAULT true NOT NULL,
    show_count_like boolean DEFAULT true NOT NULL,
    profile_id character varying
);
    DROP TABLE post.post;
       post         heap    postgres    false    9            �            1259    97296    post_comments    TABLE       CREATE TABLE post.post_comments (
    id character varying NOT NULL,
    post_id character varying NOT NULL,
    summary text,
    created_by character varying NOT NULL,
    created_date timestamp without time zone NOT NULL,
    profile_id character varying
);
    DROP TABLE post.post_comments;
       post         heap    postgres    false    9            �            1259    97302 
   post_files    TABLE     �   CREATE TABLE post.post_files (
    id character varying NOT NULL,
    post_id character varying NOT NULL,
    path text NOT NULL
);
    DROP TABLE post.post_files;
       post         heap    postgres    false    9            �            1259    97308 
   post_likes    TABLE     �   CREATE TABLE post.post_likes (
    id character varying NOT NULL,
    post_id character varying NOT NULL,
    created_by character varying NOT NULL,
    created_date timestamp without time zone NOT NULL,
    profile_id character varying
);
    DROP TABLE post.post_likes;
       post         heap    postgres    false    9            �            1259    97314    alembic_version    TABLE     X   CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);
 #   DROP TABLE public.alembic_version;
       public         heap    postgres    false            �            1259    97317    city    TABLE     �   CREATE TABLE resources.city (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    country_id integer,
    is_active boolean NOT NULL
);
    DROP TABLE resources.city;
    	   resources         heap    postgres    false    7            �            1259    97320    city_id_seq    SEQUENCE     �   CREATE SEQUENCE resources.city_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE resources.city_id_seq;
    	   resources          postgres    false    7    250            V           0    0    city_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE resources.city_id_seq OWNED BY resources.city.id;
       	   resources          postgres    false    251            �            1259    97322    country    TABLE     �   CREATE TABLE resources.country (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    is_active boolean NOT NULL
);
    DROP TABLE resources.country;
    	   resources         heap    postgres    false    7            �            1259    97325    country_id_seq    SEQUENCE     �   CREATE SEQUENCE resources.country_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE resources.country_id_seq;
    	   resources          postgres    false    7    252            W           0    0    country_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE resources.country_id_seq OWNED BY resources.country.id;
       	   resources          postgres    false    253            �            1259    97327    entities_status    TABLE       CREATE TABLE resources.entities_status (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(100) NOT NULL,
    created_by character varying(50) NOT NULL,
    created_date timestamp without time zone NOT NULL
);
 &   DROP TABLE resources.entities_status;
    	   resources         heap    postgres    false    7            �            1259    97330    entities_status_id_seq    SEQUENCE     �   CREATE SEQUENCE resources.entities_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE resources.entities_status_id_seq;
    	   resources          postgres    false    7    254            X           0    0    entities_status_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE resources.entities_status_id_seq OWNED BY resources.entities_status.id;
       	   resources          postgres    false    255                        1259    97332    event_roles    TABLE        CREATE TABLE resources.event_roles (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description character varying(100) NOT NULL,
    created_by character varying(50) NOT NULL,
    created_date timestamp without time zone NOT NULL
);
 "   DROP TABLE resources.event_roles;
    	   resources         heap    postgres    false    7                       1259    97335    event_roles_id_seq    SEQUENCE     �   CREATE SEQUENCE resources.event_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE resources.event_roles_id_seq;
    	   resources          postgres    false    7    256            Y           0    0    event_roles_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE resources.event_roles_id_seq OWNED BY resources.event_roles.id;
       	   resources          postgres    false    257                       1259    97337    events_levels    TABLE     �   CREATE TABLE resources.events_levels (
    id integer NOT NULL,
    level character varying(50) NOT NULL,
    description character varying(50) NOT NULL,
    value double precision NOT NULL
);
 $   DROP TABLE resources.events_levels;
    	   resources         heap    postgres    false    7                       1259    97340    events_levels_id_seq    SEQUENCE     �   CREATE SEQUENCE resources.events_levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE resources.events_levels_id_seq;
    	   resources          postgres    false    258    7            Z           0    0    events_levels_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE resources.events_levels_id_seq OWNED BY resources.events_levels.id;
       	   resources          postgres    false    259                       1259    97342    events_scopes    TABLE     �   CREATE TABLE resources.events_scopes (
    id integer NOT NULL,
    scope character varying(50) NOT NULL,
    description character varying(50) NOT NULL,
    value double precision NOT NULL
);
 $   DROP TABLE resources.events_scopes;
    	   resources         heap    postgres    false    7                       1259    97345    events_scopes_id_seq    SEQUENCE     �   CREATE SEQUENCE resources.events_scopes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE resources.events_scopes_id_seq;
    	   resources          postgres    false    260    7            [           0    0    events_scopes_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE resources.events_scopes_id_seq OWNED BY resources.events_scopes.id;
       	   resources          postgres    false    261                       1259    97347 	   ext_types    TABLE     �   CREATE TABLE resources.ext_types (
    id integer NOT NULL,
    ext_code character varying(10) NOT NULL,
    type_file character varying(10) NOT NULL,
    created_by character varying(50) NOT NULL,
    created_date timestamp without time zone NOT NULL
);
     DROP TABLE resources.ext_types;
    	   resources         heap    postgres    false    7                       1259    97350    ext_types_id_seq    SEQUENCE     �   CREATE SEQUENCE resources.ext_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE resources.ext_types_id_seq;
    	   resources          postgres    false    262    7            \           0    0    ext_types_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE resources.ext_types_id_seq OWNED BY resources.ext_types.id;
       	   resources          postgres    false    263                       1259    97352    jugadores_eeuu    TABLE       CREATE TABLE resources.jugadores_eeuu (
    id character varying(100) NOT NULL,
    nombre character varying(100),
    apellidos character varying(200),
    pais character varying(100),
    elo_inicial numeric(24,4),
    nivel character varying(100),
    sorteo integer
);
 %   DROP TABLE resources.jugadores_eeuu;
    	   resources         heap    postgres    false    7            	           1259    97358    jugadores_ind    TABLE     �  CREATE TABLE resources.jugadores_ind (
    id character varying(100) NOT NULL,
    nombre_completo character varying(100),
    nombre character varying(100),
    apellido_uno character varying(100),
    apellido_dos character varying(100),
    alias character varying(100),
    username character varying(100),
    provincia character varying(100),
    pais character varying(100),
    elo numeric(24,4),
    nivel character varying(100),
    sorteo integer
);
 $   DROP TABLE resources.jugadores_ind;
    	   resources         heap    postgres    false    7            
           1259    97364    packages    TABLE     \  CREATE TABLE resources.packages (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    price double precision,
    number_individual_tourney integer,
    number_pairs_tourney integer,
    number_team_tourney integer,
    is_active boolean NOT NULL,
    created_by character varying(50) NOT NULL,
    created_date date NOT NULL
);
    DROP TABLE resources.packages;
    	   resources         heap    postgres    false    7                       1259    97367    packages_id_seq    SEQUENCE     �   CREATE SEQUENCE resources.packages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE resources.packages_id_seq;
    	   resources          postgres    false    7    266            ]           0    0    packages_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE resources.packages_id_seq OWNED BY resources.packages.id;
       	   resources          postgres    false    267                       1259    97369    player_categories    TABLE       CREATE TABLE resources.player_categories (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    value_k double precision NOT NULL,
    begin_elo double precision NOT NULL,
    end_elo double precision NOT NULL,
    width double precision NOT NULL,
    scope integer
);
 (   DROP TABLE resources.player_categories;
    	   resources         heap    postgres    false    7                       1259    97372    player_categories_id_seq    SEQUENCE     �   CREATE SEQUENCE resources.player_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE resources.player_categories_id_seq;
    	   resources          postgres    false    268    7            ^           0    0    player_categories_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE resources.player_categories_id_seq OWNED BY resources.player_categories.id;
       	   resources          postgres    false    269            �           2604    97374    profile_type id    DEFAULT     z   ALTER TABLE ONLY enterprise.profile_type ALTER COLUMN id SET DEFAULT nextval('enterprise.profile_type_id_seq'::regclass);
 B   ALTER TABLE enterprise.profile_type ALTER COLUMN id DROP DEFAULT;
    
   enterprise          postgres    false    216    215            �           2604    97375    sponsors id    DEFAULT     j   ALTER TABLE ONLY events.sponsors ALTER COLUMN id SET DEFAULT nextval('events.sponsors_id_seq'::regclass);
 :   ALTER TABLE events.sponsors ALTER COLUMN id DROP DEFAULT;
       events          postgres    false    239    238            �           2604    97376    city id    DEFAULT     h   ALTER TABLE ONLY resources.city ALTER COLUMN id SET DEFAULT nextval('resources.city_id_seq'::regclass);
 9   ALTER TABLE resources.city ALTER COLUMN id DROP DEFAULT;
    	   resources          postgres    false    251    250            �           2604    97377 
   country id    DEFAULT     n   ALTER TABLE ONLY resources.country ALTER COLUMN id SET DEFAULT nextval('resources.country_id_seq'::regclass);
 <   ALTER TABLE resources.country ALTER COLUMN id DROP DEFAULT;
    	   resources          postgres    false    253    252            �           2604    97378    entities_status id    DEFAULT     ~   ALTER TABLE ONLY resources.entities_status ALTER COLUMN id SET DEFAULT nextval('resources.entities_status_id_seq'::regclass);
 D   ALTER TABLE resources.entities_status ALTER COLUMN id DROP DEFAULT;
    	   resources          postgres    false    255    254            �           2604    97379    event_roles id    DEFAULT     v   ALTER TABLE ONLY resources.event_roles ALTER COLUMN id SET DEFAULT nextval('resources.event_roles_id_seq'::regclass);
 @   ALTER TABLE resources.event_roles ALTER COLUMN id DROP DEFAULT;
    	   resources          postgres    false    257    256            �           2604    97380    events_levels id    DEFAULT     z   ALTER TABLE ONLY resources.events_levels ALTER COLUMN id SET DEFAULT nextval('resources.events_levels_id_seq'::regclass);
 B   ALTER TABLE resources.events_levels ALTER COLUMN id DROP DEFAULT;
    	   resources          postgres    false    259    258            �           2604    97381    events_scopes id    DEFAULT     z   ALTER TABLE ONLY resources.events_scopes ALTER COLUMN id SET DEFAULT nextval('resources.events_scopes_id_seq'::regclass);
 B   ALTER TABLE resources.events_scopes ALTER COLUMN id DROP DEFAULT;
    	   resources          postgres    false    261    260            �           2604    97382    ext_types id    DEFAULT     r   ALTER TABLE ONLY resources.ext_types ALTER COLUMN id SET DEFAULT nextval('resources.ext_types_id_seq'::regclass);
 >   ALTER TABLE resources.ext_types ALTER COLUMN id DROP DEFAULT;
    	   resources          postgres    false    263    262            �           2604    97383    packages id    DEFAULT     p   ALTER TABLE ONLY resources.packages ALTER COLUMN id SET DEFAULT nextval('resources.packages_id_seq'::regclass);
 =   ALTER TABLE resources.packages ALTER COLUMN id DROP DEFAULT;
    	   resources          postgres    false    267    266            �           2604    97384    player_categories id    DEFAULT     �   ALTER TABLE ONLY resources.player_categories ALTER COLUMN id SET DEFAULT nextval('resources.player_categories_id_seq'::regclass);
 F   ALTER TABLE resources.player_categories ALTER COLUMN id DROP DEFAULT;
    	   resources          postgres    false    269    268            
          0    97064    profile_default_user 
   TABLE DATA           }   COPY enterprise.profile_default_user (profile_id, sex, birthdate, alias, job, city_id, updated_by, updated_date) FROM stdin;
 
   enterprise          postgres    false    207                   0    97070    profile_event_admon 
   TABLE DATA           W   COPY enterprise.profile_event_admon (profile_id, updated_by, updated_date) FROM stdin;
 
   enterprise          postgres    false    208   s                0    97076    profile_followers 
   TABLE DATA           �   COPY enterprise.profile_followers (profile_id, username, profile_follow_id, username_follow, created_by, created_date, is_active) FROM stdin;
 
   enterprise          postgres    false    209   �                0    97082    profile_member 
   TABLE DATA           �   COPY enterprise.profile_member (id, profile_type, name, email, photo, city_id, created_by, created_date, updated_by, updated_date, receive_notifications, is_ready, is_active) FROM stdin;
 
   enterprise          postgres    false    210   �                0    97088    profile_pair_player 
   TABLE DATA           c   COPY enterprise.profile_pair_player (profile_id, level, updated_by, updated_date, elo) FROM stdin;
 
   enterprise          postgres    false    211   �                 0    97094    profile_referee 
   TABLE DATA           Z   COPY enterprise.profile_referee (profile_id, level, updated_by, updated_date) FROM stdin;
 
   enterprise          postgres    false    212   �                 0    97100    profile_single_player 
   TABLE DATA           v   COPY enterprise.profile_single_player (profile_id, elo, updated_by, updated_date, level, profile_user_id) FROM stdin;
 
   enterprise          postgres    false    213   �                 0    97106    profile_team_player 
   TABLE DATA           s   COPY enterprise.profile_team_player (profile_id, level, amount_members, updated_by, updated_date, elo) FROM stdin;
 
   enterprise          postgres    false    214   L.                0    97112    profile_type 
   TABLE DATA           r   COPY enterprise.profile_type (id, name, description, created_by, created_date, by_default, is_active) FROM stdin;
 
   enterprise          postgres    false    215   i.                0    97117    profile_users 
   TABLE DATA           �   COPY enterprise.profile_users (profile_id, username, is_principal, created_by, created_date, is_confirmed, single_profile_id) FROM stdin;
 
   enterprise          postgres    false    217   ]/                0    97124    user_eventroles 
   TABLE DATA           ^   COPY enterprise.user_eventroles (username, eventrol_id, created_by, created_date) FROM stdin;
 
   enterprise          postgres    false    218   ??                0    97130    user_followers 
   TABLE DATA           \   COPY enterprise.user_followers (username, user_follow, created_date, is_active) FROM stdin;
 
   enterprise          postgres    false    219   \?                0    97133    users 
   TABLE DATA           �   COPY enterprise.users (id, username, first_name, last_name, email, phone, password, is_active, country_id, security_code, sex, birthdate, alias, job, city_id, photo, elo, receive_notifications) FROM stdin;
 
   enterprise          postgres    false    220   y?                0    97140    domino_boletus 
   TABLE DATA           �   COPY events.domino_boletus (id, tourney_id, round_id, table_id, is_valid, status_id, can_update, motive_closed, motive_closed_description, motive_not_valid, motive_not_valid_description) FROM stdin;
    events          postgres    false    221   #U                0    97146    domino_boletus_data 
   TABLE DATA           �   COPY events.domino_boletus_data (id, boletus_id, data_number, win_pair_id, win_by_points, win_by_time, number_points, start_date, end_date, duration) FROM stdin;
    events          postgres    false    222   W                0    97152    domino_boletus_pairs 
   TABLE DATA           �   COPY events.domino_boletus_pairs (boletus_id, pairs_id, is_initiator, is_winner, positive_points, negative_points, start_date, end_date, duration, penalty_points) FROM stdin;
    events          postgres    false    223   �X      I          0    98164    domino_boletus_penalties 
   TABLE DATA           �   COPY events.domino_boletus_penalties (id, boletus_id, pair_id, player_id, single_profile_id, penalty_type, penalty_amount, penalty_value, apply_points) FROM stdin;
    events          postgres    false    270   �[                0    97158    domino_boletus_position 
   TABLE DATA           �   COPY events.domino_boletus_position (boletus_id, position_id, single_profile_id, scale_number, is_winner, positive_points, negative_points, penalty_points, expelled, pairs_id, is_guilty_closure) FROM stdin;
    events          postgres    false    224   \                0    97164    domino_categories 
   TABLE DATA           �   COPY events.domino_categories (id, tourney_id, category_number, position_number, elo_min, elo_max, amount_players, by_default) FROM stdin;
    events          postgres    false    225   �`                0    97170    domino_rounds 
   TABLE DATA           �  COPY events.domino_rounds (id, tourney_id, round_number, summary, start_date, close_date, is_first, is_last, use_segmentation, use_bonus, amount_bonus_tables, amount_bonus_points, created_by, created_date, updated_by, updated_date, status_id, amount_tables, amount_players_playing, amount_players_waiting, amount_players_pause, amount_players_expelled, amount_categories) FROM stdin;
    events          postgres    false    226   Qa                0    97182    domino_rounds_pairs 
   TABLE DATA             COPY events.domino_rounds_pairs (id, tourney_id, round_id, position_number, one_player_id, two_player_id, name, profile_type, player_id, created_by, created_date, updated_by, updated_date, is_active, scale_number_one_player, scale_number_two_player, scale_id_one_player, scale_id_two_player, games_won, games_lost, points_positive, points_negative, points_difference, score_expected, score_obtained, elo_pair, elo_pair_opposing, acumulated_games_played, k_value, elo_current, elo_at_end, bonus_points, elo_ra, penalty_points) FROM stdin;
    events          postgres    false    227   `b                0    97188    domino_rounds_scale 
   TABLE DATA           j  COPY events.domino_rounds_scale (id, tourney_id, round_id, round_number, position_number, player_id, elo, elo_variable, games_played, games_won, games_lost, points_positive, points_negative, points_difference, is_active, category_id, score_expected, score_obtained, acumulated_games_played, k_value, elo_at_end, bonus_points, elo_ra, penalty_points) FROM stdin;
    events          postgres    false    228   �j                 0    97194    domino_tables 
   TABLE DATA           �   COPY events.domino_tables (id, tourney_id, table_number, is_smart, amount_bonus, image, is_active, created_by, created_date, updated_by, updated_date) FROM stdin;
    events          postgres    false    229   >q      !          0    97200    domino_tables_files 
   TABLE DATA           Q   COPY events.domino_tables_files (id, table_id, "position", is_ready) FROM stdin;
    events          postgres    false    230   \r      "          0    97206    events 
   TABLE DATA           �   COPY events.events (id, name, start_date, close_date, registration_date, registration_price, city_id, main_location, summary, image, status_id, created_by, created_date, updated_by, updated_date, profile_id) FROM stdin;
    events          postgres    false    231   yr      #          0    97212    events_followers 
   TABLE DATA           �   COPY events.events_followers (id, profile_id, username, element_type, element_id, created_by, created_date, is_active) FROM stdin;
    events          postgres    false    232   5s      $          0    97218 	   gamerules 
   TABLE DATA           K   COPY events.gamerules (tourney_id, amount_points, amount_time) FROM stdin;
    events          postgres    false    233   Rs      %          0    97224    invitations 
   TABLE DATA           �   COPY events.invitations (id, tourney_id, profile_id, modality, status_name, created_by, created_date, updated_by, updated_date) FROM stdin;
    events          postgres    false    234   os      &          0    97230    players 
   TABLE DATA           �   COPY events.players (id, tourney_id, profile_id, invitation_id, created_by, created_date, updated_by, updated_date, elo, level, status_id) FROM stdin;
    events          postgres    false    235   �      '          0    97236    players_users 
   TABLE DATA           F  COPY events.players_users (player_id, profile_id, level, elo, elo_current, elo_at_end, games_played, games_won, games_lost, points_positive, points_negative, points_difference, score_expected, score_obtained, k_value, penalty_yellow, penalty_red, penalty_total, bonus_points, category_id, category_number, elo_ra) FROM stdin;
    events          postgres    false    236   ��      (          0    97242    referees 
   TABLE DATA           �   COPY events.referees (id, tourney_id, profile_id, invitation_id, created_by, created_date, updated_by, updated_date, status_id) FROM stdin;
    events          postgres    false    237   m�      )          0    97248    sponsors 
   TABLE DATA           8   COPY events.sponsors (id, tourney_id, name) FROM stdin;
    events          postgres    false    238   ��      +          0    97256    tourney 
   TABLE DATA           1  COPY events.tourney (id, event_id, modality, name, summary, start_date, close_date, amount_tables, amount_smart_tables, amount_rounds, number_points_to_win, time_to_win, game_system, lottery_type, penalties_limit, image, use_bonus, use_segmentation, amount_bonus_tables, amount_bonus_points, number_bonus_round, elo_min, elo_max, profile_id, created_by, created_date, updated_date, updated_by, status_id, number_rounds, constant_increase_elo, round_ordering_one, round_ordering_two, round_ordering_three, round_ordering_four, round_ordering_five, event_ordering_one, event_ordering_two, event_ordering_three, event_ordering_four, event_ordering_five, points_penalty_yellow, points_penalty_red, use_penalty, amount_bonus_points_rounds, scope_tourney, level_tourney, round_ordering_dir_one, round_ordering_dir_two, round_ordering_dir_three, round_ordering_dir_four, round_ordering_dir_five, event_ordering_dir_one, event_ordering_dir_two, event_ordering_dir_three, event_ordering_dir_four, event_ordering_dir_five, points_for_absences, amount_segmentation_round) FROM stdin;
    events          postgres    false    240   ��      ,          0    97264    trace_lottery_manual 
   TABLE DATA           o   COPY events.trace_lottery_manual (id, tourney_id, modality, position_number, player_id, is_active) FROM stdin;
    events          postgres    false    241   ��      -          0    97270    notifications 
   TABLE DATA           �   COPY notifications.notifications (id, profile_id, subject, summary, is_read, created_by, created_date, read_date, remove_date, is_active) FROM stdin;
    notifications          postgres    false    242    �      .          0    97276    comment_comments 
   TABLE DATA           g   COPY post.comment_comments (id, comment_id, summary, created_by, created_date, profile_id) FROM stdin;
    post          postgres    false    243   �      /          0    97282    comment_likes 
   TABLE DATA           [   COPY post.comment_likes (id, comment_id, created_by, created_date, profile_id) FROM stdin;
    post          postgres    false    244   :�      0          0    97288    post 
   TABLE DATA           �   COPY post.post (id, summary, created_by, created_date, updated_by, updated_date, is_active, allow_comment, show_count_like, profile_id) FROM stdin;
    post          postgres    false    245   W�      1          0    97296    post_comments 
   TABLE DATA           a   COPY post.post_comments (id, post_id, summary, created_by, created_date, profile_id) FROM stdin;
    post          postgres    false    246   �      2          0    97302 
   post_files 
   TABLE DATA           5   COPY post.post_files (id, post_id, path) FROM stdin;
    post          postgres    false    247   �      3          0    97308 
   post_likes 
   TABLE DATA           U   COPY post.post_likes (id, post_id, created_by, created_date, profile_id) FROM stdin;
    post          postgres    false    248   j�      4          0    97314    alembic_version 
   TABLE DATA           6   COPY public.alembic_version (version_num) FROM stdin;
    public          postgres    false    249   ��      5          0    97317    city 
   TABLE DATA           B   COPY resources.city (id, name, country_id, is_active) FROM stdin;
 	   resources          postgres    false    250   ��      7          0    97322    country 
   TABLE DATA           9   COPY resources.country (id, name, is_active) FROM stdin;
 	   resources          postgres    false    252   ��      9          0    97327    entities_status 
   TABLE DATA           ]   COPY resources.entities_status (id, name, description, created_by, created_date) FROM stdin;
 	   resources          postgres    false    254   ��      ;          0    97332    event_roles 
   TABLE DATA           Y   COPY resources.event_roles (id, name, description, created_by, created_date) FROM stdin;
 	   resources          postgres    false    256   a�      =          0    97337    events_levels 
   TABLE DATA           I   COPY resources.events_levels (id, level, description, value) FROM stdin;
 	   resources          postgres    false    258   Κ      ?          0    97342    events_scopes 
   TABLE DATA           I   COPY resources.events_scopes (id, scope, description, value) FROM stdin;
 	   resources          postgres    false    260   ��      A          0    97347 	   ext_types 
   TABLE DATA           Y   COPY resources.ext_types (id, ext_code, type_file, created_by, created_date) FROM stdin;
 	   resources          postgres    false    262   A�      C          0    97352    jugadores_eeuu 
   TABLE DATA           d   COPY resources.jugadores_eeuu (id, nombre, apellidos, pais, elo_inicial, nivel, sorteo) FROM stdin;
 	   resources          postgres    false    264   ݛ      D          0    97358    jugadores_ind 
   TABLE DATA           �   COPY resources.jugadores_ind (id, nombre_completo, nombre, apellido_uno, apellido_dos, alias, username, provincia, pais, elo, nivel, sorteo) FROM stdin;
 	   resources          postgres    false    265   4�      E          0    97364    packages 
   TABLE DATA           �   COPY resources.packages (id, name, price, number_individual_tourney, number_pairs_tourney, number_team_tourney, is_active, created_by, created_date) FROM stdin;
 	   resources          postgres    false    266   #�      G          0    97369    player_categories 
   TABLE DATA           c   COPY resources.player_categories (id, name, value_k, begin_elo, end_elo, width, scope) FROM stdin;
 	   resources          postgres    false    268   ��      _           0    0    profile_type_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('enterprise.profile_type_id_seq', 6, true);
       
   enterprise          postgres    false    216            `           0    0    sponsors_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('events.sponsors_id_seq', 1, false);
          events          postgres    false    239            a           0    0    city_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('resources.city_id_seq', 80, true);
       	   resources          postgres    false    251            b           0    0    country_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('resources.country_id_seq', 70, true);
       	   resources          postgres    false    253            c           0    0    entities_status_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('resources.entities_status_id_seq', 7, true);
       	   resources          postgres    false    255            d           0    0    event_roles_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('resources.event_roles_id_seq', 5, true);
       	   resources          postgres    false    257            e           0    0    events_levels_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('resources.events_levels_id_seq', 3, true);
       	   resources          postgres    false    259            f           0    0    events_scopes_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('resources.events_scopes_id_seq', 3, true);
       	   resources          postgres    false    261            g           0    0    ext_types_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('resources.ext_types_id_seq', 15, true);
       	   resources          postgres    false    263            h           0    0    packages_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('resources.packages_id_seq', 2, true);
       	   resources          postgres    false    267            i           0    0    player_categories_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('resources.player_categories_id_seq', 7, true);
       	   resources          postgres    false    269            �           2606    97386 .   profile_default_user profile_default_user_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY enterprise.profile_default_user
    ADD CONSTRAINT profile_default_user_pkey PRIMARY KEY (profile_id);
 \   ALTER TABLE ONLY enterprise.profile_default_user DROP CONSTRAINT profile_default_user_pkey;
    
   enterprise            postgres    false    207            �           2606    97388 ,   profile_event_admon profile_event_admon_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY enterprise.profile_event_admon
    ADD CONSTRAINT profile_event_admon_pkey PRIMARY KEY (profile_id);
 Z   ALTER TABLE ONLY enterprise.profile_event_admon DROP CONSTRAINT profile_event_admon_pkey;
    
   enterprise            postgres    false    208            �           2606    97390 (   profile_followers profile_followers_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_followers
    ADD CONSTRAINT profile_followers_pkey PRIMARY KEY (profile_id, profile_follow_id);
 V   ALTER TABLE ONLY enterprise.profile_followers DROP CONSTRAINT profile_followers_pkey;
    
   enterprise            postgres    false    209    209            �           2606    97392 "   profile_member profile_member_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY enterprise.profile_member
    ADD CONSTRAINT profile_member_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY enterprise.profile_member DROP CONSTRAINT profile_member_pkey;
    
   enterprise            postgres    false    210            �           2606    97394 ,   profile_pair_player profile_pair_player_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY enterprise.profile_pair_player
    ADD CONSTRAINT profile_pair_player_pkey PRIMARY KEY (profile_id);
 Z   ALTER TABLE ONLY enterprise.profile_pair_player DROP CONSTRAINT profile_pair_player_pkey;
    
   enterprise            postgres    false    211            �           2606    97396 $   profile_referee profile_referee_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY enterprise.profile_referee
    ADD CONSTRAINT profile_referee_pkey PRIMARY KEY (profile_id);
 R   ALTER TABLE ONLY enterprise.profile_referee DROP CONSTRAINT profile_referee_pkey;
    
   enterprise            postgres    false    212            �           2606    97398 0   profile_single_player profile_single_player_pkey 
   CONSTRAINT     z   ALTER TABLE ONLY enterprise.profile_single_player
    ADD CONSTRAINT profile_single_player_pkey PRIMARY KEY (profile_id);
 ^   ALTER TABLE ONLY enterprise.profile_single_player DROP CONSTRAINT profile_single_player_pkey;
    
   enterprise            postgres    false    213            �           2606    97400 ,   profile_team_player profile_team_player_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY enterprise.profile_team_player
    ADD CONSTRAINT profile_team_player_pkey PRIMARY KEY (profile_id);
 Z   ALTER TABLE ONLY enterprise.profile_team_player DROP CONSTRAINT profile_team_player_pkey;
    
   enterprise            postgres    false    214            �           2606    97402 "   profile_type profile_type_name_key 
   CONSTRAINT     a   ALTER TABLE ONLY enterprise.profile_type
    ADD CONSTRAINT profile_type_name_key UNIQUE (name);
 P   ALTER TABLE ONLY enterprise.profile_type DROP CONSTRAINT profile_type_name_key;
    
   enterprise            postgres    false    215            �           2606    97404    profile_type profile_type_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY enterprise.profile_type
    ADD CONSTRAINT profile_type_pkey PRIMARY KEY (id);
 L   ALTER TABLE ONLY enterprise.profile_type DROP CONSTRAINT profile_type_pkey;
    
   enterprise            postgres    false    215            �           2606    97406     profile_users profile_users_pkey 
   CONSTRAINT     t   ALTER TABLE ONLY enterprise.profile_users
    ADD CONSTRAINT profile_users_pkey PRIMARY KEY (profile_id, username);
 N   ALTER TABLE ONLY enterprise.profile_users DROP CONSTRAINT profile_users_pkey;
    
   enterprise            postgres    false    217    217            �           2606    97408 $   user_eventroles user_eventroles_pkey 
   CONSTRAINT     y   ALTER TABLE ONLY enterprise.user_eventroles
    ADD CONSTRAINT user_eventroles_pkey PRIMARY KEY (username, eventrol_id);
 R   ALTER TABLE ONLY enterprise.user_eventroles DROP CONSTRAINT user_eventroles_pkey;
    
   enterprise            postgres    false    218    218            �           2606    97410 "   user_followers user_followers_pkey 
   CONSTRAINT     w   ALTER TABLE ONLY enterprise.user_followers
    ADD CONSTRAINT user_followers_pkey PRIMARY KEY (username, user_follow);
 P   ALTER TABLE ONLY enterprise.user_followers DROP CONSTRAINT user_followers_pkey;
    
   enterprise            postgres    false    219    219            �           2606    97412    users users_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY enterprise.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY enterprise.users DROP CONSTRAINT users_pkey;
    
   enterprise            postgres    false    220            �           2606    97414    users users_username_key 
   CONSTRAINT     [   ALTER TABLE ONLY enterprise.users
    ADD CONSTRAINT users_username_key UNIQUE (username);
 F   ALTER TABLE ONLY enterprise.users DROP CONSTRAINT users_username_key;
    
   enterprise            postgres    false    220            �           2606    97416 ,   domino_boletus_data domino_boletus_data_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY events.domino_boletus_data
    ADD CONSTRAINT domino_boletus_data_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY events.domino_boletus_data DROP CONSTRAINT domino_boletus_data_pkey;
       events            postgres    false    222            �           2606    97418 .   domino_boletus_pairs domino_boletus_pairs_pkey 
   CONSTRAINT     ~   ALTER TABLE ONLY events.domino_boletus_pairs
    ADD CONSTRAINT domino_boletus_pairs_pkey PRIMARY KEY (boletus_id, pairs_id);
 X   ALTER TABLE ONLY events.domino_boletus_pairs DROP CONSTRAINT domino_boletus_pairs_pkey;
       events            postgres    false    223    223                       2606    98171 6   domino_boletus_penalties domino_boletus_penalties_pkey 
   CONSTRAINT     t   ALTER TABLE ONLY events.domino_boletus_penalties
    ADD CONSTRAINT domino_boletus_penalties_pkey PRIMARY KEY (id);
 `   ALTER TABLE ONLY events.domino_boletus_penalties DROP CONSTRAINT domino_boletus_penalties_pkey;
       events            postgres    false    270            �           2606    97420 "   domino_boletus domino_boletus_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY events.domino_boletus
    ADD CONSTRAINT domino_boletus_pkey PRIMARY KEY (id);
 L   ALTER TABLE ONLY events.domino_boletus DROP CONSTRAINT domino_boletus_pkey;
       events            postgres    false    221            �           2606    97422 4   domino_boletus_position domino_boletus_position_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY events.domino_boletus_position
    ADD CONSTRAINT domino_boletus_position_pkey PRIMARY KEY (boletus_id, position_id);
 ^   ALTER TABLE ONLY events.domino_boletus_position DROP CONSTRAINT domino_boletus_position_pkey;
       events            postgres    false    224    224            �           2606    97424 (   domino_categories domino_categories_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY events.domino_categories
    ADD CONSTRAINT domino_categories_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY events.domino_categories DROP CONSTRAINT domino_categories_pkey;
       events            postgres    false    225            �           2606    97426 ,   domino_rounds_pairs domino_rounds_pairs_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY events.domino_rounds_pairs
    ADD CONSTRAINT domino_rounds_pairs_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY events.domino_rounds_pairs DROP CONSTRAINT domino_rounds_pairs_pkey;
       events            postgres    false    227            �           2606    97428     domino_rounds domino_rounds_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY events.domino_rounds
    ADD CONSTRAINT domino_rounds_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY events.domino_rounds DROP CONSTRAINT domino_rounds_pkey;
       events            postgres    false    226            �           2606    97430 ,   domino_rounds_scale domino_rounds_scale_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY events.domino_rounds_scale
    ADD CONSTRAINT domino_rounds_scale_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY events.domino_rounds_scale DROP CONSTRAINT domino_rounds_scale_pkey;
       events            postgres    false    228            �           2606    97432 ,   domino_tables_files domino_tables_files_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY events.domino_tables_files
    ADD CONSTRAINT domino_tables_files_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY events.domino_tables_files DROP CONSTRAINT domino_tables_files_pkey;
       events            postgres    false    230            �           2606    97434     domino_tables domino_tables_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY events.domino_tables
    ADD CONSTRAINT domino_tables_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY events.domino_tables DROP CONSTRAINT domino_tables_pkey;
       events            postgres    false    229            �           2606    97436 &   events_followers events_followers_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY events.events_followers
    ADD CONSTRAINT events_followers_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY events.events_followers DROP CONSTRAINT events_followers_pkey;
       events            postgres    false    232            �           2606    97438 0   events_followers events_followers_profile_id_key 
   CONSTRAINT     q   ALTER TABLE ONLY events.events_followers
    ADD CONSTRAINT events_followers_profile_id_key UNIQUE (profile_id);
 Z   ALTER TABLE ONLY events.events_followers DROP CONSTRAINT events_followers_profile_id_key;
       events            postgres    false    232            �           2606    97440    events events_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY events.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY events.events DROP CONSTRAINT events_pkey;
       events            postgres    false    231            �           2606    97442    gamerules gamerules_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY events.gamerules
    ADD CONSTRAINT gamerules_pkey PRIMARY KEY (tourney_id);
 B   ALTER TABLE ONLY events.gamerules DROP CONSTRAINT gamerules_pkey;
       events            postgres    false    233            �           2606    97444    invitations invitations_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY events.invitations
    ADD CONSTRAINT invitations_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY events.invitations DROP CONSTRAINT invitations_pkey;
       events            postgres    false    234            �           2606    97446    players players_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY events.players
    ADD CONSTRAINT players_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY events.players DROP CONSTRAINT players_pkey;
       events            postgres    false    235            �           2606    97448    players_users players_user_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY events.players_users
    ADD CONSTRAINT players_user_pkey PRIMARY KEY (player_id, profile_id);
 I   ALTER TABLE ONLY events.players_users DROP CONSTRAINT players_user_pkey;
       events            postgres    false    236    236            �           2606    97450    referees referees_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY events.referees
    ADD CONSTRAINT referees_pkey PRIMARY KEY (id, tourney_id);
 @   ALTER TABLE ONLY events.referees DROP CONSTRAINT referees_pkey;
       events            postgres    false    237    237            �           2606    97452    sponsors sponsors_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY events.sponsors
    ADD CONSTRAINT sponsors_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY events.sponsors DROP CONSTRAINT sponsors_pkey;
       events            postgres    false    238            �           2606    97454    tourney tourney_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY events.tourney
    ADD CONSTRAINT tourney_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY events.tourney DROP CONSTRAINT tourney_pkey;
       events            postgres    false    240            �           2606    97456 .   trace_lottery_manual trace_lottery_manual_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY events.trace_lottery_manual
    ADD CONSTRAINT trace_lottery_manual_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY events.trace_lottery_manual DROP CONSTRAINT trace_lottery_manual_pkey;
       events            postgres    false    241            �           2606    97458     notifications notifications_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY notifications.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);
 Q   ALTER TABLE ONLY notifications.notifications DROP CONSTRAINT notifications_pkey;
       notifications            postgres    false    242            �           2606    97460 &   comment_comments comment_comments_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY post.comment_comments
    ADD CONSTRAINT comment_comments_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY post.comment_comments DROP CONSTRAINT comment_comments_pkey;
       post            postgres    false    243            �           2606    97462     comment_likes comment_likes_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY post.comment_likes
    ADD CONSTRAINT comment_likes_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY post.comment_likes DROP CONSTRAINT comment_likes_pkey;
       post            postgres    false    244            �           2606    97464     post_comments post_comments_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY post.post_comments
    ADD CONSTRAINT post_comments_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY post.post_comments DROP CONSTRAINT post_comments_pkey;
       post            postgres    false    246            �           2606    97466    post_files post_files_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY post.post_files
    ADD CONSTRAINT post_files_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY post.post_files DROP CONSTRAINT post_files_pkey;
       post            postgres    false    247            �           2606    97468    post_likes post_likes_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY post.post_likes
    ADD CONSTRAINT post_likes_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY post.post_likes DROP CONSTRAINT post_likes_pkey;
       post            postgres    false    248            �           2606    97470    post post_pkey 
   CONSTRAINT     J   ALTER TABLE ONLY post.post
    ADD CONSTRAINT post_pkey PRIMARY KEY (id);
 6   ALTER TABLE ONLY post.post DROP CONSTRAINT post_pkey;
       post            postgres    false    245            �           2606    97472 #   alembic_version alembic_version_pkc 
   CONSTRAINT     j   ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);
 M   ALTER TABLE ONLY public.alembic_version DROP CONSTRAINT alembic_version_pkc;
       public            postgres    false    249            �           2606    97474    city city_pkey 
   CONSTRAINT     O   ALTER TABLE ONLY resources.city
    ADD CONSTRAINT city_pkey PRIMARY KEY (id);
 ;   ALTER TABLE ONLY resources.city DROP CONSTRAINT city_pkey;
    	   resources            postgres    false    250            �           2606    97476    country country_pkey 
   CONSTRAINT     U   ALTER TABLE ONLY resources.country
    ADD CONSTRAINT country_pkey PRIMARY KEY (id);
 A   ALTER TABLE ONLY resources.country DROP CONSTRAINT country_pkey;
    	   resources            postgres    false    252            �           2606    97478 (   entities_status entities_status_name_key 
   CONSTRAINT     f   ALTER TABLE ONLY resources.entities_status
    ADD CONSTRAINT entities_status_name_key UNIQUE (name);
 U   ALTER TABLE ONLY resources.entities_status DROP CONSTRAINT entities_status_name_key;
    	   resources            postgres    false    254            �           2606    97480 $   entities_status entities_status_pkey 
   CONSTRAINT     e   ALTER TABLE ONLY resources.entities_status
    ADD CONSTRAINT entities_status_pkey PRIMARY KEY (id);
 Q   ALTER TABLE ONLY resources.entities_status DROP CONSTRAINT entities_status_pkey;
    	   resources            postgres    false    254            �           2606    97482     event_roles event_roles_name_key 
   CONSTRAINT     ^   ALTER TABLE ONLY resources.event_roles
    ADD CONSTRAINT event_roles_name_key UNIQUE (name);
 M   ALTER TABLE ONLY resources.event_roles DROP CONSTRAINT event_roles_name_key;
    	   resources            postgres    false    256                       2606    97484    event_roles event_roles_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY resources.event_roles
    ADD CONSTRAINT event_roles_pkey PRIMARY KEY (id);
 I   ALTER TABLE ONLY resources.event_roles DROP CONSTRAINT event_roles_pkey;
    	   resources            postgres    false    256                       2606    97486 +   events_levels events_levels_description_key 
   CONSTRAINT     p   ALTER TABLE ONLY resources.events_levels
    ADD CONSTRAINT events_levels_description_key UNIQUE (description);
 X   ALTER TABLE ONLY resources.events_levels DROP CONSTRAINT events_levels_description_key;
    	   resources            postgres    false    258                       2606    97488 %   events_levels events_levels_level_key 
   CONSTRAINT     d   ALTER TABLE ONLY resources.events_levels
    ADD CONSTRAINT events_levels_level_key UNIQUE (level);
 R   ALTER TABLE ONLY resources.events_levels DROP CONSTRAINT events_levels_level_key;
    	   resources            postgres    false    258                       2606    97490     events_levels events_levels_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY resources.events_levels
    ADD CONSTRAINT events_levels_pkey PRIMARY KEY (id);
 M   ALTER TABLE ONLY resources.events_levels DROP CONSTRAINT events_levels_pkey;
    	   resources            postgres    false    258            	           2606    97492 +   events_scopes events_scopes_description_key 
   CONSTRAINT     p   ALTER TABLE ONLY resources.events_scopes
    ADD CONSTRAINT events_scopes_description_key UNIQUE (description);
 X   ALTER TABLE ONLY resources.events_scopes DROP CONSTRAINT events_scopes_description_key;
    	   resources            postgres    false    260                       2606    97494     events_scopes events_scopes_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY resources.events_scopes
    ADD CONSTRAINT events_scopes_pkey PRIMARY KEY (id);
 M   ALTER TABLE ONLY resources.events_scopes DROP CONSTRAINT events_scopes_pkey;
    	   resources            postgres    false    260                       2606    97496 %   events_scopes events_scopes_scope_key 
   CONSTRAINT     d   ALTER TABLE ONLY resources.events_scopes
    ADD CONSTRAINT events_scopes_scope_key UNIQUE (scope);
 R   ALTER TABLE ONLY resources.events_scopes DROP CONSTRAINT events_scopes_scope_key;
    	   resources            postgres    false    260                       2606    97498     ext_types ext_types_ext_code_key 
   CONSTRAINT     b   ALTER TABLE ONLY resources.ext_types
    ADD CONSTRAINT ext_types_ext_code_key UNIQUE (ext_code);
 M   ALTER TABLE ONLY resources.ext_types DROP CONSTRAINT ext_types_ext_code_key;
    	   resources            postgres    false    262                       2606    97500    ext_types ext_types_pkey 
   CONSTRAINT     Y   ALTER TABLE ONLY resources.ext_types
    ADD CONSTRAINT ext_types_pkey PRIMARY KEY (id);
 E   ALTER TABLE ONLY resources.ext_types DROP CONSTRAINT ext_types_pkey;
    	   resources            postgres    false    262                       2606    97502 "   jugadores_eeuu jugadores_eeuu_pkey 
   CONSTRAINT     c   ALTER TABLE ONLY resources.jugadores_eeuu
    ADD CONSTRAINT jugadores_eeuu_pkey PRIMARY KEY (id);
 O   ALTER TABLE ONLY resources.jugadores_eeuu DROP CONSTRAINT jugadores_eeuu_pkey;
    	   resources            postgres    false    264                       2606    97504    jugadores_ind jugadores_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY resources.jugadores_ind
    ADD CONSTRAINT jugadores_pkey PRIMARY KEY (id);
 I   ALTER TABLE ONLY resources.jugadores_ind DROP CONSTRAINT jugadores_pkey;
    	   resources            postgres    false    265                       2606    97506 %   jugadores_ind jugadores_user_name_key 
   CONSTRAINT     g   ALTER TABLE ONLY resources.jugadores_ind
    ADD CONSTRAINT jugadores_user_name_key UNIQUE (username);
 R   ALTER TABLE ONLY resources.jugadores_ind DROP CONSTRAINT jugadores_user_name_key;
    	   resources            postgres    false    265                       2606    97508    packages packages_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY resources.packages
    ADD CONSTRAINT packages_pkey PRIMARY KEY (id);
 C   ALTER TABLE ONLY resources.packages DROP CONSTRAINT packages_pkey;
    	   resources            postgres    false    266                       2606    97510 ,   player_categories player_categories_name_key 
   CONSTRAINT     j   ALTER TABLE ONLY resources.player_categories
    ADD CONSTRAINT player_categories_name_key UNIQUE (name);
 Y   ALTER TABLE ONLY resources.player_categories DROP CONSTRAINT player_categories_name_key;
    	   resources            postgres    false    268                       2606    97512 (   player_categories player_categories_pkey 
   CONSTRAINT     i   ALTER TABLE ONLY resources.player_categories
    ADD CONSTRAINT player_categories_pkey PRIMARY KEY (id);
 U   ALTER TABLE ONLY resources.player_categories DROP CONSTRAINT player_categories_pkey;
    	   resources            postgres    false    268            �           1259    97513    single_profile_id    INDEX     \   CREATE INDEX single_profile_id ON enterprise.profile_users USING btree (single_profile_id);
 )   DROP INDEX enterprise.single_profile_id;
    
   enterprise            postgres    false    217                        2606    97514 6   profile_default_user profile_default_user_city_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_default_user
    ADD CONSTRAINT profile_default_user_city_id_fkey FOREIGN KEY (city_id) REFERENCES resources.city(id);
 d   ALTER TABLE ONLY enterprise.profile_default_user DROP CONSTRAINT profile_default_user_city_id_fkey;
    
   enterprise          postgres    false    3831    207    250            !           2606    97519 9   profile_default_user profile_default_user_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_default_user
    ADD CONSTRAINT profile_default_user_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 g   ALTER TABLE ONLY enterprise.profile_default_user DROP CONSTRAINT profile_default_user_profile_id_fkey;
    
   enterprise          postgres    false    3748    210    207            "           2606    97524 9   profile_default_user profile_default_user_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_default_user
    ADD CONSTRAINT profile_default_user_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 g   ALTER TABLE ONLY enterprise.profile_default_user DROP CONSTRAINT profile_default_user_updated_by_fkey;
    
   enterprise          postgres    false    3771    220    207            #           2606    97529 7   profile_event_admon profile_event_admon_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_event_admon
    ADD CONSTRAINT profile_event_admon_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 e   ALTER TABLE ONLY enterprise.profile_event_admon DROP CONSTRAINT profile_event_admon_profile_id_fkey;
    
   enterprise          postgres    false    3748    210    208            $           2606    97534 7   profile_event_admon profile_event_admon_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_event_admon
    ADD CONSTRAINT profile_event_admon_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 e   ALTER TABLE ONLY enterprise.profile_event_admon DROP CONSTRAINT profile_event_admon_updated_by_fkey;
    
   enterprise          postgres    false    208    3771    220            %           2606    97539 :   profile_followers profile_followers_profile_follow_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_followers
    ADD CONSTRAINT profile_followers_profile_follow_id_fkey FOREIGN KEY (profile_follow_id) REFERENCES enterprise.profile_member(id);
 h   ALTER TABLE ONLY enterprise.profile_followers DROP CONSTRAINT profile_followers_profile_follow_id_fkey;
    
   enterprise          postgres    false    3748    210    209            &           2606    97544 3   profile_followers profile_followers_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_followers
    ADD CONSTRAINT profile_followers_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 a   ALTER TABLE ONLY enterprise.profile_followers DROP CONSTRAINT profile_followers_profile_id_fkey;
    
   enterprise          postgres    false    3748    209    210            3           2606    97549 +   profile_users profile_id_profile_users_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_users
    ADD CONSTRAINT profile_id_profile_users_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id) NOT VALID;
 Y   ALTER TABLE ONLY enterprise.profile_users DROP CONSTRAINT profile_id_profile_users_fkey;
    
   enterprise          postgres    false    217    210    3748            '           2606    97554 *   profile_member profile_member_city_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_member
    ADD CONSTRAINT profile_member_city_id_fkey FOREIGN KEY (city_id) REFERENCES resources.city(id);
 X   ALTER TABLE ONLY enterprise.profile_member DROP CONSTRAINT profile_member_city_id_fkey;
    
   enterprise          postgres    false    3831    250    210            (           2606    97559 -   profile_member profile_member_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_member
    ADD CONSTRAINT profile_member_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 [   ALTER TABLE ONLY enterprise.profile_member DROP CONSTRAINT profile_member_created_by_fkey;
    
   enterprise          postgres    false    3771    220    210            )           2606    97564 /   profile_member profile_member_profile_type_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_member
    ADD CONSTRAINT profile_member_profile_type_fkey FOREIGN KEY (profile_type) REFERENCES enterprise.profile_type(name);
 ]   ALTER TABLE ONLY enterprise.profile_member DROP CONSTRAINT profile_member_profile_type_fkey;
    
   enterprise          postgres    false    215    3758    210            *           2606    97569 -   profile_member profile_member_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_member
    ADD CONSTRAINT profile_member_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 [   ALTER TABLE ONLY enterprise.profile_member DROP CONSTRAINT profile_member_updated_by_fkey;
    
   enterprise          postgres    false    210    220    3771            +           2606    97574 7   profile_pair_player profile_pair_player_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_pair_player
    ADD CONSTRAINT profile_pair_player_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 e   ALTER TABLE ONLY enterprise.profile_pair_player DROP CONSTRAINT profile_pair_player_profile_id_fkey;
    
   enterprise          postgres    false    211    210    3748            ,           2606    97579 7   profile_pair_player profile_pair_player_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_pair_player
    ADD CONSTRAINT profile_pair_player_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 e   ALTER TABLE ONLY enterprise.profile_pair_player DROP CONSTRAINT profile_pair_player_updated_by_fkey;
    
   enterprise          postgres    false    220    3771    211            -           2606    97584 /   profile_referee profile_referee_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_referee
    ADD CONSTRAINT profile_referee_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 ]   ALTER TABLE ONLY enterprise.profile_referee DROP CONSTRAINT profile_referee_profile_id_fkey;
    
   enterprise          postgres    false    212    3748    210            .           2606    97589 /   profile_referee profile_referee_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_referee
    ADD CONSTRAINT profile_referee_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 ]   ALTER TABLE ONLY enterprise.profile_referee DROP CONSTRAINT profile_referee_updated_by_fkey;
    
   enterprise          postgres    false    3771    220    212            /           2606    97594 ;   profile_single_player profile_single_player_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_single_player
    ADD CONSTRAINT profile_single_player_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 i   ALTER TABLE ONLY enterprise.profile_single_player DROP CONSTRAINT profile_single_player_profile_id_fkey;
    
   enterprise          postgres    false    210    3748    213            0           2606    97599 ;   profile_single_player profile_single_player_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_single_player
    ADD CONSTRAINT profile_single_player_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 i   ALTER TABLE ONLY enterprise.profile_single_player DROP CONSTRAINT profile_single_player_updated_by_fkey;
    
   enterprise          postgres    false    220    3771    213            1           2606    97604 7   profile_team_player profile_team_player_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_team_player
    ADD CONSTRAINT profile_team_player_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 e   ALTER TABLE ONLY enterprise.profile_team_player DROP CONSTRAINT profile_team_player_profile_id_fkey;
    
   enterprise          postgres    false    3748    210    214            2           2606    97609 7   profile_team_player profile_team_player_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_team_player
    ADD CONSTRAINT profile_team_player_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 e   ALTER TABLE ONLY enterprise.profile_team_player DROP CONSTRAINT profile_team_player_updated_by_fkey;
    
   enterprise          postgres    false    3771    220    214            4           2606    97614 +   profile_users profile_users_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_users
    ADD CONSTRAINT profile_users_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 Y   ALTER TABLE ONLY enterprise.profile_users DROP CONSTRAINT profile_users_created_by_fkey;
    
   enterprise          postgres    false    217    220    3771            5           2606    97619 +   profile_users profile_users_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_users
    ADD CONSTRAINT profile_users_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 Y   ALTER TABLE ONLY enterprise.profile_users DROP CONSTRAINT profile_users_profile_id_fkey;
    
   enterprise          postgres    false    210    217    3748            6           2606    97624 )   profile_users profile_users_username_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.profile_users
    ADD CONSTRAINT profile_users_username_fkey FOREIGN KEY (username) REFERENCES enterprise.users(username);
 W   ALTER TABLE ONLY enterprise.profile_users DROP CONSTRAINT profile_users_username_fkey;
    
   enterprise          postgres    false    220    217    3771            7           2606    97629 /   user_eventroles user_eventroles_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.user_eventroles
    ADD CONSTRAINT user_eventroles_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 ]   ALTER TABLE ONLY enterprise.user_eventroles DROP CONSTRAINT user_eventroles_created_by_fkey;
    
   enterprise          postgres    false    3771    220    218            8           2606    97634 0   user_eventroles user_eventroles_eventrol_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.user_eventroles
    ADD CONSTRAINT user_eventroles_eventrol_id_fkey FOREIGN KEY (eventrol_id) REFERENCES resources.event_roles(id);
 ^   ALTER TABLE ONLY enterprise.user_eventroles DROP CONSTRAINT user_eventroles_eventrol_id_fkey;
    
   enterprise          postgres    false    3841    218    256            9           2606    97639    users users_city_id_fkey    FK CONSTRAINT     }   ALTER TABLE ONLY enterprise.users
    ADD CONSTRAINT users_city_id_fkey FOREIGN KEY (city_id) REFERENCES resources.city(id);
 F   ALTER TABLE ONLY enterprise.users DROP CONSTRAINT users_city_id_fkey;
    
   enterprise          postgres    false    220    3831    250            :           2606    97644    users users_country_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY enterprise.users
    ADD CONSTRAINT users_country_id_fkey FOREIGN KEY (country_id) REFERENCES resources.country(id);
 I   ALTER TABLE ONLY enterprise.users DROP CONSTRAINT users_country_id_fkey;
    
   enterprise          postgres    false    220    252    3833            ?           2606    97649 7   domino_boletus_data domino_boletus_data_boletus_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_boletus_data
    ADD CONSTRAINT domino_boletus_data_boletus_id_fkey FOREIGN KEY (boletus_id) REFERENCES events.domino_boletus(id);
 a   ALTER TABLE ONLY events.domino_boletus_data DROP CONSTRAINT domino_boletus_data_boletus_id_fkey;
       events          postgres    false    3773    221    222            @           2606    97654 8   domino_boletus_data domino_boletus_data_win_pair_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_boletus_data
    ADD CONSTRAINT domino_boletus_data_win_pair_id_fkey FOREIGN KEY (win_pair_id) REFERENCES events.domino_rounds_pairs(id);
 b   ALTER TABLE ONLY events.domino_boletus_data DROP CONSTRAINT domino_boletus_data_win_pair_id_fkey;
       events          postgres    false    3785    227    222            A           2606    97659 9   domino_boletus_pairs domino_boletus_pairs_boletus_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_boletus_pairs
    ADD CONSTRAINT domino_boletus_pairs_boletus_id_fkey FOREIGN KEY (boletus_id) REFERENCES events.domino_boletus(id);
 c   ALTER TABLE ONLY events.domino_boletus_pairs DROP CONSTRAINT domino_boletus_pairs_boletus_id_fkey;
       events          postgres    false    221    3773    223            B           2606    97664 7   domino_boletus_pairs domino_boletus_pairs_pairs_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_boletus_pairs
    ADD CONSTRAINT domino_boletus_pairs_pairs_id_fkey FOREIGN KEY (pairs_id) REFERENCES events.domino_rounds_pairs(id);
 a   ALTER TABLE ONLY events.domino_boletus_pairs DROP CONSTRAINT domino_boletus_pairs_pairs_id_fkey;
       events          postgres    false    223    3785    227            �           2606    98172 A   domino_boletus_penalties domino_boletus_penalties_boletus_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_boletus_penalties
    ADD CONSTRAINT domino_boletus_penalties_boletus_id_fkey FOREIGN KEY (boletus_id) REFERENCES events.domino_boletus(id);
 k   ALTER TABLE ONLY events.domino_boletus_penalties DROP CONSTRAINT domino_boletus_penalties_boletus_id_fkey;
       events          postgres    false    221    270    3773            �           2606    98177 >   domino_boletus_penalties domino_boletus_penalties_pair_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_boletus_penalties
    ADD CONSTRAINT domino_boletus_penalties_pair_id_fkey FOREIGN KEY (pair_id) REFERENCES events.domino_rounds_pairs(id);
 h   ALTER TABLE ONLY events.domino_boletus_penalties DROP CONSTRAINT domino_boletus_penalties_pair_id_fkey;
       events          postgres    false    3785    227    270            C           2606    97669 ?   domino_boletus_position domino_boletus_position_boletus_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_boletus_position
    ADD CONSTRAINT domino_boletus_position_boletus_id_fkey FOREIGN KEY (boletus_id) REFERENCES events.domino_boletus(id);
 i   ALTER TABLE ONLY events.domino_boletus_position DROP CONSTRAINT domino_boletus_position_boletus_id_fkey;
       events          postgres    false    3773    221    224            ;           2606    97674 +   domino_boletus domino_boletus_round_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_boletus
    ADD CONSTRAINT domino_boletus_round_id_fkey FOREIGN KEY (round_id) REFERENCES events.domino_rounds(id);
 U   ALTER TABLE ONLY events.domino_boletus DROP CONSTRAINT domino_boletus_round_id_fkey;
       events          postgres    false    226    3783    221            <           2606    97679 ,   domino_boletus domino_boletus_status_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_boletus
    ADD CONSTRAINT domino_boletus_status_id_fkey FOREIGN KEY (status_id) REFERENCES resources.entities_status(id);
 V   ALTER TABLE ONLY events.domino_boletus DROP CONSTRAINT domino_boletus_status_id_fkey;
       events          postgres    false    3837    221    254            =           2606    97684 +   domino_boletus domino_boletus_table_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_boletus
    ADD CONSTRAINT domino_boletus_table_id_fkey FOREIGN KEY (table_id) REFERENCES events.domino_tables(id);
 U   ALTER TABLE ONLY events.domino_boletus DROP CONSTRAINT domino_boletus_table_id_fkey;
       events          postgres    false    229    221    3789            >           2606    97689 -   domino_boletus domino_boletus_tourney_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_boletus
    ADD CONSTRAINT domino_boletus_tourney_id_fkey FOREIGN KEY (tourney_id) REFERENCES events.tourney(id);
 W   ALTER TABLE ONLY events.domino_boletus DROP CONSTRAINT domino_boletus_tourney_id_fkey;
       events          postgres    false    3811    221    240            D           2606    97694 3   domino_categories domino_categories_tourney_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_categories
    ADD CONSTRAINT domino_categories_tourney_id_fkey FOREIGN KEY (tourney_id) REFERENCES events.tourney(id);
 ]   ALTER TABLE ONLY events.domino_categories DROP CONSTRAINT domino_categories_tourney_id_fkey;
       events          postgres    false    3811    225    240            E           2606    97699 +   domino_rounds domino_rounds_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds
    ADD CONSTRAINT domino_rounds_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 U   ALTER TABLE ONLY events.domino_rounds DROP CONSTRAINT domino_rounds_created_by_fkey;
       events          postgres    false    226    220    3771            I           2606    97704 7   domino_rounds_pairs domino_rounds_pairs_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds_pairs
    ADD CONSTRAINT domino_rounds_pairs_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 a   ALTER TABLE ONLY events.domino_rounds_pairs DROP CONSTRAINT domino_rounds_pairs_created_by_fkey;
       events          postgres    false    3771    227    220            J           2606    97709 :   domino_rounds_pairs domino_rounds_pairs_one_player_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds_pairs
    ADD CONSTRAINT domino_rounds_pairs_one_player_id_fkey FOREIGN KEY (one_player_id) REFERENCES enterprise.profile_member(id);
 d   ALTER TABLE ONLY events.domino_rounds_pairs DROP CONSTRAINT domino_rounds_pairs_one_player_id_fkey;
       events          postgres    false    3748    227    210            K           2606    97714 6   domino_rounds_pairs domino_rounds_pairs_player_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds_pairs
    ADD CONSTRAINT domino_rounds_pairs_player_id_fkey FOREIGN KEY (player_id) REFERENCES events.players(id);
 `   ALTER TABLE ONLY events.domino_rounds_pairs DROP CONSTRAINT domino_rounds_pairs_player_id_fkey;
       events          postgres    false    3803    227    235            L           2606    97719 5   domino_rounds_pairs domino_rounds_pairs_round_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds_pairs
    ADD CONSTRAINT domino_rounds_pairs_round_id_fkey FOREIGN KEY (round_id) REFERENCES events.domino_rounds(id);
 _   ALTER TABLE ONLY events.domino_rounds_pairs DROP CONSTRAINT domino_rounds_pairs_round_id_fkey;
       events          postgres    false    226    227    3783            M           2606    97724 7   domino_rounds_pairs domino_rounds_pairs_tourney_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds_pairs
    ADD CONSTRAINT domino_rounds_pairs_tourney_id_fkey FOREIGN KEY (tourney_id) REFERENCES events.tourney(id);
 a   ALTER TABLE ONLY events.domino_rounds_pairs DROP CONSTRAINT domino_rounds_pairs_tourney_id_fkey;
       events          postgres    false    240    3811    227            N           2606    97729 :   domino_rounds_pairs domino_rounds_pairs_two_player_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds_pairs
    ADD CONSTRAINT domino_rounds_pairs_two_player_id_fkey FOREIGN KEY (two_player_id) REFERENCES enterprise.profile_member(id);
 d   ALTER TABLE ONLY events.domino_rounds_pairs DROP CONSTRAINT domino_rounds_pairs_two_player_id_fkey;
       events          postgres    false    3748    210    227            O           2606    97734 7   domino_rounds_pairs domino_rounds_pairs_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds_pairs
    ADD CONSTRAINT domino_rounds_pairs_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 a   ALTER TABLE ONLY events.domino_rounds_pairs DROP CONSTRAINT domino_rounds_pairs_updated_by_fkey;
       events          postgres    false    3771    227    220            P           2606    97739 6   domino_rounds_scale domino_rounds_scale_player_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds_scale
    ADD CONSTRAINT domino_rounds_scale_player_id_fkey FOREIGN KEY (player_id) REFERENCES events.players(id);
 `   ALTER TABLE ONLY events.domino_rounds_scale DROP CONSTRAINT domino_rounds_scale_player_id_fkey;
       events          postgres    false    235    228    3803            Q           2606    97744 5   domino_rounds_scale domino_rounds_scale_round_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds_scale
    ADD CONSTRAINT domino_rounds_scale_round_id_fkey FOREIGN KEY (round_id) REFERENCES events.domino_rounds(id);
 _   ALTER TABLE ONLY events.domino_rounds_scale DROP CONSTRAINT domino_rounds_scale_round_id_fkey;
       events          postgres    false    226    3783    228            R           2606    97749 7   domino_rounds_scale domino_rounds_scale_tourney_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds_scale
    ADD CONSTRAINT domino_rounds_scale_tourney_id_fkey FOREIGN KEY (tourney_id) REFERENCES events.tourney(id);
 a   ALTER TABLE ONLY events.domino_rounds_scale DROP CONSTRAINT domino_rounds_scale_tourney_id_fkey;
       events          postgres    false    228    3811    240            F           2606    97754 *   domino_rounds domino_rounds_status_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds
    ADD CONSTRAINT domino_rounds_status_id_fkey FOREIGN KEY (status_id) REFERENCES resources.entities_status(id);
 T   ALTER TABLE ONLY events.domino_rounds DROP CONSTRAINT domino_rounds_status_id_fkey;
       events          postgres    false    226    254    3837            G           2606    97759 +   domino_rounds domino_rounds_tourney_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds
    ADD CONSTRAINT domino_rounds_tourney_id_fkey FOREIGN KEY (tourney_id) REFERENCES events.tourney(id);
 U   ALTER TABLE ONLY events.domino_rounds DROP CONSTRAINT domino_rounds_tourney_id_fkey;
       events          postgres    false    3811    240    226            H           2606    97764 +   domino_rounds domino_rounds_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_rounds
    ADD CONSTRAINT domino_rounds_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 U   ALTER TABLE ONLY events.domino_rounds DROP CONSTRAINT domino_rounds_updated_by_fkey;
       events          postgres    false    226    3771    220            S           2606    97769 +   domino_tables domino_tables_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_tables
    ADD CONSTRAINT domino_tables_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 U   ALTER TABLE ONLY events.domino_tables DROP CONSTRAINT domino_tables_created_by_fkey;
       events          postgres    false    3771    229    220            V           2606    97774 5   domino_tables_files domino_tables_files_table_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_tables_files
    ADD CONSTRAINT domino_tables_files_table_id_fkey FOREIGN KEY (table_id) REFERENCES events.domino_tables(id);
 _   ALTER TABLE ONLY events.domino_tables_files DROP CONSTRAINT domino_tables_files_table_id_fkey;
       events          postgres    false    3789    230    229            T           2606    97779 +   domino_tables domino_tables_tourney_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_tables
    ADD CONSTRAINT domino_tables_tourney_id_fkey FOREIGN KEY (tourney_id) REFERENCES events.tourney(id);
 U   ALTER TABLE ONLY events.domino_tables DROP CONSTRAINT domino_tables_tourney_id_fkey;
       events          postgres    false    229    240    3811            U           2606    97784 +   domino_tables domino_tables_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.domino_tables
    ADD CONSTRAINT domino_tables_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 U   ALTER TABLE ONLY events.domino_tables DROP CONSTRAINT domino_tables_updated_by_fkey;
       events          postgres    false    220    3771    229            W           2606    97789    events events_city_id_fkey    FK CONSTRAINT     {   ALTER TABLE ONLY events.events
    ADD CONSTRAINT events_city_id_fkey FOREIGN KEY (city_id) REFERENCES resources.city(id);
 D   ALTER TABLE ONLY events.events DROP CONSTRAINT events_city_id_fkey;
       events          postgres    false    231    3831    250            X           2606    97794    events events_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.events
    ADD CONSTRAINT events_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 G   ALTER TABLE ONLY events.events DROP CONSTRAINT events_created_by_fkey;
       events          postgres    false    231    3771    220            \           2606    97799 1   events_followers events_followers_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.events_followers
    ADD CONSTRAINT events_followers_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 [   ALTER TABLE ONLY events.events_followers DROP CONSTRAINT events_followers_profile_id_fkey;
       events          postgres    false    232    3748    210            Y           2606    97804    events events_status_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.events
    ADD CONSTRAINT events_status_id_fkey FOREIGN KEY (status_id) REFERENCES resources.entities_status(id);
 F   ALTER TABLE ONLY events.events DROP CONSTRAINT events_status_id_fkey;
       events          postgres    false    3837    254    231            Z           2606    97809    events events_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.events
    ADD CONSTRAINT events_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 G   ALTER TABLE ONLY events.events DROP CONSTRAINT events_updated_by_fkey;
       events          postgres    false    220    3771    231            ]           2606    97814 '   invitations invitations_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.invitations
    ADD CONSTRAINT invitations_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 Q   ALTER TABLE ONLY events.invitations DROP CONSTRAINT invitations_created_by_fkey;
       events          postgres    false    220    3771    234            ^           2606    97819 '   invitations invitations_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.invitations
    ADD CONSTRAINT invitations_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 Q   ALTER TABLE ONLY events.invitations DROP CONSTRAINT invitations_profile_id_fkey;
       events          postgres    false    210    3748    234            _           2606    97824 (   invitations invitations_status_name_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.invitations
    ADD CONSTRAINT invitations_status_name_fkey FOREIGN KEY (status_name) REFERENCES resources.entities_status(name);
 R   ALTER TABLE ONLY events.invitations DROP CONSTRAINT invitations_status_name_fkey;
       events          postgres    false    3835    254    234            `           2606    97829 '   invitations invitations_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.invitations
    ADD CONSTRAINT invitations_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 Q   ALTER TABLE ONLY events.invitations DROP CONSTRAINT invitations_updated_by_fkey;
       events          postgres    false    234    3771    220            a           2606    97834    players players_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.players
    ADD CONSTRAINT players_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 I   ALTER TABLE ONLY events.players DROP CONSTRAINT players_created_by_fkey;
       events          postgres    false    3771    220    235            g           2606    97839    players_users players_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.players_users
    ADD CONSTRAINT players_id_fkey FOREIGN KEY (player_id) REFERENCES events.players(id);
 G   ALTER TABLE ONLY events.players_users DROP CONSTRAINT players_id_fkey;
       events          postgres    false    3803    236    235            b           2606    97844 "   players players_invitation_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.players
    ADD CONSTRAINT players_invitation_id_fkey FOREIGN KEY (invitation_id) REFERENCES events.invitations(id);
 L   ALTER TABLE ONLY events.players DROP CONSTRAINT players_invitation_id_fkey;
       events          postgres    false    235    3801    234            c           2606    97849    players players_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.players
    ADD CONSTRAINT players_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 I   ALTER TABLE ONLY events.players DROP CONSTRAINT players_profile_id_fkey;
       events          postgres    false    235    3748    210            h           2606    97854 %   players_users players_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.players_users
    ADD CONSTRAINT players_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 O   ALTER TABLE ONLY events.players_users DROP CONSTRAINT players_profile_id_fkey;
       events          postgres    false    210    236    3748            d           2606    97859    players players_status_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.players
    ADD CONSTRAINT players_status_id_fkey FOREIGN KEY (status_id) REFERENCES resources.entities_status(id);
 H   ALTER TABLE ONLY events.players DROP CONSTRAINT players_status_id_fkey;
       events          postgres    false    254    235    3837            e           2606    97864    players players_tourney_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.players
    ADD CONSTRAINT players_tourney_id_fkey FOREIGN KEY (tourney_id) REFERENCES events.tourney(id);
 I   ALTER TABLE ONLY events.players DROP CONSTRAINT players_tourney_id_fkey;
       events          postgres    false    240    3811    235            f           2606    97869    players players_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.players
    ADD CONSTRAINT players_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 I   ALTER TABLE ONLY events.players DROP CONSTRAINT players_updated_by_fkey;
       events          postgres    false    220    235    3771            [           2606    97874    events profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.events
    ADD CONSTRAINT profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id) NOT VALID;
 @   ALTER TABLE ONLY events.events DROP CONSTRAINT profile_id_fkey;
       events          postgres    false    231    3748    210            i           2606    97879 !   referees referees_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.referees
    ADD CONSTRAINT referees_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 K   ALTER TABLE ONLY events.referees DROP CONSTRAINT referees_created_by_fkey;
       events          postgres    false    220    237    3771            j           2606    97884 $   referees referees_invitation_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.referees
    ADD CONSTRAINT referees_invitation_id_fkey FOREIGN KEY (invitation_id) REFERENCES events.invitations(id);
 N   ALTER TABLE ONLY events.referees DROP CONSTRAINT referees_invitation_id_fkey;
       events          postgres    false    3801    237    234            k           2606    97889 !   referees referees_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.referees
    ADD CONSTRAINT referees_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 K   ALTER TABLE ONLY events.referees DROP CONSTRAINT referees_profile_id_fkey;
       events          postgres    false    3748    210    237            l           2606    97894     referees referees_status_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.referees
    ADD CONSTRAINT referees_status_id_fkey FOREIGN KEY (status_id) REFERENCES resources.entities_status(id);
 J   ALTER TABLE ONLY events.referees DROP CONSTRAINT referees_status_id_fkey;
       events          postgres    false    237    254    3837            m           2606    97899 !   referees referees_tourney_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.referees
    ADD CONSTRAINT referees_tourney_id_fkey FOREIGN KEY (tourney_id) REFERENCES events.tourney(id);
 K   ALTER TABLE ONLY events.referees DROP CONSTRAINT referees_tourney_id_fkey;
       events          postgres    false    237    3811    240            n           2606    97904 !   referees referees_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.referees
    ADD CONSTRAINT referees_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 K   ALTER TABLE ONLY events.referees DROP CONSTRAINT referees_updated_by_fkey;
       events          postgres    false    3771    220    237            o           2606    97909    tourney tourney_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.tourney
    ADD CONSTRAINT tourney_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 I   ALTER TABLE ONLY events.tourney DROP CONSTRAINT tourney_created_by_fkey;
       events          postgres    false    220    240    3771            p           2606    97914    tourney tourney_event_id_fkey    FK CONSTRAINT     ~   ALTER TABLE ONLY events.tourney
    ADD CONSTRAINT tourney_event_id_fkey FOREIGN KEY (event_id) REFERENCES events.events(id);
 G   ALTER TABLE ONLY events.tourney DROP CONSTRAINT tourney_event_id_fkey;
       events          postgres    false    240    231    3793            q           2606    97919    tourney tourney_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.tourney
    ADD CONSTRAINT tourney_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 I   ALTER TABLE ONLY events.tourney DROP CONSTRAINT tourney_profile_id_fkey;
       events          postgres    false    210    240    3748            r           2606    97924    tourney tourney_status_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.tourney
    ADD CONSTRAINT tourney_status_id_fkey FOREIGN KEY (status_id) REFERENCES resources.entities_status(id) NOT VALID;
 H   ALTER TABLE ONLY events.tourney DROP CONSTRAINT tourney_status_id_fkey;
       events          postgres    false    3837    240    254            s           2606    97929    tourney tourney_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.tourney
    ADD CONSTRAINT tourney_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 I   ALTER TABLE ONLY events.tourney DROP CONSTRAINT tourney_updated_by_fkey;
       events          postgres    false    220    240    3771            t           2606    97934 8   trace_lottery_manual trace_lottery_manual_player_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.trace_lottery_manual
    ADD CONSTRAINT trace_lottery_manual_player_id_fkey FOREIGN KEY (player_id) REFERENCES events.players(id);
 b   ALTER TABLE ONLY events.trace_lottery_manual DROP CONSTRAINT trace_lottery_manual_player_id_fkey;
       events          postgres    false    235    241    3803            u           2606    97939 9   trace_lottery_manual trace_lottery_manual_tourney_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY events.trace_lottery_manual
    ADD CONSTRAINT trace_lottery_manual_tourney_id_fkey FOREIGN KEY (tourney_id) REFERENCES events.tourney(id);
 c   ALTER TABLE ONLY events.trace_lottery_manual DROP CONSTRAINT trace_lottery_manual_tourney_id_fkey;
       events          postgres    false    240    241    3811            v           2606    97944 +   notifications notifications_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY notifications.notifications
    ADD CONSTRAINT notifications_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 \   ALTER TABLE ONLY notifications.notifications DROP CONSTRAINT notifications_created_by_fkey;
       notifications          postgres    false    242    220    3771            w           2606    97949 +   notifications notifications_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY notifications.notifications
    ADD CONSTRAINT notifications_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id);
 \   ALTER TABLE ONLY notifications.notifications DROP CONSTRAINT notifications_profile_id_fkey;
       notifications          postgres    false    3748    242    210            x           2606    97954 1   comment_comments comment_comments_comment_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.comment_comments
    ADD CONSTRAINT comment_comments_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES post.post_comments(id);
 Y   ALTER TABLE ONLY post.comment_comments DROP CONSTRAINT comment_comments_comment_id_fkey;
       post          postgres    false    246    243    3823            y           2606    97959 1   comment_comments comment_comments_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.comment_comments
    ADD CONSTRAINT comment_comments_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 Y   ALTER TABLE ONLY post.comment_comments DROP CONSTRAINT comment_comments_created_by_fkey;
       post          postgres    false    243    3771    220            {           2606    97964 +   comment_likes comment_likes_comment_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.comment_likes
    ADD CONSTRAINT comment_likes_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES post.post_comments(id);
 S   ALTER TABLE ONLY post.comment_likes DROP CONSTRAINT comment_likes_comment_id_fkey;
       post          postgres    false    3823    246    244            |           2606    97969 +   comment_likes comment_likes_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.comment_likes
    ADD CONSTRAINT comment_likes_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 S   ALTER TABLE ONLY post.comment_likes DROP CONSTRAINT comment_likes_created_by_fkey;
       post          postgres    false    3771    220    244            �           2606    97974 +   post_comments post_comments_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.post_comments
    ADD CONSTRAINT post_comments_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 S   ALTER TABLE ONLY post.post_comments DROP CONSTRAINT post_comments_created_by_fkey;
       post          postgres    false    246    220    3771            �           2606    97979 (   post_comments post_comments_post_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.post_comments
    ADD CONSTRAINT post_comments_post_id_fkey FOREIGN KEY (post_id) REFERENCES post.post(id);
 P   ALTER TABLE ONLY post.post_comments DROP CONSTRAINT post_comments_post_id_fkey;
       post          postgres    false    246    3821    245            ~           2606    97984    post post_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.post
    ADD CONSTRAINT post_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 A   ALTER TABLE ONLY post.post DROP CONSTRAINT post_created_by_fkey;
       post          postgres    false    220    245    3771            �           2606    97989 "   post_files post_files_post_id_fkey    FK CONSTRAINT     |   ALTER TABLE ONLY post.post_files
    ADD CONSTRAINT post_files_post_id_fkey FOREIGN KEY (post_id) REFERENCES post.post(id);
 J   ALTER TABLE ONLY post.post_files DROP CONSTRAINT post_files_post_id_fkey;
       post          postgres    false    3821    247    245            �           2606    97994 %   post_likes post_likes_created_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.post_likes
    ADD CONSTRAINT post_likes_created_by_fkey FOREIGN KEY (created_by) REFERENCES enterprise.users(username);
 M   ALTER TABLE ONLY post.post_likes DROP CONSTRAINT post_likes_created_by_fkey;
       post          postgres    false    220    3771    248            �           2606    97999 "   post_likes post_likes_post_id_fkey    FK CONSTRAINT     |   ALTER TABLE ONLY post.post_likes
    ADD CONSTRAINT post_likes_post_id_fkey FOREIGN KEY (post_id) REFERENCES post.post(id);
 J   ALTER TABLE ONLY post.post_likes DROP CONSTRAINT post_likes_post_id_fkey;
       post          postgres    false    248    3821    245                       2606    98004    post post_updated_by_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.post
    ADD CONSTRAINT post_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES enterprise.users(username);
 A   ALTER TABLE ONLY post.post DROP CONSTRAINT post_updated_by_fkey;
       post          postgres    false    3771    220    245            z           2606    98009 1   comment_comments profile_id_comment_comments_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.comment_comments
    ADD CONSTRAINT profile_id_comment_comments_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id) NOT VALID;
 Y   ALTER TABLE ONLY post.comment_comments DROP CONSTRAINT profile_id_comment_comments_fkey;
       post          postgres    false    210    3748    243            }           2606    98014 +   comment_likes profile_id_comment_likes_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.comment_likes
    ADD CONSTRAINT profile_id_comment_likes_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id) NOT VALID;
 S   ALTER TABLE ONLY post.comment_likes DROP CONSTRAINT profile_id_comment_likes_fkey;
       post          postgres    false    244    3748    210            �           2606    98019 +   post_comments profile_id_post_comments_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.post_comments
    ADD CONSTRAINT profile_id_post_comments_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id) NOT VALID;
 S   ALTER TABLE ONLY post.post_comments DROP CONSTRAINT profile_id_post_comments_fkey;
       post          postgres    false    210    246    3748            �           2606    98024 %   post_likes profile_id_post_likes_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.post_likes
    ADD CONSTRAINT profile_id_post_likes_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id) NOT VALID;
 M   ALTER TABLE ONLY post.post_likes DROP CONSTRAINT profile_id_post_likes_fkey;
       post          postgres    false    3748    210    248            �           2606    98029    post profile_id_psot_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY post.post
    ADD CONSTRAINT profile_id_psot_fkey FOREIGN KEY (profile_id) REFERENCES enterprise.profile_member(id) NOT VALID;
 A   ALTER TABLE ONLY post.post DROP CONSTRAINT profile_id_psot_fkey;
       post          postgres    false    3748    245    210            �           2606    98034    city city_country_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY resources.city
    ADD CONSTRAINT city_country_id_fkey FOREIGN KEY (country_id) REFERENCES resources.country(id);
 F   ALTER TABLE ONLY resources.city DROP CONSTRAINT city_country_id_fkey;
    	   resources          postgres    false    252    250    3833            �           2606    98039 .   player_categories player_categories_scope_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY resources.player_categories
    ADD CONSTRAINT player_categories_scope_fkey FOREIGN KEY (scope) REFERENCES resources.events_scopes(id);
 [   ALTER TABLE ONLY resources.player_categories DROP CONSTRAINT player_categories_scope_fkey;
    	   resources          postgres    false    268    3851    260            
   I  x�uWK��]����^d!?���hDS"����DfF�e�t��ݴfn�#>/�W!Lu��L��|�(>y�A�19(ʽ�BW�vm�.������g��[���n���;�-)m��O�E�FU�E&'�}|/5zGR��"~~8OU����K�X��U��g���]��k�����WxD�#/���Z���.Mq0]��Y�-Vq�::��r�l���x�O��˼,r|X�%6���b�U����7�������j/���O��䋘luR��)j�U�V���u�]*�*���Q���/�\xzXO�[o�3)����A{1��������y���<\���2o.A�ʹ*M�+"��=�b�T���rW��|�����y�$����j+^=�U��3���;E �\ֻ�e��Ï������_�_�l�|Ohʹ��$+f�ʦ�e����e�9ɲIo��tRNT"�p�+v�������x��I֊�gv�U׌Z%@O�ʑ��������8����N&�X,D��F'�ab$�TY��̆5P�}�?�O�c6*\�ffE�����-��}�;����3�y÷����H��
������+�b��Z�u�l�[9}�'>�-Q��t*;���4�
�z�btY�gi�<���moҺ1L�J��R�Mp����w`���2��\�4k\��v �+�t�|�Ath6��^�4y?4]�ړ��4��tS��TZ�1�����~�o?�����,��ԚIʋ� C����*Mj�9[����2O#�x�� fA��!�P\��*�f8���/��c���o�7�����LYu�P#d܁�܁R&6ɮ��~Zn��m�y��`<<\
�V&q��K� vx����k+��V1e�l�*q"+4~w_��/��Ɩ��)W����R,!{�knN���~�e���cn]���ܭ��#pCk��(ڊ�����ͱB>����~{�{H�9�R)v����XMc^��ѫ����kP���f�8�J�WGhJk�/�vdXYpXI
�>>}>��p�t�6�%A��Pܠ�I���K���c<6Plm��F5Sm�:^��T"�x�]��N�����~�~�yS�4�N�S�vP

��A�P���N�^�tġ�O�Lo�S|'[I0JQO+TP&QEg�N���H�
����H���_�t��5�ʅT�%0�M� ��x�Ţ�/Z��٦���(�N��#��N��Ҁ�x�>!�ZUI��SbL��b��q���>[��/A����Z�=É�벫uXF��J�c���mPuEU�ㅶ�#S�wY�� �6���ڄ\Qx�
�P�T�4!0x:boEl۝��$�Y�$�:� ?e$�_����1�+���u^������9�7��>����b����� &�1�mذ�t�r�@n�J+�c#|���A���{^�ʩi�uJ͖UbQ&Y7����@�N�o����qY�M5�"o�b����5�E�l�Θ�e��|�E�V'ٶ��3TrbEk���j�QH-X~|�fm���z9o��p��V���W;�Z�wJY�io���r�y�e� ����ץ[KNY7��K?����$��w^�?�wk�kW���� F)ԛ ���ll0u�h_C��������%� k��U��MxB��C��/��H��w�z���6!Ǧ�,��.H��`�7B�����CC^I[-��a�U�B�j�J����
�[����v�&	ym4� d�iEaGA	*DP
Xv�-�3(N;��d���|VѬ�f"Ա{��C�"�N�^�A��W�ӿ�j��[��u $L�1)A7��E���B3��[���R���8��!~���@���e�������_�Lmg������q	E�_�au�ow쟛#V�K�J�f Z�NQ�{|���<�w�z1��Y���H�cL"x���N��LGAC��]8{)r/'h62�4m��<�����,cy�[r#Dr7���^ C���bXkM�&�L�q���"� բ��b����c��_��k(���U��M��4�s�~X���ɓ'�yꭻ         _   x�M�11���E�c.�_h6v�(h�(�=�c�1�F��F��Z7�̆P�U%��<����01�t�9(�{A���<	���1i��_�����]J)_YqE            x������ � �            x��\ےGr}����Cu���f.Es�ARkr-�Fl���vA`��ъ�����OuWc�@�0
EPT�N���d��ʞ���\g�D��պ�7�r�x��_�{�n����՛W����?�ˇ�~�y:��_���{�q���S.	儹�����|S���$Il�Hi3q)�B4�%�MR�������/�돯����;���ΪH%a11"���;��9f��M�f�����n����گ���o��hv"7ćg=�F~y�U�e$���D���Ȥ�k��c+�uP">��7���a��/��?� <r����Sr�;���:b��F���!�I+�ܚ����/�����o�{['�S�߃�U�����X�0��	�����์�'� R0��LLǤL\��<+<���$���$<Q�u�Қ�d�Vz����A�K4a�	{����y;�\��	m��*�#�D�Jd�$�8�K�=&n%��Ө(�8e#�&Fl��dg��y;�/��n������șۄ&��kϧ	�
�Ú��q�(m�Rǳ��	\��1q+�i��!ˈ�$(���ń�L�*p�J��~���y�n��oǵ� ��F�0A�\y<�^�IZ�aA��GW�c=�:
坖����-�X��a�{�Sr��f�:�y��'G��<'W��{�pw���@�G ���;sk衡�x\��0Q�\�3`1�h�?LH��ek)�vy�ϩ�y
�i2�������cV�XŰbEfɲ�6�i2�mw�W߯�#��̮"�	y���O�F���z�X�D�����@DV<I�5t1�zn���G��qj	�eD$ț �@T�jWr�mҾ��5"�w����~3����|���|H�0VZ��9�FU]� �-x�����C\���{�<��4��g�^�`�T�P����֙�1즉}��������z{��M~�<�l�a�1��PЁj���;
�
LׂK��H�����+Ocۦ�"�z	�F!�IC��Hd2)��۔>�������ݏ��f��_G�,~8���|il�U�U�V%,W��t��1SpHR4<����g^"�c橄���"G�Py�!d��Y�X)^-�Av��}�������y��۔?����s}����dc8�q��k��!X^�g�@R���!��1���[��S��iE��|B$�骙%/.>e��A��P��}ޏj�w&�2�=���1K����"K�cW�5��P�2o�]
Uz=n������	
E�$%NFpZ/�t�0iNC�A� ^�L�^{ޤ�K2(�I����1VB 9;�rP�F~9<H�����4�+�D��P�i:�R��>�E�b����Ϗ����~�}�����=Ѓ/���>vD��9��2A�PY�����T��\�Q�R����q;�V�1�F<�P	nN֔9T��g�B� �9����~<!=إn�J�|d�Ɉ�f$��1�@lF
���H�
OJ\�T{�<�j��=PO4�3�x%�+���L"ƙҒ�w��Zqz�?�9�Ä=�p��4�4[�BD��3�b�X[	)�ĸ��,��%���l�1$�'O�J��M5�z1i�����_n�Ъ���Ջ�H�iCv����08�|i���S�L��lP��`��ޔ�^�시{�<�s+n��$E��»�d�RL��31k���?�߭������ g�#t��G�<.�ȭcQ,cR�CU�x���(��*/7�a���6��
c>�g�U��ߪ�ʹ�X:l��*�o�~�]�x�-�����؍_h�1τ@�*v>��m��tH��1��e�>��c�v���'g�d�ST �)��(Mu�I�4��&o�w���� ��{�d�=o�����찵U��~.�zQ�#Sː�$�c�V�M7"�P�$B�c���w48c�d�ͼ�ϫw�;��M�qy��Ì=Y����
yv���%�T
�*�uL�.g�qI��ĭ$[z���E>�@���+�K$gC�6�I���?�}Z��!�#�����c����da8�p
�8ڤ8ry�%& ���� �Dۀ�8y�}_��c跠�MbV�M�Bs��9"���f����d[��~}w��pD?���zЇv���~a���\
e�Z�z�����4I�y�1/��E�f�Jx޽�Z9h"�*ӛ<R@LRL�;�}Q����z�Y�����Vvf��CC�>Ҧ�
���Y ڕTje
�CvŖĴQK]tN���S���r�!����^�饙Iىh�\����?��� ��*�B����v7l��R�>!��!ȣ]���`8
���_0�pÖ�D����($(p'�v�Y�0�u�.X�&�ʛO��[��A�����k�[ꭼ�i3K�V���"��i�s��8�$�c�V�� Ǆ$TRbĴ4R��<��\g��I��{��0y�����祽�V�T
I�pDdQo3�G**1�Z���ɳ��3�=6n�yߊ<��v��Ñu��T�D�����w�����K(y�oe���g�������/�)*#���B�i�#��4Dv�՞�ȜN�E�=v�ι�u�`.%R���.G�D!&S�9cQ��!���~�z�_Z���ؙ��#�G�a7֔'�U���ߠgrieA��Rs�S�1��-� 	e�-T�4k�k�oMd���<�Gz�|X��ԁ=$#z��ǩ�Ց��JA�c��.� �(	a7�\tY�etF���S��]KN����+e��V;��Ќ:ͥ����d���|�z��~�_>��ԯy,h}�]#gfNj[_�_Z�T��!�$�^��C�e��y!n�>��]�)z���?�|�i�9`�dn��B$�8��Xa�V��9���,y��uU?O�_?�B><�O����RJ�Xk���*'�!6Q��29*F�]^�_`�c�il�)�1%.�� w)4����`C�`b��}\o?�V�����ۂ���eB}|�rud�b��R\�g8�4�z��FV�����j���Pm."AgR䍅���x��/PG%)�����6oj��˻�}�l�H�<S���~��C�p祏&�"ê��Զ1xK-��dZ�����Xy�Y�{��Ǟ�v]};���*�E�M�o�������{��zh�cU}ud�Ox�t�-�����٤#1����9[
�s�=F�B�iWŃrX�X�����S-sx��@��s�����V��aj���>��=4􉫿6RZ��R�`���F*�� 5e�
r�,N-��y
�i2}����X�	a�Z�(���9j7_����-��Oy��zp��A �	y|)x��4�ʔ�,d���V�B�Y��,��9^�w�'�z�Bo.&���O�3�do&8�p��*�B 5E���]ܭ^?|h���fV#r�G�����h���jk'�pX�BK�l�I��.gW��z�B��P��'��\/)�^1$[+��F(��_�;$�p�Ǩ�<��:L��l����Bq�)���wle��C$�(�����2g?e�c�6��z�+V����2J9���T=�M5�T��w7�����~?���-)�CÞ\�^~�*����@T- H�S���_p0o|��e�$�c�V���T/������9d�Ӕ�B����=�$�>��#���W�p@��#M�@�{U����[���sV3�����Wv�vuN���S�6�G#r%�H4���^o�k_��N�\<�4����1ɭ�Б`t&8��>bqu�U6���KrF�,|F���_��KexƳ���<۞tF0	� >�wG��+���s�z�]M�H#�T�=kn�dd���g��v�"��Ő��v�˘{L��k���~p�"���+�z/,2�^��7��ic��Oy�,=�E)���K��sCK�a�+�S��NC���Xh�1.�����l����U=i �����p��:�8d�p�����n�������/�;]����Ҍ�8U��X�O�-u�w��a�3��r2묑��d�2��@���S	����cX7�T]m��D�+H|=��֒�v�����7����Pف<pv�����<�˼̛��/s��C>K�� �  c>I(Q��AhI��ĭ$[v�3�Im$͵������O�
<���wy����~�v��$k3�X�^h�PFE���5ddoY$:��֜}�sƳ���<�!c��p�lm�G�GD��&�����o�>߭�������U��W<4�q�ȵ��xK�e���\q Em[W�L*z-��6�]Ξ��q;�&�=B|��� ��e�k%��bN\��oi�c��Se��;U�|R�2��t��&����D)�� Gi�&9Д!��5�3�=6n�٪�RQF��E�^^t-Yk��5�"�La�3��?�w+���}+rw`�<��}��WGZ�x��"��>3�b͍B�Qq.ϩ�y
��!��Q�1�V�����k�!����6[��u�B�>_���������t��fM�GGl�8��gD�D�"99Hg�U��2��n��J�5�%�=v�ιI#I��P3��2��r�RBr%k���Ǵ�W�=ГƻK��WZ9�c�������؞MI�"�5#|�e9�g���y� 53 �&D�_G/u))0��&�wm-�ȥ�����y�>��C�Dؕ��d����Ë�rE��${L�J�)I^�rI�(j�0�j2�6��H�i���ݔ>��N��G���/?m�WP܎5sN�.�x��2B�/��^��[赺�/��_-	�%�	�ޡ�s���	�gt[����/����e��{����h�ϗG[�,Y�
����,���#a6:��/�9����C���v�2�6g<����P?����Pj@�s�_��w���fj�� ?��
�G~u���4e�-=���GD�	�K"��%��B��+Ocۂ�R�8U{��J�h{�\}������8�����z��`y���}\{��|��W�wOBИ
'9][�4����pLT������g���y�2Z�1Z�	�u��0�G�'s������x���*�|R����F�Iu���6u�`��v8U���/8���efA��;��[��skٍL�Ski���(Hk��Z3��8TA��	�!:��%>PxD�������`�	J�BLc��ϵɡ�(�^h�YR�1������XU[�0��6o��!�� �?�q��K�޷�_1�c��WSMS���o��&�:�            x������ � �            x������ � �         h  x�}�ɒ�q��ȧ�Q:DY���@CҰPd2�%��B���{D�m�2=¼�h��1A���g���/�so��*�k��,��j��\���e���>�_�Ym��V������o^�~�B�FQƔ�|�M��*v�d�u���Fs�A�޽��'Uk�jFg��)难]�o�E	�[�k�0���U-����.581[�If�]�)o�(�z���y��^����{��+��m���,m��I��١�Ğ}N��ڕ2������'���鬋�\���׊����r���^�:iu��J�]�Իjy��R2i֚M��ٌ�L�����7U�݅Z�o%=U��������w
���Tw��7%S:��a���t��Ki�P0S0�HS�/Q��M�7M�����t9��r����!�ui�`rf�]T�ͪ:�N�[en�qG��*�i��дU7�$��M�9�C��r'�ǟ�^=��I��⤩���д���1��"2��:�5��dl��t�`Z:�w�|���ݗz�Z[=큧�)Vge�y��R5���4�c�ҫ�J�1����lvT�ѩ���~&���)__�r�z9�<�ﯗ�q�_��r&�5Ϊ�1�7�\Ҵ�]�ʛ1���-(�4��ѓ�e�p3�����x9��������U2H��+����ڡ��~���u�Z��WS��d3uDh��&�L��T�e��.w�_��\�C�>�'��;���n;���-���>t��\N�Rی�:f�!N`�G�Q�r�kSs�m��ʏPzw/�=F�g��ܨ�[tig�Clu��06)÷�ju��v�=[S"EiAr��o1��G����T􌭕Tu�lI�[�~�"��j��0���t׋���0������AN�u�$$m�����l�-�L�� 39����\vlQp��l�XPl�ȴ#�������z��ؘ��hs0C�X��������XiӒ�i�ΚT�ө6�c�w�>5�}��ƾ��/{���jk��h���4�Pvՠa!M���ơ ж�TK w�k���x�W�#l ��/O�aw�H�z-'d3��ƚ��S)�ښ�9c�9�P90CS�Pn gHrs��ɸ^o.��s�0��Pvq�+ToT����"����H�8;��]q: ;ho�NFJ����i\�����'\ӘʂTJFD#�Lt�Nr����<��&�F����%�3��z7��o�t����ָ$�v��k���ufh�x)�=/z}�� ��t6����_R��l�����I�!�a5:�� ���Z���D�@~=�NA���(��U̍w,7L���?��8�����(��=�k���jh#p7Jn�Q��"sj�A��-Qk��������p������X��zڝh&;��e�at.��^&l�L#o%;x _��1�9�.#0�&�p�,�v<�����]�w��k��E�R�9D��������:�f3$�����./�T�X �-o:�����|�+�/��:Dd��C�aYl�ד�r�!F���W��vAY� �,��}�`~9�}�+(W�t�����2��\�}CJ���D����D�S����o��_��C�~ܝ����Z�������טx��)�H�l
~:Ox�s�������r��W�9�+��`�p����3�j=.������ƥ�4��Ev�7�$AJ>�	�Fw����:"�C=ݏ{5�	��j�bN���''�V,����Șf$�@
��n@+�ҋxCCǏKS^"-���6���O�i/A��ҏ���~>@�YO����
 ]�`�Xou��J�k=����/�����^q��1EU��{�(�o8�66���Vj_�
/�I6c��h��mB:h��s�=� 9AeTi�<�fM�k����@T{�a�&p`I��.�d�q��l�w�������_���^��ǰ��z��"�xY���frP�R�y�'��q�m�lD��HiO5��i�Ww�W9��^w��!�i�"s]y����:���F�[#��?'˺b��1���b ��Y�W������~��H40��tƅNfguY<$�*[Oj���Κ Dؘ#���֘mz����<�ÿ�aU��|��B�����c����ct [܆;�}��P28�@��oc�o"�I����`])r�LL�z� (F�'�����FM02A>�`��N0�\.�򌝷�W��~9�~إR�DD)P�?�`�C�&~m�����0´t�>$��d���
6��=S�Cko���?�eY>�,3QDg�w��o�1v4-�B<ƦД��I��u�'"�o���u��3C�0Jf�5PH��D���C'�!3rD��Y��Hbs�&�r���a�ڮǽ�~,K��mKX(�2�cв���
��"��B?Т�"�<����f'���v	�^I�	wZBC�k0���WTJ�
�2�-L܈�I�*+�B=XL�57Kꨵ�[��rxy}��/��}��~e�W2s�a�:6��9���E���5}jѽ�������9:n���p7dz.��1&�<[��o�.����eH߹!�������^N����o~��]�p�Օ�'��.eY[�X2��B�X��� ���� S�f������M{Qޢ^��^O?��^✭��g�WY΍��`+��t�A��L�ej��B5���Ӣ�9�{�+9��>��ws�����R�,��'�A�	3n>4�B�I�Jk݊���h{�s��xR20��72��i��([M^+�5XT��❁�=&ʯ�z�Y#�6	O�_<��~����ݴ���_u��/!̆]����[�H�����Tx(���,��%��K��z�@ܤ���}C@|4_�t ZK��ƣ�������Whܼ�X>�Z�L�M���M��r�������\����]�G�9���!&Qf�+����o�Ҷ�nobח�}L�Z��B�AQ�1���L�أ^�ZY##'�W�}�hs��W��Ó��e}X_"1��/LZȞh�o�p��]{i�g��#�mN��#��>�$[�<vS��(�Y^����|g��z���K@	]�s��^�JK��F��WR��qL����#��µ)Jsc�����ڹ�"l~�S��㾩�ur��5�I�,�Ԗ�7;�ڶ����?[p��������l&���r�!�N��3��$8^���^[O]��Ljv1�M;G��9qq\e��H�a=/�u���\?
����� �2�*ny��
je&��u�.��Za),�Y*^e�u�z1-$K��͇��u�'q����c��_G�E�eȜs�ͷ\
�����r�����i���I���c�=
�c�����J`��䖚%�5�ߕ��m�����            x������ � �         �   x���An�0E��)� 4;+��D��J�*U��V����/�I^����D��S��MI_��v��b0~��:+1�#����8Ӏ�~HVq�"�"��$���G����4��F��d��C��g��I}N�>"Cj��7j	ۺg-���F55Z�Ħ����P[#����A��3�q�s��p���_���fWW@�I鹤����>����Dy-�f�-<���"��         �  x��Zے7r}��
=�����ȥh�:DiMm��}I d{��ޞyɿ�Op��c>葨�.�F�z���S ��9Y]C�FQƔ�|�U��*��d�u��r>���r��ߟ?,V[��U�`��߬]�)�Z��k�Q�Gg��)iJ���5��o��o:{��U�}UX��ڒ+)q��g���Z����n{W�j���jl��_q:-����tܽ��?��@�����C�Z��L3Iyk�*!�2���8�í�3�+7�Ek��T�|�X��AY]�(�uY^���>���齜O����^����(M|w�Ve�M%ש�=s��ڂ��`�M��o�E�w�]�8��}x:������W�k�❷�(�
�٪ڍVT|ա�R�t�"E���ZLC��H*�؝�K7�W9�^�r���B��d� ��r*�;�d�Ŏ!���f�֞|���$������vE�YWk���];��~x;�����ّ|��R�ι)�
6��r+�n�AS`3Hk��2{R]7#)
DI�.�ظԶ��;:�B�~���f�k/E��2�cD6�M�Rm��Zynk�6�bVN@�>�3����#΅�W������G:��<^�@��rU��|V�5� -Qì��A[=fh�=�j�Ox|��ɐ��Xi@�=T��wt�zޏ�^Ml6kG�#�ď�#d�5^U�X�.�r��0��[ԭ�}ZR5u�\��tBz,���9�^��gw}>�^Iv��ܳ順�8�^g�J�=h�x�@�୾$g|cUPM���!oLQ�-����{y~��H��7��e�w#$X�	:�'�*N<ᘩ��heu�\J���`Q�G�D'*�XBc�E��·����������&�tց��np7QC���E�n���[]u�\#�t�F�\4[�<W����� ?��q��Ï�%wC\OmV�)��E�C5U�(�\r�MW��v��5�ڊ��Sa����`"hj������әv/�?�}���p��P�;/	�7����C��-�Π�l,+A�0����H0VU�)Շj�[~'�����&�{����zP��`�T�=��V�T�Э!�!to���[��6e�d\f�(�����3U�yyq���^�#������^s68O�ĀZ:`䦗�s�������ޚ
գ�՛8��iMh}J�k:�6}w��Zx>ްǐG���R�7B/����[ g�V�A�����-�a/4G%&���a�������|������p5q��Q8}�Pvdej��6�A�f�Fո	tqe(�CQ��Y�"�J�r�8.��`d�Z�r����ڿ}�����ۜM�H�>(Ⴚe�ay��G�T�ρ��]	4:X�s�!t+l��z,�)dȢ���{�(���Ӱ5�����;ki�O�A"[k�ro5�������w=���޹��C��T�N�NwO��e�����/���5�=�(�?KG� ��g���
;ՠ���4LII�C���d�?
#��>]*�����q=��拉�07�v������b���f��F]�2�F�bG�m�T�T�>��w�ˁ>�#����ɍv���mZ���lp�����Tǣ��y�3ȫb)��[���`�L�!1K3`�0T>�=�����p8]�����&���E�� ���+�Ui`6���(���`��h�C���'��
�qyBB%X���;�����t�ɧ��h�t�n�c�_˗�̈́�ָ��&�[ g�V_ck�F���zo]QEgR	�o2�p:�0<v_���<��y��%�!`�P�
��wxg�����@P38k��I�6�1r�C=V�P��fݍsÃ����,���ĦWUs)��P�(`�1�Y"��w[;��6��5
��6� MP<1�X�aP��.�:c~���.ѡ�@aK�cȸA!8nD,N4�
�{?
�a�������Ź��d�(Tugbs��~�����֦�2��e�d<t�d}k���=��*� ���ju�K;V*<�e��j:v�����k���4�/���&�(;ʸ81F���y">�AU4�3hk�����0�S	*���O��qy��,�x?ڽ��E�?n�T)�`xH�T��4���L�3hkq��G�nN�"S�h8��f��K3˗�v����3>m�WF�7pV�F�g+#�F���R�,��Z�u��66�a�F����y=ؗ������O��2����Fi���jƝ�<!���o���ln�A\]&���*Ŏx� q��{���E��;�o��"6��\���z�����r �L��&�f�� ]����Hz�9!�.�(t��n��/鸗���t�H�F�}3�QE�����06b7w����(�VC��<�����`����"4��9�\R��sY�!���{�?ޟO#��g6LUu���x���6:�\C��	K�
;���GQA-�i���>.��p������V���_�?\^�l�6�	�A1���0:{�#�:b�[��1�ہgP!Ƥنo�v�A`6
��i|���m��/�T����X��ӛ�˶72��Q	tB�B���RǦ�}��7�A_9�0��s<4�h�؞������?f�����6�C�ügq��(�%(�6�����AZ�G}��<�����Ơȱ�@-�/�\Ҟ7���!k?���å��R��f�g�ք���5a5�!��� =9�������:��؅y6�8V��g0��ҏ�k�_�k��[ g�֘��	( 8�Az����)�F��T��H�tzR�~��^I�QCy"��V���Ė!�-w��c�Z5�h��@��nD nH�@��u�@yC�Ow�d�qE���j��SR9w�*����u��A[#�;l��P_y�4{Pd��-������a��%��v/����[�����Gd��A^W�
ܘ�	��a����7Q��ZB7^C�py��efb9�����t����Ѧ�c������}� ��
��f�f�V�n�=�?�˻p[2N�V�Y]^��?�^>ȣzz>ޜ'�ՅoM<v<ۖ�iho����M��@hM�*�a�pc������Z�;��φ�|�EF3e4��_���' �f@ Ӏ3h+>:�B��$:
d�SAF�5�ep�cC���n����<��D)��9�a�Mq�� F��ll�l7 Π��F��]��#��,�r�%W�ie�˛}{Gg�}������"��A0��M=�pӣ��UƏ�lQ`@�b������<�䵰�1Ɔ��v4~�c`3������yw�'��;:<����6�$���y��sM��ʫ�ٞ��ہgPq^`i�Q���E��56T�R˿��=��}���$W��d�R6�9����a
@6�����m�3�kuEB�J`\�z��� �Lb)�%�����~�OG��S�҈r����T�W�������p3X+��iP��`
05|t�N��Ԉ���Ç㧎³�Fy���E(%�p�HF�{AYSQ��H�ipmՍ!b�V�����a�~��kń��W���o��_�i�q%!���F�&�����K����ln����ԃ=��k��,Qu�$�J�v����t>x�'B�v9_�vn�Hm�	�����w^�C>�뱃9�w�ρ���%
�?��%\�#�J��X8~���ۻ���-�����9uA��0����L(�>����tq��0�I��Ǐ:�*C���\X���Ѵ=�^B��/�q5��.0F��r�5T���N;�i����"�F��uxb�Q�w]ZP09jt��s�5��!,�C��A���t������_���w�T"j8߃V��KdT5���m���63�X%'�U,���ޝ�#�FR��:po�k�gȩ�����~�3[��܆�j�X@�f�����h�ۭ�3�kn������ac��w�Ju����-_���oO�y؟O�W[�0�鰃�Do�����]��t�Ȧ�@g�?��u����            x������ � �            x������ � �            x�}ZI�㸖\�NQ���^�"��5ϳB��H�%��8h�M�m}��X?�Y_֩6+K�#��<������9ܡ��&B�5�<��n`
`�9&B#M�7c�\e,�~���� �Ƞ�qc�?����a��nU����:�q�9l�C��������}�+�å�n%��a�f�2������7��#q��_��a�)���@2��;�(G�jM�L�a��??y���`���u.҆_KՋ�8uٴ9,��j6���	���f��p�|U��^-�@�X��~"�j'�ا&�2i�)���)]�k[H�hd��f��T��M����s���ξ�C�x��/�~%�;���v*x�t��/����Y%k��
�ۛ�I�g�,\������Cv)�Y�ģX(8U;0�r(T��B9��!��iSh FFO���/yn��k�8�UX=�ٮ$&��u��S��n��"����V�_����=��Y��7W�`�~��P��`j���žkzڣ&�����9�����՗�N^�x��_�X���K�~k۷S�� �ƺh�G�4�l����K{q�/V�t$:�i���~°���=l��mcS8�7)�}��?-����ufI�\���o�-1X/N�6�O�7���&\��b�dx��d^ƛd����N�y�^8�7E���x���4���h&��L��x>s�>2jE�k螃��k�~#�����#Y1>bI�;.���ݕ����2jҸ8�J��#���Z�-D�8��ǄZA� (I���6�6#k%�Yd�<'tM
]���ѼN��*��_\A�?v���R��(J��p�YG_�xQ]��2�j��<�Z����s��y�2��Uk�7�����)����6:I��yx����x.���z���%ݟ�d3��M��N绮�fZ����k��w�v��������\�#=��H`���J���X���l����m�d���dz���^��oT��z�*V���@(�m9:φ������tp��ja�>T�]r=}Se���'�k*��M�8{T�4%Bp��'`��0zI��{bU�8O�a^����W��Ѯ�-�݃+��d�2k�:oɹ<�V�~�y�J�_j����j�l��#Q-�oڔ9&���ґ06�bʧ��F9Γ8L�zv*�3�k������a��{���9��Cq{��W�հ�l_z02�}�n����ڰc�6�.�ʓ*���3����Z�H�A�`�s!@:mc�3���Q�i�dVK�������o��_����{ņ�դ?b�բ���������U�*&��9�v��uE��g��򓲋m�|��8u�I��yϸ~�f
�4��H�Qφ�:M��\�ћ��˻R�uۍ/�E�<��q��G;��]��O�b�E4�z��U��0����QW0nl�QGAC��)�B�r`�_�T�W3�F�KW���پ�T�z�ku6�N��]Ei��밒�u�\�x>x���b���8"A�m����=|�c
FG���C�ej�u��?�x�7�N�X]wj�+�ݺ�tЇ"�#kT��:Vs>γ:�V����&;�U6|�k���a��pp������=dTJ����藼�d.�䗼����fz�7�f�x�A���e?tT���t��dG�QS��S��svr���`�͆���<[�.�B��s�B��1�cvX���<�%�&� ���7L=I�>]d޴{�5K�UV�����4��m�j�A�R��9���IR0�O�S�
i?$���H���eB�Kfԣ�\�[��B=t�g���y���"ۮ�#T�,O�r�Z��.�弑7��}�Ƥ����s�'*�"O����	�p���p����܇��P[@�0FZ���OR8���\�O!e���b{IGb�.�dֺ<�N���Y#.��WC�U�S��������]IP�5t��\��#�ؾ��I{*T�V�Џ9�D���l�;�ڱpo�Qi9��N��c�����@��2<AY���z��&-2��>��c�#�a���&0Չ���t��k�U����(��*��wU�k#ѓ�������8%�fK��3��,�9�j�˘N�܋�i}ltD���Iho�q�x�����6b)�h+�(�=���5&������[��ýN�-�_����J�����:[e��֦bS�m}��R�F�t�[�
��KIPl��^�N�S5�HW(�	b8Q0o0���l�!�!Sܨn�0�C	7�������~��b6Q��ȿ7�鵼��ݙ��ֶtd�j�y�R��np���upQl��|��.lOi�K�$�c)ؔ0��4dMH�X���(�k��Z��|W��$8i:�'#g�[��땲t�*/o��tFnk$��R��X��R�n������?g "4�+� �\=D��DLiA|��vz�?�����s_��a���A�'�<�oQTl�]��6���}��fA=S�.K�����������'`��r�"�b�D\�>��0���n�+=��2P�&]䇃zu5����*��>�jak��>r��<��r��e�痳'E��|վ�Gm�	J�(�rL|����6v5r��6���Q�O��Bo$n����D����+�nz4��.��ҩ1�n���f�X�OS޴K�����{��$>���iz��x�p���؞c�d�DʚI(�@� ���_v��^v7_�[�m�&-b����ѥ��q��֪�э8:�4]��ny/U�xʻ#�{r T(e�p���.T�"�ɴ�5��A2���h*ch�M��/�F�լ��6?��E:���t>�a��_�Q'����Ι|�Ϛ~��m?#��gw乁6�9�0�Y S#��HI𞜾^b�*����0��hf�8�s2]_�h9���P�^��}���o�[��n�E<�}�ig=Z��:��4E�	T�)���)���L�F�*��?���t�g3�ﰸ���7���{��ۥٗ�-���]�V;q�JöP�����0�x,OVǟ�졅�W�C�}.���z��W`��e '�
|�2T0?��p��'6���b���[�@^3��1I}K�g֪s�7�0J�˫ڡ��8�n�(}�Qjӏ
�}�0A07=(U0��䔀H9p��c�QKa�I�q���/�F�(,�ToU&Nc���ʕa�X��bv�M/��*��y���I��5��<=(���3=Jjüp 3	,3���Ü�RQ*�r=��Y��(�/l��oD�Rv*�l2窭S>���J��k��#�:�ܹж}MP�!��l>+�
����t����I�)N �`�.�7�ڨ�i&����X����Ѭ���P葻ط�d+���Eh<�C��Z_|T��}c�>w��i�D8����`��5�G�R_B�p�ÎH�TAh�t��V���/�F��Q39�?$8�����\F�g��0�vKQg�[z}&�ro2�|]��51j��ot+��n��M�Cq�Ŏ��־+ 5#�I�u��4���.w�1³m�8�n͸�OU������x�ը��#{��Oa�>��)~5��?� ��>�0���<�.��xe�>Q��d~b�
h���|�����a�A��%,�|��GǞn&�ƵO�HZ�=��j�(A����+�ӝ:��(B���r����6Az��9H.s}%<ߨ�fQJ��\������9�����:9�Ջ���%$3RVC��"K��W�����`�&;�?�5;(p\n�A��͙\	0�iQ�VA����j�e��'0^���5����t���<Z��ih�?#�"y�f�l��j3��fݸ��x���&�'�T�T>�Oa�᐀�`�`zb[)H�7&�%\zi(�����nN�&��$og�ɭlU��Z�Qu���^~J�S���4����:I��x�p��)�c�L�>"�{<"1pIB������2^�d���]{����x�N�����䬺�2��i�������ލ�V�"�u�O��u?_7� �+S ��(������s<���Xմ�?���Z߯r�'�۴�+q�����!ډ���r�V�f�v�3RU�":y��xf���k&p���I��a��ǧ4�ah�� �  �Ʌ���9	���e�_��=Y��֭3���
����W��Bݙ3���M��Yw8�m|Zl-z{}����[��D \%�j!_*5'�� ��@�H��?�5(��o�:�6����_���m���\;�Rr�g�"��a1_�ҥ���iq_nʋ!�+��k^����Dx��� �B�2R��
���D�E�m��Y�ȗ�_����F1��X�d�z�M[$ۆ�t��{:�z7gٺ{��ҥ1
�2<,ǯoh.�<���y<[ꇷ�+�BC�z��O����5}�����F�����ڇq�p�wO�b9�h��>�<dǏ�7�ӃIt�U_�E���$�P��0�D��NM/��A�3M����F9V�i��Va,_�x�7�v�H�E�/��򔔋ˑ�gݪ� ����~M�ڽ��=���my����
���KP� ��o:�a"f�Vf����``ʾ?���OP�8y"���ܦկ�-���~����
��D�e3Λ�:��a��[�c,���ḭ��G�� �����@���}xs�Ԉ3a3�*��4/�Ă{�ǫ�74~��]�Qﰾ���h�C�[e�AQ���a�!��5��x<�}MI�8)>~���}lH
��a2��aS�4��p̔�^FO�:��l��x�4�?;��;od�9�ԫՎ�Ad�q����(�x}�ڗm�Vd�^�q�D�y>� &�ǩC��ES&p甃	�(�L�" ��p߿ �+�~������=鐼~kyIEE�[�<��=_�H��V�s�굖��&�f�4Z���E���ct@��jD��!�G�Q�#���S���d����QT�a?�#gz[�E�H����Ҷ<o|eg��p}��qma������G�+-"��G2HG(����LJ��iPwd;���h�{�����{�F�L�I߷�4˶�B��;��q��(�����`���x8B�{{>���y�`��Gz�l����+����p�p�6�X*��yF'�e���ハ����g��{��K)n��P�ҭ9��:7���!��k�V�;�ykorI�����$��]��h,���?>�AV䈃�D�E�(ǁ��w�Cl��0��6~��^?�㕇��E��W�6��Vk8�vۦn�[�d=�4-͖��":��zز�Ϧ�8`����x���5�B	����3�1�h�l`��?��f�<=N���^�E�mz�n����V��i��hi��}�V�F+z:$��tl�?>P��>�T&&�6�&r�K8�@AC�Փ��^߫7r�}}�v��}e�|u�-y띦�����~�_�fcE���q�U�����RH������}��1�0ps;@�<%�����������>v=g�,�o;���v�ml�{�&�qQʇ�m��|�L7�ܟ��?H|������/6�,�         �  x���͎[1��7O������O0R�1H���h&}�:�lfVYD�,o|l>8`Ɔ�r�<�B�ᠣ 4�I�NLM�j�M*C�,Q�8ءxd�����1�C�s��DZS!�����P����B��at� ��"Q���m�[l���������N�e����:��u?^���D�'�������?t{����Jcr,�%/�<���d��"mxzaR	�"O��s.Q_/��t��q��Iݶ�~��>�$s���x�3��V8Ŋg1A�f0���#��/�e��6��-;0 ���S�Î���_�o'?_�7bYj_}�+F� �d|xӑ�$�W�Z��	�苛"��U����UM�ӳG׮��~'k��jJ�eJ���X���+-��	<�K"Z"���%��'߃2�I{E�Z:�D7 �%ѽ�/�|�/�Sr�����Xך-��2$ͱb��R>9w�)��R�H"P�2��uf�QB�����/����p�{���         �  x���͍�!E�߫"x�_�SK6�
ҿ�$둞&K���s/��Jk@�)�|/�^�#�0�%��5��S����b����г��Ö���E�����c�0�2�� �4����hL�rg����*�����$��q�8�nt�}�&_�K`�;hՄ=q��ط�����ۼ�Ce�"j%y��	^��Ro"?k�3�m-��=�Lm��e��L���=I7���tJvT� �:z�����]avmT��GI6n/�Rg��4�:����V��ho�� wZl��mG�RH�=:�&Qp�a���6�'�䎓��kޛ��o_����ݎ����x�}^�o�������Now	:�:WvW�{��;z؄�x`����5�]��4�ɻ��R�K�cl�5N���Ż�����~i}�??^��o	��         �  x���[��6E�ݫ�ؠ(�Ջ�
�zp�?B�$@5�

�K6�､��p�mπ��@�N�*�-6!�5l�K`�A0��}y�Ȥ@��>����/�i 4�����_,�n�y|�������Na����� C3�[��i�|��lz��x;0����g�6�<�yV%jn���;�L��(�C�r��u���x����H,>��# �hi��p�&�O>`�5�T�p0��Y�!tT�3�y�R׋���q�>�S�?�;f)��
�jz��Y����A���\$@1�j�_���(����y*�ViQ�\g��b9�yFp\˫�f��d�2��������'�уN��A������g�>[{�s��K<F'$,���g�ߔ��F�b��v�lv�����Q��ث��ڙZ�d�:y��n������֭����Rן�>ǃ�گt��eUiB`~��t$H�>���9Z#����T���)ԥ���y^�%�k-Ut��k��"��r:#�ߥ�S<+������sw�{��Xޤ���Q��~t�*�^E}:�9vǥk��ؠ��T��8��3[��w��?�k5�
TM���<k�u�s���!ݡ]����Y��h����v!�ꮗ>�LrA$ge=���G�o��s8R�)�L�g�	sW�X�7��۷G�o�������
Y      I   ~   x��1� @�N��26{�:u�‑Z�K��+D��ӯ2�Xeh�7Ȇ���D^$W�Y��&���Dm�.D�Y����g�9P`�i�G�&�QP���ǎ���x�����3�����$�         W  x���Kn-7D����@�G7��	�[A��T;���#���W-��"��q��R]#Icl�!L�D����OJ��ۢ��Hۘԫ����cV�*�O-�y~��h����HU�Աm`)�68�{J���o�9Ǵ��Է��7�ڇ֘.�Z����72��xx���a�,��V�9j����_���,�S�����Jﴖ��"��r͠����	&�=�t�E�ZinEǙ�[Κ�KU2�B:�@�O�����2y�sp8�M0��>V�%W����F��kFcy	�X��B-*��cOZ��l	 �giY��F��ɛk+�lf�m�G��*�� ��!�F��9G���4�4�l�04�k��������e���#�UJ/������w~N[�j/x�luT^��vc�"�<��d��������J	)��e�%���5�>R|8�AG�p\,{�Ԗ��+��q�����]���'4P�&�^�'>��[��o]p�
�A���QQ�D�Im�Աk�2��N�en��:.3:Hd����S�glb��+Jy�SGpy���,�/U&�T;vӡVM�6�4�c�-g��,��"�TGò 94���t|$1�.Q�F�ݕv8�P+Ө���;,N�ky�mkړ��{5WAa"Ʋ)�#��&��Dۑ��*j�C�A�����|��_���(�洳Rn ��i��5�Z�5�>=&0n_p>p��9��ᙯh���ygKy�a�9���D�ʊv����[}Hdr��m�k�����c㶮�Υ�� �N���Tx.BM�@�;����3������+ goG�
�Ĥ��0=�6ɣ�%�����^��}kG±��J׃����L�{ �+�6�K7h�汞�	ǵ;��x��^N)��p�w#[�
@?;4^=�.�6�"x"F�5t%6��:S|�9}Z.�n_AcG!����3��r4��F��Ck�L��9k��$X�Ì�1�5�&���4�
�J���ӟ�Yi���\5ΐ��������������u�]��yh�3! ;���B�5�\����|91��}&T��(Q�~򡧰Ś�V�~�(~ᄟ�����O����         �   x��αqD1E�X�< 	��Ǳ!���l�0���<H����`� � �#]���o��,�[��	�@�C�D���~�Ѵ�����c�^q��Mx�#^�dky�f�g6�Iɢ�V�]�V�W �.`��X�80Û[�U�x0�]D���}+�*~7K�gHL��k��ە�$��g���Q����</�LW�         �   x���=j1�k�)����"E�4[��&����%ɲ�=$��G�>������J�`E�c�yXҢ6�Q���iҡ�u������^O/��z�@�"�	q�0�YrIz'цq��r����8:��x�|�x�r��������0��6��{g����Ĺ�m���F�;K�^��#�b���B�䁔��$ށ(ZCKT�����j��v�y����-��D�"�Kv�x��@��eY~ � �!         �  x��X�nd�}�����"Y�8v#A�'���M7�e`��s��F�|�iHj�r�^�N����e�َ郥уe�����J�Ps܄��"j)�dy�_�82�^���,S�A]���N�J�A:ț`b)�_�%�Ίs�J����ř�J�,bs���nZ�"��9L-�oǛ��e�Iovv���w�����������N�̯�0�׿��Y��W�o�&2!HՉ}�Qt��D	UI"��L��F,����j��<�9����կK~��.���������pAܺ�-["%+M�͹E��߆@���bcl��ڎv�E��[�S��(`�x��F��ȗi=�X.��7s&���+��kI�v@�g-=����a��p���q~>������a���dZ��K�����M+���TU|BS�6���X��h�9�����x��;��x���7�0>#���o�z������=V�bRN	˳2=*��A����t%��Ý*69��5�\���U���C��x�kq��o���v�� ��u\�S3i�s:T�y�U�-N�yR_�}Yׯ�u���
�"�ӓ���X�����hK �i�bkA5��찆�I�X�d"�(�������O=:v���:{�m��<�E�Ju��fo~����a��^����C�7��F���@����Qzvm���*ƌ�T�̔� t��mk��O���ҫ�.q�@.�Bp��)���,��^π�p��g��e��"���."D��
�"���j���^�X�CtS)ʙ�V�f]f��[�� �2e��C�fTx�3�&������?z�f�t4�T'b}2�2{s���dcv�mx����G�]�w����L|�^��{x {��r�����A��R�ڤ��¶��mP�	� �i^�#46ł�� �o� 9CO��^�q4D��J�N]�@ ���>��nn��q�O���ć�~�?쾿�ށD�L֖�8��ҏ���A�MM!�l`�\�=�Ă���,�luM�JN�	� �u_baO`�\�#.!;&;d%� �+w�!�t�/o��=>�5#7�V%N[s�I^)e[����U��G= ��D�vQa�a
0k-���V[@�D��Uh@��Q|"�=D٩U��pE�
�W�+%����H/��y�s����
|ES�C�
{�m�H�H��yF$��<D� ���E�z�j��!����`x����;����`��"�/4���>����D��������q5�xW�M�3Rv�Oi��ܬ��v.\��ZF8�@� �-c;$����Ԥ'R,$ �}���Wx�{@�/� \���@�d�� �~��c��/�Rc������>�.r	
�y�]�`$������ڑ��\�B��i�п)�Ъ�����	9%dui�tc��Q��)�sF>#+��K��=�������suTD��m�+� ;�&�#`�����ɖ!������q��8�o�k����Ш6��F,�4��"�R�aU´�i7P��U��h�������:���[I�e�e���}Ȳ�,fd��3S`����ՊY�D���)��#ٓ�ǔg�ŭ�r1���41�V$�RUK:'k���I�>OU�,c+e��t�i��unԆ��9:� �`��`P��b��������LQ	o�M��1tfT�W,�3�^qӹ�5�n����ɦ$�����\��XTsǅ�����A�f؉8��Sy�
� ��<%!�/7�+:LKU8E��;$���j����q6�̒B��qH�r���E�=e�o�O�a�ܥ�N뺠+!�V:r��`���_�X�j"pub4`���c�1��_!ī��>�_�EFv�DdX��Ch/H[V�Rk�匸�m���[/������N�;�%pG{�iC� �a�X`���@z�����m0���!�c����<Y(z��˯�ye,�W�
6�ļ04ˢkB���q3AM��7�U܄M�v�pS0x���py��Ｇ�B�Y��uO��4bPW���b�X��R�la.�~iu"��`��1O^������*�Ƹ��.��u��BMO��5�FJǓM�𶌅�}c�:M�E%�ڦ��2T+�{i yK��t��<�>|]�_//..��[!t         =  x��YYn%7�n߅�DQ�%r���� �G��س�A�6��`Hz,��*�����L*���e�GvZ�e[�,n���b��w��lۢ�v�����#Ҟ}m�R�"�Xԅ��ٚi�n�G�cy�5e���I�
�&J;E7��$�ᕏ�����G��G.|�y��2'EJB�P�8�r���������Gz��7}����_���R�=�p�� �b���ǽ��1�V�sP�n$'��ǦѺ�G�K�ׂ�զ�ʑ��g�h�P߳��Rے[A�1V_c�S��$)s	#WՂ�[�t)����|���q��q^NM3��d8��i����5WUMI�/��)�7U�8=M%[����=�5�5'��6��a�u,��
�a����~�[B���E��|u��V�=V���C�&��om4��HŽxۑ2�i� [�)VG�#9:]������9���(gT��yjn5�@�������c��48��{"����<��]��/�v:�����b�����/�}D[ᕆ�v�� �xN��e"�V�ܭz ^��k�L��V-�Q_�;F�u�����m ]�V���u'n=,J�Y�Z&�NH�&��se��;���o%N�*��J\�Z����ZAa�h`tDD�Ñ�T�}'d;2$[�%3�*7�m��l3{�)پ���w�DX�O������V�Z�7{�Vtv�4��J�3�Iv�Vr�Y�a|J����&e��};- ��j(��3K�ND������k������_����,�B�/=�,36�ݽD��(Rb+O�SpN��0��W�װgJ���0���pJ�5[�f����x�I��Qw�UKEK?�N�{ˉrX�T^�sM\�C���c/�mL�f;N��_4�:�\��Ϝ1]!�)�h@lg9.�a���������d���s����[�"�S����x.0rw�>w=������{����.���Rim�%�Ke�[q��.�(.��
Y����m��"!|/�r���v��;�5Hc�ʜS���	����5f��v���w-#�f��A%�e8�<yw��b~н}h�����i�*'`�� �\1�2 b���V���K����nW6�F!������x���9�&ݻ���+��p߈o8�p��#X�Vѕ�u�
牏�0?=A*��^P��x�."v�W�MO�MW4�}p��͙�C�>���ւ�s��?�o� X��}[tY�%��v�nW�Vg�±r���qz�~������'��&��%#9?�)���%v0�v��,��@��*�n���%f�ZG�]MnෞP"� ޶4���m���'l٧2��0��ϦN�����A�p�%ݫlvql�M�Z��-���SO7���J00��fe��꧀�����ֲL
��4��vVč�ϊ��ך�ܫt�����;���������C�C��)�@�7���6�:_�?�� ���s���өÂ �'�@=K��<Y/S�A�_�R�|������N��z�E���^�^��#���/�#/��q��`"�(�Jw�T�Dտ�q_#/������A1�w��໖B��\��i��	������/���            x���;nD1Ek��0��l�DV0����"M�&���M��@�s��D�G5Ж���r��vâ���|�����J�d�U�d���(?�����0�2��ϯ>ć�ǰ׼�rW'�s��A����Q�s�f����k�z[\gP9������jMAI�V���tn�|�TϡD��ɠIА	c�gZm:��́�Rc���R���h�l.񎧫c��W���co��dv�?�����4���\����q��n�m��v}���㺮?�F��      !      x������ � �      "   �   x��NK
�0\���^I^R����
���k�J�MK����Aq�nf���		�Y	::�ҀQ�
�C��!�)�|3�<Ğo�!呡@A�7�>pU��x�|?��Ӵ�됺�T�c�c�#���W�=�te�ǣ�2��!���_�R!�u`�6���m�/�URx�&��(�*zDy      #      x������ � �      $      x������ � �      %      x���K�4������/tWhi�=��x���]Bp��������D��+UBn����H)⽄�t�Z���l���[�n���_Kt�yyY=�;���.N��Kz��(ID�Sr8;;�4]���o=n��R�u�]~�������e�}��ǯ~��7���o~��/���D��х���T��c��d�����^����?��S]|f�����S^q���{!�$k����Z	1E'��E�J���}b`?V���
����mj��y��kKn��	�6'qWw�D-��ޅ�����r!%���n>�����G�BL����]�{��Nws��6�d��'ޅX5�Cp�r��wt��F�ӗYji��C�����������R���[������D7d�R�)R�]��s-�ޝ'I\N}ZZ�'�NA��a���|�q�\�]����EW&��]���6�j��@�~��\ŅM�4���Y�2��9�5�q��z�i�|Zu�pc���,�)L�:��O�H3�x��\�$b���:%K����#R5��/�1�-!TG��ɀ���e���d�5<��J��qn���Fޝ1�9C�	���!�wl+1����U�s�,�SJ�Y�{K2�볐Eu7���Iu��]�ɷٲO<mbG�3����'�����|5Jk�1JdQ�$���h���_C�2H���e%�L!����uw��B|�}�A=e,�pwx�|4(B�KJ�D�o�:�փ�PY�:��e,���7D�@�X�%�vV�k��<!J��h�(D�`MRK>m�����0R=��|Y/e��!J�~�M���c.�Nis� s�G!v��:ǣ�������:^���h�{�����!}����W*�W�3�W��ǅ�ƅ��|�9oW�MN�rQ��"|:#zt�3��E��O/���� g� kA������t$�ux٩>ߗ��bSا�����C�S�(���B�P�h\���@O�z��G�|��I��9����}���\t����^�@�$��^$Zl�o����#�|((Q��5�C��4~�!toe��<��@��`#�����rC��KgVq���.H?��g.��M��m�ӒA������[���F;��S���5g����_%�8���&��:<�����9��8)���r�ُ"��]N���r��J���x �����o�����<{�1]V4���A��ُ�s�	m�qb+����r'�(C���$"�p�)g��ˍ����E��a��e{)xti��Y.�^���3�)�] ��D)�y��`C݇��LN�U��?��L���V�o���v�r���2h�\-,���k�ӏ���;G�����5�Ϡ;�&K���o�65@����ڸѧĢ�t'pqn$�b)�_J�,�\�j��|���&����7blD�η!��x?ER���a�QO)f�4d]z��R3Z�VQ�і�F$�J�\Vt��;�?�yV��R.�d����N�J1�t�Y*u8>m�pV_�4d�?� �G���ythk���k�όA����*�Y��D9������U�%�YE	l��2-�P&+BR�s�g!�(2(5��}�YYU~`.Uc�7\V4*xgtC��w���~�y��M�s=�E�%�݀�A	�f�����q��fm��a|�)�Q:�k�.���K�tP�D���� �h����X?��\�ĳ�9;�6{���xs��^�!����~"��|tQ'[$��/�;��Hs�3`�u}�|e�] �����BY�xuo-���"2GQ�6\���1(������9A�Ι�ϔ�Ft�s�+����w���.���y�*5�U� �� ��V;֜�3��b�+W2px.�3����g�s�qٍ0��fe���H���uѺ {����wb�Zy���f�G)�����s*��ӺmL'�����VO�g�qv�Ky+��z����D90��K�ء�ӵ;����;-���y��j홏������3�$GG����E�e�-M�Ý f�4p�Ufǽ����]�į4<�PO�x V�u��mB�)�B7��(��l���EHm����gJ�G+�<C!o�څ)JǺ�T�e����+c��hS:�8�嘷�ʳr9"yָ�qn'�v���o�
�2�?��.�����K��ԞF	��Fˎ��\U�P(3�����U֭�*�Ժ�p;���Z�v�`R��\؛s��ț\��H	Lj\u�Ko떣KS��d��p��.����+x֫G�/�T��#�Z{@���v���Vd3�g��H�ag��ލ���_
&�$�֚�[�e���$Gb1��� ��J�=V�!G��5�h�dp�:���m' >ݚT*����e��$_G�F[ևy��y� �"5@V�U�ci�K���������N¦Q�-�%\d��yh�D��5�MFL�F۰DC6�[��*F�{�
��e��?�ͳ�@}V<9�x��uCMU]֡.��+轂�-��%t-h�c��~5�d���V[8!�8~��^v���醢�R"�sۗz����Z����x/�>	��A�K��b�ƶ!1�WD�;T���y��s)5�b�	k���5���l�ϻ�s��h[������Rҭ��h�\�[�.��]A=�e�FO*.�D��N�E#��s;y��ڥ})HŁ��f_*,��=��W���R��Z���Oü�u{��G=�N[��.PeCs�+Lkb�~�%!�Q�et��>\�Q���ݵ���� Bq�ˬ"���)��;e�"!g�A���%�{T�b,��a��`�N!�]!��#/)��r��YRȎ���e��ƾ����L�b4�����zp������)rr�.�vRUL�9a~���:(�7�1�!O���T��	Ҕ ��)�fU
�lv7��ڹ4�H5���ZE٢c�����\i�Z�.�og��ϥA����[1灴�ܽJ�qT�P.��^;:_=�������X[<�z�ԛ9��_;:?-�1�U	���k�h9gm�|��U|��|��`���3�ÅQ��ZH
��܅�����0u���i�m 8ݎ�v��r�����ѹ�,P���lSAR��m+�T:��n��::�fM-b�C5����ojt��P��!�ut��̨,`8槗�g�kyTD�^��e.�ut>�t�9?]	�ꡬ�D�84^�P;�w�
���r%�$In����Zݰ_;�K���i����9�ڳ���\�G`1�Ų��}�.o t�T��E�l�&��ب)J�k�������m9��ɛ�i�E��d�]�`��L���f$��	�|UB��.�n��Xŉ����o���9:JHu���/n�F�O�kk�t��?:��[wR�v�|ؙjC��������%.�5i����s�B���l6��ȓ�ŗK\|m�DQ�>Q�]l2y�V6@�Q�/��t^�4)aƤ[� �N}y�|<f�j�QK�z�
�I�::N�����yB��*�rL��Ru�6i���aX1N��u;�M�M9#�u�kc��ֳ�[��U��a�.���r���2�ˆĽ^D�Z��cS$d6Z���y�.��
�z�۾�7�ӱ*�/��L3GD��V�eE�6�#�?��5"X��0��屦�
о/	�ێ���F;��\�u��9;��m�m�QI�K\|k^���+�x�FXl�;�R-~tv�6_��������c6��g����>����0��%�S�'���<��C��~��)�2.C|mFO�s],�4\,6�xlFb�.�2�o����xR������&M��ٔM�
���.	�y��n\fk��N��.0�d��F�4���Hۄh�J��2��6 2-_��k�:�bo��t��&M�Co�hČ���o��C�0K![��"S�e���F�]�o��9gQ=J�Fs`��`02��︣���J�k3E���^�o���?��4N��.�[3ET��ټi":J�g�3��pV:+|	����lQb�L~ڴ6ǁ�)��Ϟ��t�I~� �؀�G,֏}K�+���s�F~� `  ��/g�8d띢ظ��6�]�#sP�!�~#'m�m��}{��>����iy�L3�^�0��q����q���7E׶}���\�iv���llf��]��͸�0ұٹYO������UL��V�6�W���o+V�1�h��Le�Yn;x�͸�r��?=�����(a?�(rɗ��fܰE���R�}-�-��F��mV��'��t�P��:�,�%�m�@ۙ®x��!�6���1�6�"ɛ��wC�.Hm�ZR��=�6�u��s,t4���4���:ɘ6Z����t���@�B���̄ڄ�X��H\�]��o��c���#c]�>m��C�K&#g��/U�C��1��?~����S*B      &   �  x��W��%;�{��(?$K��RELb�V	�27���靜�s��mI�<ckl&�t��F����un2��Q,&��E<����'�%^3;O/�ʥSr/�:'-�Ax;[]�T�s��n��t	�I��h�ڳ�������_O+��4��w�[)�/���������D�C5��=|�am����a�*��̵O#�e�.4e8��m�^\�=��>p��x�~صv2���1�^?�`�o�O[�GQ���KS�iIc��ls{Y�p�CiJaZ��l�j[խ6��k�
�y8)��r�4�޼�-��eg�L�L#���d%
--CF_��Kٌ�{*\+����3e��c�KN�"x�mV��ڏ���ZD��/+h�j$J�)��Nǝ��b����*����>ы,y��v��t��؉� K�h�Ƅ�������JAe9�<:��J�S��v�zW����BI�����f;ف$.O�_��@?���8Q�m��`f�/+�! �m���L� s�io�w��p�V� u<ǧЋX���>������ʥ;�Glʲ�b����7�ZT?9�\�B �R�pWw0#1��*X@�0�dꂗt��r���)R�Q�f�G�.Y �ڠZ�5yg�����O��9 ���]�|2E�E�j��K� k�
0�Aո�0��Y�yR9 ����@ۡ%�P.��ufV��L��kIm�_��l�.�
��*U�e�Okv8ֈ.k�	&�G�yL��fô��zt���
~�A�u"�zϼ�<��5�1F�*;�_z2�xΜ�xļ�H��݋�َ�gI�5I7~@M��@��D�!��e�}�l�g�OI*3�",vd�� �2�ph:H��!H��Ɇ/<b��/��>��پ����}���3�6p�$mR��J����/g0�auy��fA��G ���F�[X8|�5�]M(�l�x�����N���-8��{H`:�l/g�)\��|G{���>IVב��ny���j (���WE�B9$�N�E?2����7`Q8*#hhSkH~�*��\� *�N��L��c�N���^��B�<��n@�bD=r޷4i��C�'E��@P��ҽaV^�uԅps#Ϲ>���t����ǻl��,`oG/���܈�9�o�oPdLu_C�L�NG[3h�P�Q����WD6�f���u\���Ɏ�n�k�_�
�d��H9."�e_����d�n�r}m0�(nH�D(��@b�B:����(ss�ٸ!Ln �HE�����]�+ȆP�r=�-���|W� �x*�� F���"�O�"������x.W��* E�iC�`��g~Y����|7֤�������J�i=s�����&���(f9:i�LF��zP`9�A�Z�j=P��x��/��wcB�A4�[ҥN��wrlqjh�E�|
���KGoO;q`00��R #�"�2�	�qk�K`!����zq���b��H�r�V^N@��'B�0��>q
���!{D}�KYeV���w�ME�������m�q��	��9�b�V����*Vǜ|V���vl$���T�� ���?_���P "��s'"q�t�rx�Z������E��A��&�z�,�Q��k��/��kw�]C�2����}_�	������ߧ���      '   �  x��XM�\�<��/�	���;N�Ͼ���'�߬k�m���'͎v8d7�h��f�3�16��F��!��]��[����Kid�
���0N�5�S��\?����˙��Tkry��07��l��U�r�U+_�U�^�c��X�?�+�Kú�g��|�E<=H�v�����������Ư3�2���:�g1��U[��g��m���$��O鋜W�?�,��[>�P���"$�K�H���p��9�#|,!^�[���?F�˱�<m���������'�棺h�Ɨp�]Y(U��G��m�Z{�r�'c{�ڬ[m]��e�+Vz���,�u�b�����W���4�,��V<����7@j����������/�+���k}zy� ka�v�#��@d �L&V��s��yz�v)��6y�F�&4WzRѽz]�f��!���O�������>J����ٚ�&��CG� 3C�����r��Lӂ
#?���m؉�\]b�ѷ}�?�����x�~�"�&蜉��jHj Z�6������Q��~&$��F4�ѿ҉۹��(��h���G��*� ���uo�d��H�mf�Z�����]J�M댳�����&��]�5��v�e�AR�Ԋ��4BX���z|���� .j�jlǽ���}������Ceq%ݣ@*�P�g�c��`;��47�.dh0m�N�m���귌�-�/�]��G�-��C9x���bb��={��itn0����c�t7+JD��T+���F��A^��Ea5Q���XI����6��Kڱ�>(ʼK���G�X�z�o-�d�.d-�U(���C�o}�Q�S�\�P;��#t�Tvt��~�\Ђ����$����+ꆽ�|rF����|~{�͡| )�{�~��!���z�B]Kk�g�kG�YW����/�(4_`3'1t`��l�>e�N��nJg�K�X8��2�U��`+���gAD�tj,�'+��N�/��/E�W���>����Q�ˍ;"; ��)ғ�
	�\��vE��v4C��ܝ<�}z����G�s�Pt F�A�Aa6��U��S���n���'z�)�Nƴ�N66�O��Zj�x���8P�=S��.�3F,��$����u���>��wx�N���C�)���26��֭d��%7Ā��Q�pU�4�����!
$�w�X�jy5�Za��T�����,���m����S���z�gg�È��gT���*������y��E�&�eejv�͟�!i�#�&e+MF߁��Ck {�r�ylRE� L�� �Q��:z�O)�D���EV���90��K4���!x�ch���tW`�gOY�X�p�t����I\_��J4�����1�Z�b������]5;i`��\f��|
88r��WM���v�_Ap@[��w�s����	�w;����qe��cc����|<�k��#      (      x������ � �      )      x������ � �      +   G  x���QK�0 �����\.iry,۔ɶʺ��^Ҥ��� *��ͺn����q�H�G��(���5�o(��ꍉy0����ҡ�X�n�O҂U!�ܑ#��%�>v��?��zV	AH���خ��}���cy(�ԥ�>�!-���g�{Z��&ZR���mϻ����ҍ��#)��f�񷵟ٝ��ٛ��f��p�-���	�s{1U�*GRz?K�R�(���7���'G����S����H�{��;�p+f�b���(��d�鬚�ҡ�ǢLoJYl�I��Ɔģ[M l�ҁ�u*\l8-�sC��pY��bqU�᷻&��&˲/��+      ,   �  x���K%7E��{!�0,!{�l,E�2J��P���7*=�\>�끉sLԽ��6���?�mW9�h���.`=v��vɦY=��}�����o�����Rq	Z��.�����0��Ϗ{5��pg�����	��5C���guzJ��c#��G��׉�^u�Qӈ��|��P���X&�g���K<�n.�:	�!�����N�k�,8����}�`Q-�9�Y��:?�-�*��^)��	��hGG�[�*�9��~��	ddB��q��V�gtmYFb׾����ŤT��G'y��n;B�y`������:}���]Ԧ�B+ܑa��p�'��f����d�@�ˋiͭ�S��]Q���h9���̦NU�r.g��#��K��X��]�B:�&��gu{,g�G��|+ ].�o<Ezo�s��v�^L���S|ᐕ������&m��A��w��^��̧ٛ�u��D6���.��<fqu2�|g~���%���Q9 U7��M�!�|5�L�A�_�p�p�[���0&��]���Җ#mc-�G�o�D�.[��)o��J��>��|A-�<i���/TO�u��%�=|G׻t!�-��n}�3k��>v�������}�_�~>�g�����}�#��3l(����t�"�UО��y�����{��4�s?���픇a��w��]���}�I>5���l^���7�g�ͩ�./���ye�6�f�ы�xm4�m���������.K�E      -      x������ � �      .      x������ � �      /      x������ � �      0   �   x�}�9�0@��>�/0ȳ{����xC� KA��� ���W�,��H�BRTȒcL��7�]�=�v�����}ߎn���6�I��:��Ɠ� _��gRs�"dJ)*��F�r�
Jd�b�v���*w      1      x������ � �      2   S   x��̱� �v1���wIcLHe�*+�8�k��>Œ)�A��:����u\��%f�%ʴ����?��>w=[��8��      3      x������ � �      4      x�3763I4H4517������ &z�      5   �   x�-�AN�0EדS��6-K�E	QĊ͏�F��	8v���(�7`�1d�������m���u�H�R��gψ���y)�a�t����	W��CV��	g��3����	���Л�	��pK{p�f��OYm���K7�iS�O>��ZjУ+����k�9�.h7�.�+/i�����c��&��^�6ˠ�0z��]��(E�&�C>9N�����H`�߯���-3[p      7   L   x�3�t.MJ�,�2�t*J,��2�9��s�s�29ӸL8]C������E%�
A���@��kqA�� �1z\\\ �S�      9   S  x����N�0��?����埳ڕ�"aé�"N�Ȣ^�e;ٖI���y�y�a`�+>֕�}۪���e b`_�^h�!�L+@��hD"V�Δ"���n�,`4a<���e}�eC$�eEU#���́%Of���e7������qC���e;��\���t��e�u��A���NV���U���D"�G�5U���|�:"��C��m�����F]u0:f�����c�f��]��\��1�1}��F6�,1,|�XSu��^�m��	ڂ��K>���)���/��C����Z�Q�g_�g�mau"'�i~v�$�ꪐS«�i�@��3      ;   ]   x�3��q�t��
uwt���M/�4202�50�54R00�#.#� W7� WWN� 'ϐ �*�9��C��}<�C8\�<�]�,G��c���� ]ta      =      x�3�4A.#N0�2�C�=... 4#p      ?   8   x�3���OŃ��\F�~�ə�y@�a�g`�e��W�Z�D���q��qqq �      A   �   x�����@E���*l 2�Z�@p�'C v�V��99�d�ͯ7����]��䤏��R7�v�1s�Hp/3i��&ʓ�6z��Yw���kZ��3t�I�,��ðg{�.L�#�4*��M!��6�| ���      C   G  x�uU�r�F<�|��Ņ} $�2D�N��C�J�ʗ�7^�F@��7��T>A?��e��ڵ.T�N�t��4l)���g0��O�`U��	R��ug�����<U���
���5�G�ɻ(Q���t�c����]a	?������>�Q`��qp�@q�r)V�K؄h���~�!�S�
���e���h�Mک�XCCхޙ��wfZ�$^%��FQ<A�LLT�x�~��i�F!��h�W�pm���
�zQ�4��f�BÞ�F���cHu�����,��8;��:������6�L'�Öp�h=4��m�i�`k�����^+5w1�yz�6%%P���bW��Oc��8�R(4�h����9Jq�
��_�s��p�R����(5��G��ae���d�<�Sߟ�(�g]S�͠)�KxG1�>c�bb�D��Vpٷ�+�L�6U�Aװ����v���FU|[��K���'�gZ�
T�Mk;^`�Us�)�����p��Q�2��"�1�`g�$�~��9Jyr+k-�x�5wQ�BU2�&��o=[٥D�
.�a'нɬ�-�M�� �1#���4�m	�$É���[��D1���B�z�7��G7�R2�R�����f��}J�ZΜ��c�D֨ճ��i9(<FÎ��<��a7>���b�T��wْ{�;-�N�1�?p^��g2M3"���׳5��)"�B��3���
���8�k8!�0�x�r���,`c�q�3X��}CF���)n�E��S$_���Ha����&d��K,5<NNt��r��y�e���d����\
i���]�5���)_�dV��e ���/��X��_#�Fr��      D   �  x����n�F�ϳO�'X��dIGEI`'�ݦ������\gI�����r(z+zӋ���R옭aؚ�P3���RN��Zuٵ����!��O�쯶��DW�h��c+M��ZP��M�?�ӌ�Q]#���Vw��"�����r���#Vҵ��R�"{%#�LV&/_@��A�X�s��I2�lJoŽ�&;��Z�2�Eu%�Zn4}q��Q�6��C���V��*���^�P8J��	�~�N�7�yZ�6"��G"/�j6��W��I� �k�ʍ�78��U2sv���9]H�
S��Lvwb�Z��̃R4�J��,�љ��W�sr-���(�a�J��$���Gc^�%��wD�JT�ƻ�HQ�Q� �3���Y����y-�T-��M&��p��#����9}P�=��[�����"�`��Q.�|���w��q��M+�^�Xd���]�)$�􊑰��xcyI��Ne���� S���@����� 
��X����$Y.
�Oq*�+��Ob�t��
�x��N����|�O��C��:o7e�:�Q��|D+i<��w�Z�n7R�� l�E�e�/��a��,��<�Km�T�^��w�z��5樰ju����L9�>g���ɺ�mv%{et#ѐ<����)l�N�����YR ���5U¶��nP{]v��[�d�5��=�s9%߄7}���%�TLYaKt�-.�|�6�z�P"8�)2��&-�Q�T��.f�Ŵ`E�ϙ�{ ��]�����\����s�gǨ,P�;)����0(̃� @�S�8}D'�IX%_�gG��sV�O�\�J�=sx���4��ϲ`��Z]W�3������c��=ϟ�Ӓ3Z�z-�&�B��Q}�t3�m.F�-���{���Yq�ŧQ�a��Z�۾�l���M��r�?p�Ϡ4G8�[�N̰�� �	LS�.VN��^3��Z�[���]�y�
���a�8��P_�K:S�]��z��G�Es^AI���~�t�sҽ�#g�~��QYN���������8G1genۯĜA>֍�$��[�9%N�۶�U<iƣ>ae� ���*$��������=�J��c�E�"th7Xf���z@�6?,�g���)RZ�:;f�As�<~�ƴU�[���r�ʙM�A��> >ϼx5�B�V����MYy�s�9/�.��	��"J&%�t*zQ;l����'��s��O�vJ��N4�� �x����r��{>�(Yi�v)��u[��?��3OF-/Y��w���fWF�]wN�ȱ����g����c���N��=�����b��Ô0E��x-WIc��"?a�<̝+	mv��{&�#��d7g��7�׺��o��e��
��J�
i����a{?(yJ��G��J�i��>\�lZb%J��nxM�u�6e	�,yj�`�DL�>q�>��$V��:�'���%��c��B�d      E   S   x�3�t-K�+�/V�/�K�N�g&�sp�a	gnfQ%������������&���̴���"NSN#0L������ ��      G   �   x�=�A
�0���)z�L��.J��t�B�����#J���^R�Ӝb^GxxkA��F�L}�r&p��Fb>��:,�qHZ؅Z8���;毮Pus��!��8汬��;����`�8.kٔ��m��4���O��n�g�1�Q>2X     