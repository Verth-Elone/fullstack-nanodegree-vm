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
	winner_id int,
	created timestamp DEFAULT now()
	);
-- show the created table structure
\d tournament

-- Create table for storing match information
-- Deletion of matches
-- is allowed through ON DELETE CASCADE
-- winner_id is not referenced to player(id),
-- due to possibility of removing winning player,
-- but keeping match records
CREATE TABLE match(
	id serial primary key,
	tournament_id int references tournament (id) ON DELETE CASCADE,
	winner_id int,
	created timestamp DEFAULT now()
	);
-- show the created table structure
\d match

-- Create table for storing player information
CREATE TABLE player(
	id SERIAL primary key,
	name text,
	registered timestamp DEFAULT now()
	);
-- show the created table structure
\d player

-- Create table for match-player unique combinations
-- Deletion of matches and players
-- is allowed through ON DELETE CASCADE
CREATE TABLE match_player(
	match_id int references match (id) ON DELETE CASCADE,
	player_id int references player (id) ON DELETE CASCADE,
	entered timestamp DEFAULT now(),
	primary key (match_id, player_id)
	);
-- show the created table structure
\d match_player
