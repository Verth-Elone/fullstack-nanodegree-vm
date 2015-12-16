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
	('i1', 'Some desc', 'Some path', 1),
	('i2', 'Other desc', 'Other path', 2)
;