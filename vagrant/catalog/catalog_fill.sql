/*
Project: Full Stack Web Development - Catalog
Author: Peter Majko
Date of creation: 14.12.2015
Language: PostgreSQL

Purpose: Fill out the database with test data
*/

\c catalog
INSERT INTO category (name)
VALUES ('c1'), ('c2');

INSERT INTO item (name, description, image, category_id)
VALUES
	('i1', 'Some desc i1', 'Some path i1', 1),
	('i2', 'Some desc i2', 'Some path i2', 1),
	('i3', 'Some desc i3', 'Some path i3', 2),
	('i4', 'Some desc i4', 'Some path i4', 2)
;