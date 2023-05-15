ALTER TABLE IF EXISTS enterprise.users
    ADD COLUMN receive_notifications boolean DEFAULT False;

INSERT INTO resources.event_roles(name, description, created_by, created_date)
		VALUES ('PLAYER', 'JUGADOR', 'miry', '2023-05-12 00:00:00');
	INSERT INTO resources.event_roles(name, description, created_by, created_date)
		VALUES ('REFEREE', 'ARBITRO', 'miry', '2023-05-12 00:00:00');
	INSERT INTO resources.event_roles(name, description, created_by, created_date)
		VALUES ('JOURNALIST', 'PERIODISTA', 'miry', '2023-05-12 00:00:00');