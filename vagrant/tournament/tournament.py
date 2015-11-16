#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

# Some GLOBAL variables

# name of the database
database = "tournament"

# names of the tables
table_tournament = "tournament"
table_match = "match"
table_player = "player"
table_match_player = "match_player"

# allow custom print statments?
# set value to True for detailed statements
allow_custom_print = False

# suppress Exception print-outs?
# set value to True for error print suppression
suppress_exception_po = False


# Functions

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection
    or False if the connection wasn't successful."""
    if allow_custom_print:
        print "-Connecting to database..."
    txt_conn = "--Connection to database '{db}' ".format(db=database)
    try:
        conn = psycopg2.connect("dbname={db}".format(db=database))
        if allow_custom_print:
            print txt_conn + "successful."
        return conn
    except Exception as err:
        if not suppress_exception_po:
            print txt_conn + "failed due to error:\n{err}".format(err=err)
        return False


def execute_sql(cursor, sql):
    """Execute sql command through supplied db cursor.
    Returns True if query was successful else False."""
    if allow_custom_print:
        print "-Executing query..."
    try:
        cursor.execute(sql)
        if allow_custom_print:
            print "--Query executed successfuly."
        return True
    except Exception as err:
        if not suppress_exception_po:
            print "--Query:\n" + sql +
            "\n--not executed due to the error:\n{err}.".format(err=err)
        return False


def commit_sql(connection):
    """Commit everything. Returns True if commit was successful else False."""
    if allow_custom_print:
        print "-Commiting changes..."
    try:
        connection.commit()
        if allow_custom_print:
            print "--Changes commited successfuly."
        return True
    except Exception as err:
        if not suppress_exception_po:
            print "--Not commited due to the error:\n{err}.".format(err=err)
        return False


def deleteMatches():
    """Remove all the match records from the database."""
    if allow_custom_print:
        print "\nDeleting matches..."
    conn = connect()
    if conn:
        c = conn.cursor()
        # delete all matches, return count of them
        sql = """WITH deleted AS (
                    DELETE FROM {m} RETURNING *
                )
             SELECT count(*)
             FROM deleted
          """.format(m=table_match)
        if execute_sql(c, sql):
            del_count = c.fetchone()[0]
            if commit_sql(conn):
                if allow_custom_print:
                    print "Deleted {c} records from table {m}".format(
                        c=del_count, m=table_match
                    )
        conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    if allow_custom_print:
        print "\nDeleting players..."
    conn = connect()
    if conn:
        c = conn.cursor()
        # delete all players, return count of them
        sql = """WITH deleted AS (
                    DELETE FROM {p} RETURNING *
                )
             SELECT count(*)
             FROM deleted
            """.format(p=table_player)
        if execute_sql(c, sql):
            del_count = c.fetchone()[0]
            if commit_sql(conn):
                if allow_custom_print:
                    print "Deleted {c} records from table {p}".format(
                        c=del_count, p=table_player
                    )
        conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    if allow_custom_print:
        print "\nCounting players..."
    conn = connect()
    if conn:
        c = conn.cursor()
        sql = """SELECT COUNT(ID) FROM {p}""".format(p=table_player)
        if execute_sql(c, sql):
            player_count = c.fetchone()[0]
            conn.close()
            if allow_custom_print:
                print "Player count: {c}".format(c=player_count)
            return player_count


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    if allow_custom_print:
        print "\nRegistering a player..."
    conn = connect()
    if conn:
        c = conn.cursor()
        sql = """INSERT INTO {p} (name) VALUES
                 ('{name}');""".format(p=table_player, name=name)
        if execute_sql(c, sql):
            if commit_sql(conn):
                if allow_custom_print:
                    print "Player {n} registered.".format(n=name)
        conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    if allow_custom_print:
        print "\nGetting player standings..."
    conn = connect()
    if conn:
        player_standings = []
        c = conn.cursor()
        tid = tournament_id
        sql = """WITH p_wins AS (
                    SELECT {p}.id AS pid, {t}.id AS tid,
                        COUNT({m}.id) AS wcount
                    FROM {p}
                    LEFT OUTER JOIN {m} ON {p}.id = {m}.winner_id
                    INNER JOIN {t} ON {m}.tournament_id = {t}.id
                    GROUP BY pid, tid
                ), p_matches AS (
                    SELECT {p}.id AS pid, {t}.id AS tid,
                        COUNT({m}.id) AS mcount
                    FROM {p}
                    LEFT OUTER JOIN {mp} ON {p}.id = {mp}.player_id
                    RIGHT OUTER JOIN {m} ON {mp}.match_id = {m}.id
                    INNER JOIN {t} ON {m}.tournament_id = {t}.id
                    GROUP BY pid, tid
                )
            SELECT {p}.id AS id, {p}.name AS name,
                p_wins.wcount AS wins,
                p_matches.mcount AS matches
            FROM p_wins
            INNER JOIN p_matches ON p_wins.pid = p_matches.pid
                AND p_wins.tid = p_matches.tid
            INNER JOIN {p} ON p_wins.id = {p}.id
            WHERE p_matches.tid = {tid}
            """.format(
                t=table_tournament, m=table_match,
                mp=table_match_player, p=table_player, tid=tid
            )
        if execute_sql(c, sql):
            for row in c.fetchall():
                player_standings.append(row)
            if allow_custom_print:
                print "Player {n} registered.".format(n=name)
        conn.close()
        return player_standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    if allow_custom_print:
        print "\nStoring match outcame to DB..."
    conn = connect()
    if conn:
        c = conn.cursor()
        tid = tournament_id
        sql = """WITH new_match AS (
                    INSERT INTO {m} (tournament_id, winner_id)
                        VALUES ({tid}, {winner})
                        RETURNING id
                )
            SELECT id
            FROM new_match;
            """.format(m=table_match)
        if execute_sql(c, sql):
            if commit_sql(conn):
                if allow_custom_print:
                    print "Match record for winner: {w} / loser: {l}" +
                    "successfuly stored.".format(w=winner, l=loser)
        conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """


def create_tournament():
    """Crates a new tournament"""
    if allow_custom_print:
        print "\nFetching player standings..."
    tournament_id = 0
    conn = connect()
    if conn:
        c = conn.cursor()
        # Insert new default row and return the id of it
        sql = """WITH created AS (
                 INSERT INTO {t} DEFAULT VALUES RETURNING id)
             SELECT id
             FROM created;
          """.format(t=table_tournament)
        if execute_sql(c, sql):
            if commit_sql(conn):
                tournament_id = c.fetchone()[0]
                if allow_custom_print:
                    print "Tournament #{tid} created.".format(
                        tid=tournament_id
                    )
        conn.close()
    return tournament_id


def get_latest_tournament():
    """Returns the latest tournament id."""
    if allow_custom_print:
        print "\nFetching player standings..."
    conn = connect()
    if conn:
        c = conn.cursor()
        sql = """SELECT max(id) FROM {t};""".format(t=table_tournament)
        if execute_sql(c, sql):
            latest_tournament_id = c.fetchone()[0]
            if allow_custom_print:
                print "Latest tournament #: {tid}.".format(
                    tid=latest_tournament_id
                )
        conn.close()


def main():
    tournament_id = create_tournament()
    print "Torunament id:", tournament_id


# MAIN
main()
