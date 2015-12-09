#!/usr/bin/env python
#
# Test cases for tournament.py
# Altered by Peter Majko, to reflect some additional functionality

from tournament import *


def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    # EDIT START
    # edited due to changes to reportMatch arguments
    # players are passed as tuple/list
    # 2nd argument is tournament id for which we want to get next round matchings
    # More info in the reportMatch function doc string
    # winner is passed as index of this tuple/list
    # If there is no winner, use False (or nothing for default False)
    reportMatch((id1, id2), None, 0)
    reportMatch([id3, id4], None, 0)
    # EDIT END
    standings = playerStandings()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings(tid):
    deleteMatches()
    deletePlayers()

    # EDIT START
    # as we got the ids from standings[i][0] we do not need to store
    # return value of registerPlayer()
    # EDIT END

    pA = registerPlayer("Twilight Sparkle")
    pB = registerPlayer("Fluttershy")
    pC = registerPlayer("Applejack")
    pD = registerPlayer("Pinkie Pie")

    # ADD START
    # now we need to register players for the tournament
    register_player_for_tournament(pA, tid)
    register_player_for_tournament(pB, tid)
    register_player_for_tournament(pC, tid)
    register_player_for_tournament(pD, tid)
    # ADD END

    # EDIT START
    # As we can have more tournaments now, we need get standings
    # only for this tournament! So passing tid to playerStandings
    standings = playerStandings(tid)
    # EDIT END

    [id1, id2, id3, id4] = [row[0] for row in standings]

    # EDIT START
    # edited due to changes to reportMatch arguments
    # players are passed as tuple/list
    # 2nd argument is tournament id for which we want to get next round matchings
    # More info in the reportMatch function doc string
    # winner is passed as index of this tuple/list
    # If there is no winner, use False (or nothing for default False)
    reportMatch((id1, id2), tid, 0)
    reportMatch([id3, id4], tid, 0)
    # EDIT END

    pairings = swissPairings(tid)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."

def testPairings2(tid):
    """Testing pairings for another tournament,
    without player and match deletion,
    where there is odd number of players added
    and one match uses tie (draw):
    1st round:
        A plays B = tie
        C plays D = C wins
        E gets bye
    2nd round:
        A plays B
        C plays E
        D gets bye

    Yet to implement: after bye, store it in database, player can't get more bye
    after that - this should be coming from VIEW ordered_tournament_standings,
    but maybe not - need to think more about that

    Another thing is that players shouldn't play more than one game with the same
    oponent - need to think more about that
    """

    pA = registerPlayer("A")
    pB = registerPlayer("B")
    pC = registerPlayer("C")
    pD = registerPlayer("D")
    pE = registerPlayer("E")

    register_player_for_tournament(pA, tid)
    register_player_for_tournament(pB, tid)
    register_player_for_tournament(pC, tid)
    register_player_for_tournament(pD, tid)
    register_player_for_tournament(pE, tid)

    standings = playerStandings(tid)
    [id1, id2, id3, id4, id5] = [row[0] for row in standings]

    reportMatch((id1, id2), tid, None)
    reportMatch([id3, id4], tid, 0)
    reportMatch((id5,), tid, 0)

    pairings = swissPairings(tid)
    if len(pairings) != 3:
        raise ValueError(
            "For five players, swissPairings should return three pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), \
     (pid5, pname5, pid6, pname6)] = pairings
    correct_pairs = set([frozenset([id1, id2]), frozenset([id3, id5]), frozenset([id4, None])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4]), frozenset([pid5, pid6])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After second match, players with one win should be paired.")
    print "9. After second match, players with one win are paired."


# new function added to implement tournament creation
def test_tournament():
    tid = create_tournament()
    if tid != 0:
        print "-- Tournament #{tid} successfully created.".format(tid=tid)
    else:
        print "-- No tournament was created due to an unexpected error."
    return tid

if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    # for pairings new tournament has to be created
    # as matches played outside tournament are considered as training
    tid = test_tournament()
    # testPairings had to be altered by passing tournament id argument
    testPairings(tid)
    tid2 = test_tournament()
    testPairings2(tid2)
    print "Success!  All tests pass!"
