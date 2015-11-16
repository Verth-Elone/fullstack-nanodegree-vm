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
\c tournament;

-- Create table for storing game information
CREATE TABLE tournament(
	id serial primary key,
	winner int,
	created timestamp DEFAULT now()
	);

\d tournament

-- Create table for storing match information
CREATE TABLE match(
	id serial primary key,
	tournament_id int references tournament (id),
	winner int,
	created timestamp DEFAULT now()
	);

\d match

-- Create table for storing player information
CREATE TABLE player(
	id SERIAL primary key,
	name text,
	registered timestamp DEFAULT now()
	);

\d player

-- Create table for match-player unique combinations
CREATE TABLE match_player(
	match_id int references match (id),
	player_id int references player (id),
	entered timestamp DEFAULT now(),
	primary key (match_id, player_id)
	);

\d match_player
