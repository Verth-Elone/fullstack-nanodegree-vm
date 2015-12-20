rdb-fullstack
=============

This repo holds vagrant/vm projects for Udacity's Full Stack Web Development nanodegree projects.

Installation:
-------------

1. Get VirtualBox from Oracle, install it (no need to launch or do anything else).
2. Get Vagrant, install it.
3. Clone/download this repo.
4. Using terminal/command line, navigate to "(your path)\fullstack-nanodegree-vm\vagrant" subdirectory
5. Use command "vagrant up".
6. If everything went well, you can now use command "vagrant ssh" to access terminal console of the project system installation. Please note that this will be not possible without SSH client installed on the host machine. Cygwin, MinGW or Git come with this client.
7. Typing "..\\..\vagrant" will move you to the right directory, from which you can select project.

Projects:
---------

#### Tournament
__________
Description: Swiss style tournament postgreSQL database, with Python functions operating on it.

Database installation: 

1.  Navigate to subdirectory "tournament"

2.  Run command "psql" to enter postgreSQL console

3.  Run "\i tournament.sql", which will create database "tournament" with all required tables and views

4.  Run command "\q" to leave psql environment

Testing:
To test out, you simply run command "python tournament_test.py" from "tournament" subdirectory.

Refer to comments in code of "tournament.py" for further description of all functions.

#### Catalog
__________
Description: Catalog web app with working database, login/logout through Google and Facebook, CSRF protection

Database installation: 

1.  Navigate to subdirectory "catalog"

2.  Run command "psql" to enter postgreSQL console

3.  Run "CREATE DATABASE catalogwithusers;" command

4.  Run command "\q" to leave psql environment

5.  Run command "python database_setup.py"

... need to add more ...
