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
table_tournament_player = "tournament_player"

# allow custom print statments?
# set value to True for detailed statements
allow_custom_print = True

# suppress Exception print-outs?
# set value to True for error print suppression
suppress_exception_po = False

points_for_win = 3
points_for_tie = 1
points_for_loss = 0

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


def execute_sql(cursor, sql, vars=[], many=False):
    """Execute sql command through supplied db cursor.
    Returns True if query was successful else False.

    Args:
        cursor: cursor from the connection
        sql: sql string with placeholders (to prevent SQL injection)
        vars ([]): variables for placeholders (can be tuple, list or dict)
        many (False): True for executemany, False for execute
    """
    if allow_custom_print:
        print "-Executing query..."
    try:
        if many:
            cursor.executemany(sql, vars)
        else:
            cursor.execute(sql, vars)
        if allow_custom_print:
            print "--Query executed successfuly."
        return True
    except Exception as err:
        if not suppress_exception_po:
            print "--Query:\n" + sql + \
                "\n--not executed due to the error:\n{err}.".format(err=err)
        return False


def commit_sql(connection):
    """Commit everything. Returns True if commit was successful else False.

    Args:
        connection: db connection object
    """
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
        pid = 0
        sql = """INSERT INTO {p} (name)
            VALUES (%(name)s)
            RETURNING {p}.id;
            """.format(p=table_player)
        vars = {"name": name}
        if execute_sql(c, sql, vars):
            if commit_sql(conn):
                pid = c.fetchone()[0]
                if allow_custom_print:
                    print "Player {n} registered.".format(n=name)
        conn.close()
        return pid


def playerStandings(tournament_id=None):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Args:
        tournament_id (None): id of the tournament for player standings

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
        sql = """WITH p_wins AS (
                    SELECT {p}.id AS pid, {t}.id AS tid,
                        COUNT({m}.id) AS wcount
                    FROM {p}
                    LEFT OUTER JOIN {m} ON {p}.id = {m}.winner_id
                    LEFT OUTER JOIN {t} ON {m}.tournament_id = {t}.id
                    GROUP BY pid, tid
                ), p_matches AS (
                    SELECT {p}.id AS pid, {t}.id AS tid,
                        COUNT({m}.id) AS mcount
                    FROM {p}
                    LEFT OUTER JOIN {mp} ON {p}.id = {mp}.player_id
                    LEFT OUTER JOIN {m} ON {mp}.match_id = {m}.id
                    LEFT OUTER JOIN {t} ON {m}.tournament_id = {t}.id
                    GROUP BY pid, tid
                )
            SELECT {p}.id AS id, {p}.name AS name,
                p_wins.wcount AS wins,
                p_matches.mcount AS matches
            FROM p_wins
            INNER JOIN p_matches ON p_wins.pid = p_matches.pid
                AND (p_wins.tid = p_matches.tid
                    OR (p_wins.tid IS NULL AND p_matches.tid IS NULL))
            INNER JOIN {p} ON p_wins.pid = {p}.id
            WHERE p_matches.tid IS %(tid)s;
            """.format(
                t=table_tournament, m=table_match,
                mp=table_match_player, p=table_player
            )
        vars = {"tid": tournament_id}
        if execute_sql(c, sql, vars):
            for row in c.fetchall():
                player_standings.append(row)
            if allow_custom_print:
                print "Player standings: {ps}".format(ps=player_standings)
        conn.close()
        return player_standings


