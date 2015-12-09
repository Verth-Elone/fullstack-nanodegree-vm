-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- IF db already existst, delete it
DROP DATABASE IF EXISTS tournament;
-- Create new "tournament" database and connect to it
CREATE DATABASE tournament;
-- Connect to the database
\c tournament;

-- Create table for storing tournament information
-- winner_id is not referenced to player(id),
-- due to possibility of removing winning player,
-- but keeping tournament records
CREATE TABLE tournament(
	id serial primary key,
	created timestamp DEFAULT now()
	);
-- show the created table structure
\d tournament

-- Create table for storing match information.
-- Tournament_id is not referenced to tournament(id),
-- as it should be possible to play match outside tournament.
-- Winner_id is not referenced to player(id),
-- due to TIE (Null) and possibility of removing winning player,
-- but keeping match records.
CREATE TABLE match(
	id serial primary key,
	tournament_id int,
	-- tournament_id int references tournament (id) ON DELETE CASCADE,
	winner_id int,
	created timestamp DEFAULT now()
	);
-- show the created table structure
\d match

-- Create table for storing player information
CREATE TABLE player(
	id SERIAL primary key,
	name text,
	registered timestamp DEFAULT now(),
	rank int DEFAULT 0
	);
-- show the created table structure
\d player

-- Create table for match-player unique combinations
-- Deletion of matches and players
-- is allowed through ON DELETE CASCADE
CREATE TABLE match_player(
	match_id int references match (id) ON DELETE CASCADE,
	player_id int references player (id) ON DELETE CASCADE,
	is_bye_match boolean DEFAULT FALSE,
	entered timestamp DEFAULT now(),
	primary key (match_id, player_id)
	);
-- show the created table structure
\d match_player

-- Create table for tournament-player unique combinations.
-- Deletion of tournaments and players
-- is allowed through ON DELETE CASCADE.
-- TO DO: this shouldn't be possible for player deletion.
-- If player is deleted, the reference should point to "dummy" player,
-- but results should persist (same with match_player table)
CREATE TABLE tournament_player(
	tournament_id int references tournament (id) ON DELETE CASCADE,
	player_id int references player (id) ON DELETE CASCADE,
	entered timestamp DEFAULT now(),
	points int DEFAULT 0,
	primary key (tournament_id, player_id)
	);
-- show the created table structure
\d tournament_player

-- Create view for ordered tournament standings
CREATE VIEW ordered_tournament_standings AS (
	SELECT ROW_NUMBER() OVER (ORDER BY tp.points DESC,p.id ASC) AS rowid,
    tp.tournament_id AS tid, p.id AS player_id, p.name AS player_name, tp.points
    FROM tournament_player AS tp
    INNER JOIN player AS p ON tp.player_id = p.id
);
\d ordered_tournament_standings

CREATE VIEW full_match_info AS (
	SELECT mp.player_id AS pid, m.tournament_id AS tid,
		m.id AS mid, m.winner_id AS wid
	FROM match AS m
	INNER JOIN match_player AS mp ON m.id = mp.match_id
);
\d full_match_info

-- this view will contain all players who haven't played
-- any match yet AND those which played non-tournament matches
CREATE VIEW partial_non_tournament_match_info AS (
	SELECT p.id AS pid, tid, mid, wid
	FROM player AS p
	LEFT JOIN full_match_info AS fmi ON p.id = fmi.pid
	WHERE fmi.tid IS NULL
);
\d partial_non_tournament_match_info

-- this view will contain all players
CREATE VIEW full_non_tournament_match_info AS (
	SELECT p.id AS pid, pntmi.tid AS tid, pntmi.mid AS mid,
		CASE WHEN pid = pntmi.wid THEN 1
			ELSE Null
		END
		AS wid
	FROM player AS p
	LEFT JOIN partial_non_tournament_match_info AS pntmi
		ON p.id = pntmi.pid
);
\d full_non_tournament_match_info

CREATE VIEW full_non_tournament_standings AS (
	SELECT pid, tid, COUNT(mid) AS mplayed, COUNT(wid) AS mwon
	FROM full_non_tournament_match_info
	GROUP BY pid, tid
);
\d full_non_tournament_standings

CREATE VIEW full_tournament_match_info AS (
	SELECT tp.tournament_id AS tid, tp.player_id AS pid, fmi.mid, fmi.wid
	FROM tournament_player AS tp
	LEFT JOIN full_match_info AS fmi ON tp.player_id = fmi.pid
);
\d full_tournament_match_info

CREATE VIEW full_tournament_standings AS (
	SELECT pid, tid, COUNT(mid) AS mplayed, COUNT(wid) AS mwon
	FROM full_tournament_match_info AS ftmi
	GROUP BY pid, tid
);
\d full_tournament_standings

CREATE VIEW full_standings AS (
	SELECT *
	FROM full_non_tournament_standings
	UNION
	SELECT *
	FROM full_tournament_standings
);
\d full_standings

CREATE VIEW full_standings_with_names AS (
	SELECT p.id AS pid, p.name AS pname,
		fs.mplayed AS mplayed, fs.mwon AS mwon, fs.tid AS tid
	FROM full_standings AS fs
	INNER JOIN player AS p ON fs.pid = p.id
);
\d full_standings_with_names