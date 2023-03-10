# Bidding utility for helping in quick asynchronous bidding for
# arbitrary N player games (with Gaia Project as a motivator)

# == Program Inputs:
# 1. "Factions" (names of 'seats' players are bidding for)
# 2. "Reserve prices" for each player, decided by each player
# privately and submitted simultaneously into this program. Players
# can either use honor system to privately "lock in" their reserve prices
# before sharing them, or use a trusted broker to manage everyone's reserve
# prices and use them in this program.

# == Explanation / example of "reserve price":
# If a player has [0, 5, 10, 15] as their reserve prices
# for ["Hads", "Terran", "Nevlas", "Geodens"], this means
# that they would value Geodens as the best seat; they would, for example,
# prefer Geodens over Nevlas unless Geodens cost 5 more points to play than Nevlas.
# They would thus treat all the following choices as equal: Hads at 0, Terran at -5,
# Nevlas at -10, and Geodens at -15.
# Note that these preferences are important for pairwise comparisons.
# Such a player, if presented with Geodens at 6 and everything else at 0,
# would *not* prefer Geodens (despite Geodens being '15'), but would actually
# prefer Nevlas -- Geodens are only 5 better than Nevlas.

# Results:
# Instructions for the seat assignment and handicap for each player.
# The results are that no player is forced into an option that is worse
# than their reserve prices.

# The factions present in the game, in turn order.
FACTIONS = ["Lantids", "Hads", "Geodens", "Nevlas"]

# "Reserve prices" for each player. Players are keys,
# and players should be enumerated in their turn order.
PLAYERS = {
  "Chris" : [0, 17, 16, 15],
  "Rob" : [5, 19, 0, 35],
  "Wendy" : [1, 0, 20, 15],
  "Nate" : [0, 8, 5, 7],
}

def validate_inputs(factions, players):
  if len(factions) != len(players):
    raise Exception("Number of factions must equal number of players, but %s != %s" % (len(factions), len(players)))
  for k in players:
    if len(factions) != len(players[k]):
      raise Exception("Each player must list %s factions, but %s did not" % (len(factions), k))
    contains_zero = False
    for bid in players[k]:
      if bid < 0:
        raise Exception("Illegal bid for %s, bids must not be negative" % k)
      if bid == 0:
        contains_zero = True
    if not contains_zero:
      raise Exception("Illegal bids for %s, one bid must be zero" % k)
  pass

# If it's player_index's turn to bid, with reserve as their
# reserve and current_bids are the current bids, this returns
# (faction_index, bid_score) where that is the "best bid"
# for that player.
def best_bid(player_index, current_bids, reserve):
  # util_val for i is the assessed value of faction i
  # high falues are more appealing; bid on the faction
  # with highest value.
  # Note that best util should always be non-negative, or
  # something went wrong.
  best_util = -1
  best_bid = -1
  best_choice = -1
  for i in range(0, len(reserve)):
    potential_bid = 0
    if current_bids[i] is not None:
      (_, last_bid) = current_bids[i]
      potential_bid = last_bid + 1
    util_val = reserve[i] - potential_bid
    if util_val > best_util or (util_val == best_util and potential_bid > best_bid):
      best_util = util_val
      best_bid = potential_bid
      best_choice = i
  if best_util < 0:
    raise Exception("Something went horribly wrong")
  return (best_choice, best_bid)


def bidding_algorithm(factions, players):
  # current_bid[i] consists of (player_index, bid_score) where player_index was the last person
  # to bid bid_score for that faction, or None if no player has yet bid on that faction.
  current_bids = [None] * len(players)

  # FIFO queue of players who need to bid. players_to_go[0] is front of queue.
  players_to_go = []
  players_to_go.extend(players.keys())
  
  while len(players_to_go) > 0:
    (player_index, players_to_go) = (players_to_go[0], players_to_go[1:])
    (faction_index, bid_score) = best_bid(player_index, current_bids, players[player_index])
    print("%s bids %s on %s" % (player_index, bid_score, factions[faction_index]))
    if current_bids[faction_index] == None:
      current_bids[faction_index] = (player_index, bid_score)
    else:
      (prev_player, prev_bid) = current_bids[faction_index]
      if bid_score <= prev_bid:
        raise Exception("Illegal bid")
      current_bids[faction_index] = (player_index, bid_score)
      players_to_go.append(prev_player)
  return current_bids



def main(factions, players):
  validate_inputs(factions, players)
  final_result = bidding_algorithm(factions, players)
  print("--------")
  player_orders = {}
  for i in range(0, len(factions)):
    (player, bid) = final_result[i]
    player_orders[player] = (factions[i], bid)
  for player in players.keys():
    (faction, bid) = player_orders[player]
    print("Player %s will be %s at bid %s" % (player, faction, bid))

main(FACTIONS, PLAYERS)