def reportMatch(players, tournament_id=None, winner=None, ):
    """Records the outcome of a single match between two players.

    As my vision of this function is to allow any number of players to
    enter a match, but only one can be a winner or there is a tie,
    I have altered the winner/looser to tuple/list of players
    and passing the winner as index of this tuple/list.

    This would be useful for FFA (free for all) matches in multiplayer
    games of more than 2 players in a match.

    Tournament id was added as argument to link a match with some tournament,
    however it is still possible to record a match outside any tournament.

    The point in this is to use the same function with practice
    and tournament matches.

    Args:
      players:  tuple/list of players' IDs who played the match
      winner (None): None for TIE, otherwise valid tuple index of winner
      tournament_id (None): id of the tournament
    """
    sql_1 = """INSERT INTO {m} (tournament_id, winner_id)
            VALUES (%(tid)s, %(winner_id)s)
            RETURNING id AS mid
            """.format(m=table_match)
    sql_2 = """INSERT INTO {mp} (match_id, player_id)
            SELECT %s AS mid, %s AS pid;
            """.format(mp=table_match_player)
    sql_3 = """UPDATE {tp} SET points = points + %(points)s
            WHERE tournament_id = %(tid)s
            AND player_id = %(pid)s;
            """.format(tp=table_tournament_player)
    if allow_custom_print:
        print "\nStoring match outcame to DB..."
    conn = connect()
    if conn:
        c = conn.cursor()
        tid = tournament_id
        if winner is not None:
            winner_id = players[winner]
        else:
            winner_id = None
        vars_1 = {"tid": tournament_id, "winner_id": winner_id}
        if execute_sql(c, sql_1, vars_1):
            match_id = c.fetchone()[0]
            # prepare list [(newMatchId, player1_id), (newMatchId, player1_id)]
            vars_2 = []
            vars_3 = []
            for player_id in players:
                vars_2.append((match_id, player_id))
            if commit_sql(conn):
                if allow_custom_print:
                    print """Match record #{nmid} successfuly stored.
                        """.format(nmid=match_id)
                if execute_sql(c, sql_2, vars_2, True):
                    if commit_sql(conn):
                        if allow_custom_print:
                            print """{rc} player/match records stored successfully.
                                """.format(rc=len(players))
                        # if the match is being recorded for a tournament
                        # it is needed to store the points acquired
                        if tournament_id is not None:
                            all_ptr = []
                            for player_id in players:
                                ptr = {}
                                ptr["tid"] = tournament_id
                                ptr["pid"] = player_id
                                if winner is not None:
                                    if player_id == winner_id:
                                        ptr["points"] = points_for_win
                                    else:
                                        ptr["points"] = points_for_loss
                                else:
                                    ptr["points"] = points_for_tie
                                all_ptr.append(ptr)
                            if execute_sql(c, sql_3, all_ptr, True):
                                if commit_sql(conn):
                                    print """All player points updated."""
        conn.close()


def swissPairings(tournament_id):
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Args:
        tournament_id: id of the tournament

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    if allow_custom_print:
        print "\nPairing players for next round..."
    conn = connect()
    if conn:
        next_round_pairs = []
        c = conn.cursor()
        tid = tournament_id
        sql = """WITH even AS (
                SELECT ROW_NUMBER() OVER () AS rowid2, *
                FROM ordered_tournament_standings
                WHERE tid = %(tid)s
                AND rowid %% 2 = 0
            ), odd AS (
                SELECT ROW_NUMBER() OVER () AS rowid2, *
                FROM ordered_tournament_standings
                WHERE tid = %(tid)s
                AND rowid %% 2 = 1
            )
            SELECT even.player_id, even.player_name,
                odd.player_id, odd.player_name
            FROM even
            INNER JOIN odd ON odd.rowid2 = even.rowid2;
            """.format(tp=table_tournament_player, p=table_player)
        vars = {"tid": tournament_id}
        if execute_sql(c, sql, vars):
            if commit_sql(conn):
                for i, row in enumerate(c.fetchall()):
                    next_round_pairs.append(row)
                if allow_custom_print:
                    print """Player pairings for next round:\n{pp}""".format(
                        pp=next_round_pairs
                    )
        conn.close()
    return next_round_pairs


def create_tournament():
    """Creates a new tournament"""
    sql = """WITH created AS (
                    INSERT INTO {t} DEFAULT VALUES RETURNING id
            )
         SELECT id
         FROM created;
      """.format(t=table_tournament)
    if allow_custom_print:
        print "\nFetching player standings..."
    tournament_id = 0
    conn = connect()
    if conn:
        c = conn.cursor()
        # Insert new default row and return the id of it
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
    sql = """SELECT max(id) FROM {t};""".format(t=table_tournament)
    if allow_custom_print:
        print "\nFetching player standings..."
    conn = connect()
    if conn:
        c = conn.cursor()
        vars = {}
        if execute_sql(c, sql, vars):
            latest_tournament_id = c.fetchone()[0]
            if allow_custom_print:
                print "Latest tournament #: {tid}.".format(
                    tid=latest_tournament_id
                )
        conn.close()
        return latest_tournament_id


def register_player_for_tournament(pid, tid):
    """Registers the player for tournament.

    Args:
        pid: player id
        tid: tournament id
    """
    sql = """INSERT INTO {tp} (tournament_id, player_id)
        VALUES (%(tid)s, %(pid)s);
        """.format(tp=table_tournament_player)
    if allow_custom_print:
        print """\nRegistering player #{pid} for tournament #{tid}...
            """.format(pid=pid, tid=tid)
    conn = connect()
    if conn:
        c = conn.cursor()
        vars = {"tid": tid, "pid": pid}
        if execute_sql(c, sql, vars):
            if commit_sql(conn):
                if allow_custom_print:
                    print "Player successfuly registered for tournament."
        conn.close()
