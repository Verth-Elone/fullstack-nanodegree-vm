/*
Project: Full Stack Web Development - Catalog
Author: Peter Majko
Date of creation: 14.12.2015
Language: PostgreSQL
Addition info:
	Package needed: postgresql-contrib-9.3
	Why?: citext extension
	On Ubuntu: sudo apt-get install postgresql-contrib-9.3
	However to CREATE EXTENSION, only SUPERUSER can do so.
	You can grant user "vagrant" SUPERUSER rights by:
		1. Need to be logged in as user "postgres"
		   One way to do that is to write "su - root"
		   and then "su - postgres"
		2. Then enter "psql"
		3. In PSQL console write: "ALTER ROLE vagrant SUPERUSER;"
		4. Login back as vagrant
*/
/*
-- use this to disconnect all users (in case that the DB is locked)
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'catalog'
  AND pid <> pg_backend_pid();
*/

-- IF db already existst, delete it
DROP DATABASE IF EXISTS catalog;
-- Create new "catalog" database
CREATE DATABASE catalog;
-- Connect to the database
\c catalog;


-- create citext (case insensitive) extension
CREATE EXTENSION IF NOT EXISTS citext;

-- user table
CREATE TABLE catalog_user (
	-- unique id, serialized
	id serial PRIMARY KEY,
	-- user name
	name text,
	-- user email, must be unique, but case insensitive
	email citext UNIQUE
);
\d catalog_user

-- category table
CREATE TABLE category (
	-- unique id, serialized
	id serial PRIMARY KEY,
	-- name of the category
	title text NOT NULL,
	-- which user has created the category
	created_by int REFERENCES catalog_user (id),
	-- when was the category created
	created_at timestamp DEFAULT now()
);
\d category

-- item table
CREATE TABLE item (
	-- unique id, serialized
	id serial PRIMARY KEY,
	-- name of the item
	title text NOT NULL,
	-- which user has created the category
	created_by int REFERENCES catalog_user (id),
	-- when was the category created
	created_at timestamp DEFAULT now(),
	-- item text
	description text,
	-- is this item being locked (edit or delete deny)
	locked boolean,
	-- item's image path
	image_path text
);
\d item

-- item_category table
-- this table provides option to put item to more than
-- one category (e.g. movie can be Action and also Fantasy)
CREATE TABLE item_category (
	-- item id
	item_id int REFERENCES item (id),
	-- category id
	category_id int REFERENCES category (id)
);
\d item_category


-- OPTIONAL FUTURE TO DO:

-- roles table
-- stores information about different access roles
/*

*/


-- HIERARCHY TABLES

/*
-- category_hierarchy
CREATE TABLE category_hierarchy (
	-- parent id
	parent_id int,
	child_id int,
	PRIMARY KEY (parent_id, child_id)
);
*/

-- HISTORY TABLES

/*
-- category_history table
-- not in use yet
CREATE TABLE category_history (
	-- unique id of history record, serialized
	id serial PRIMARY KEY,
	-- id of category this history record belongs to
	category_id int,
	-- name
	category_name text,
	-- which user has modified the category
	modified_by int REFERENCES catalog_user (id),
	-- when was the category modified
	modified_at timestamp DEFAULT now()
);
*/
