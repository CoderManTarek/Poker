import time
from abc import abstractmethod
from PokerTools.player import Player
from PokerTools.deck import Deck
from PokerTools.hand import Hand

class Table:
  cap = 10000
  def __init__(self, deck, total_seats,players = None, button_seat_number = 1):
    self.total_seats = total_seats
    self.button_seat_number = button_seat_number
    self.deck = deck
    self.action = -1
    self.pot = 0
    self.active_players = []
    self.community_cards = []

    if players == None:
      self.players = []
      self.players = players
    else:
      self.players = players
  
  @abstractmethod
  def deal(self):
    pass

  def print_table(self):
    print("Pot: ${}".format(self.pot))
    for player in self.active_players:
      if(player.status != "out"):
        print("Player {} [Stack: ${}]: {}{} {}{}".format(player.player_id, player.stack, player.hand.card1.value, player.hand.card1.suit[0], player.hand.card2.value, player.hand.card2.suit[0]))


  def print_all_players(self):
    print("Pot: ${}".format(self.pot))
    for player in self.players:
      if(True):
        print("Player {} [Stack: ${}]: {}{} {}{}".format(player.player_id, player.stack, player.hand.card1.value, player.hand.card1.suit[0], player.hand.card2.value, player.hand.card2.suit[0]))
    

  def reset_player_round_amounts(self):
    for player in self.active_players:
      player.money_out = 0
      player.owed = 0

  def print_community_cards(self):
    for i in self.community_cards:
      print("{}{}".format(i.value, i.suit[0]))

  def showdown(self):

    # # test data (delete later)
    # test_card1 = Card('A', 'diamond', 14)
    # test_card2 = Card('5', 'spade', 5)
    # hand1 = Hand(test_card1, test_card2)

    # test_card3 = Card('K', 'club', 13)
    # test_card4 = Card('K', 'spade', 13)
    # hand2 = Hand(test_card3, test_card4)

    # test_card5 = Card('9', 'heart', 9)
    # test_card6 = Card('10', 'heart', 10)
    # hand3 = Hand(test_card5, test_card6)

    # test_card7 = Card('4', 'heart', 4)
    # test_card8 = Card('5', 'heart', 4)
    # test_card9 = Card('6', 'heart', 6)
    # test_card10 = Card('7', 'heart', 7)
    # test_card11 = Card('8', 'heart', 8)
    # self.community_cards = [test_card7, test_card8, test_card9, test_card10, test_card11]

    # self.players[0].hand = hand1
    # self.players[1].hand = hand2
    # self.players[2].hand = hand3

    # test (delete this later)
    for player in self.players:
      print("Player {} [Stack: ${}]: {}{} {}{}".format(player.player_id, player.stack, player.hand.card1.value, player.hand.card1.suit[0], player.hand.card2.value, player.hand.card2.suit[0]))

    print("Community Cards: ")
    print(*self.community_cards)    

    # iterate through all players
    for player in self.players:

      # check to see if player folded before showdown
      if(player.status != "out"):

        # assign all of their hand rankings
        player.hand_data+=self.assign_hand_ranking(player)
    
    top_hand_rank = -1
    winning_player = Player()
    tie = False
    for player in self.players:
      if(player.status!="out"):
        if(player.hand_rank == top_hand_rank):
          tie = True
        if(player.hand_rank>top_hand_rank):
          winning_player = player
          top_hand_rank = player.hand_rank
          tie = False
    
    #  if one player has a clear win (higher hand type than all other players)
    if(tie == False):
      # give them the pot
      winning_player.stack += self.pot
      self.pot = 0

      # test (delete this later)
      for player in self.players:
        print("Player {} [Stack: ${}]: {}{} {}{}".format(player.player_id, player.stack, player.hand.card1.value, player.hand.card1.suit[0], player.hand.card2.value, player.hand.card2.suit[0]))
    
    # if  two players tie for best hand type
    else:
      # locate players that tie and load to list
      tie_players = []
      for player in self.players:
        if player.hand_rank == winning_player.hand_rank:
          tie_players.append(player)


      # flush analysis [5]
      if winning_player.hand_rank == 5:
        nested_tie = False
        nested_tie_players = []
        highest_player = None
        highest_weight = -1
        for player in tie_players:
          total_weight = 0
          for card in player.hand_data[1]:
            total_weight += card.weight
          if total_weight>highest_weight:
            highest_weight = total_weight
            highest_player = player
            nested_tie = False
            nested_tie_players = [player]
            continue
          if total_weight == highest_weight:
            nested_tie = True
            nested_tie_players.append(player)
        # if only one player wins, give them the entire pot
        if nested_tie == False:
          highest_player.stack += self.pot
          self.pot = 0
        # if multiple players win, divide the pot and increment their stacks
        else:
          total_tie_players = len(nested_tie_players)
          for player in nested_tie_players:
            player.stack+=(self.pot/total_tie_players)
          self.pot = 0


      # straight analysis (straight, straight flush) [8, 4]
      if winning_player.hand_rank in [8, 4]:
        nested_tie_players = []
        nested_tie = False
        highest_straight = -1
        highest_player = None
        # iterate through tie players
        for player in tie_players:
          # strip hand_data for high value in integer format
          tokenized_hand_data = player.hand_data[0].split(' ')
          for index, token in enumerate(tokenized_hand_data):
            if token == 'high':
              high_card = tokenized_hand_data[index-1]
              try:
                high_value = int(high_card)
              except:
                card_dict = {
                  'J':11,
                  'Q':12,
                  'K':13,
                  'A':14
                }
                high_value = card_dict[high_card]
          if high_value > highest_straight:
            highest_straight = high_value
            highest_player = player
            nested_tie = False
            nested_tie_players = [player]
            continue
          if high_value == highest_straight:
            nested_tie = True
            nested_tie_players.append(player)
        # if only one player wins, give them the entire pot
        if nested_tie == False:
          highest_player.stack += self.pot
          self.pot = 0
        # if multiple players win, divide the pot and increment their stacks
        else:
          total_tie_players = len(nested_tie_players)
          for player in nested_tie_players:
            player.stack+=(self.pot/total_tie_players)
          self.pot = 0
      

      # two pair analysis [2]
      if winning_player.hand_rank == 2:
        highest_player = None
        highest_kicker = -1
        highest_pair = -1
        lowest_pair = -1
        nested_tie_players = []
        nested_tie = False
        for player in tie_players:
          two_pair_values = []
          tokenized_hand_data = player.hand_data[0].split(' ')
          kicker_value = ''
          kicker_int = -1
          high_pair = -1
          low_pair = -1
          for index, token in enumerate(tokenized_hand_data):
            if '\'s' in token:
              two_pair_values.append(token.split('\'')[0])
            if token == 'kicker':
              kicker_value = tokenized_hand_data[index-1]

          # convert kicker to int
          try:
            kicker_int = int(kicker_value)
          except:
            card_dict = {
              'J':11,
              'Q':12,
              'K':13,
              'A':14
            }
            kicker_int = card_dict[kicker_value]

          # convert one pair to int
          pair1 = two_pair_values[0]
          pair2 = two_pair_values[1]
          try:
            pair1_int = int(pair1)
          except:
            card_dict = {
              'J':11,
              'Q':12,
              'K':13,
              'A':14
            }
            pair1_int = card_dict[pair1]

          # convert second pair to int
          try:
            pair2_int = int(pair2)
          except:
            card_dict = {
              'J':11,
              'Q':12,
              'K':13,
              'A':14
            }
            pair2_int = card_dict[pair2]
          
          if pair1_int>pair2_int:
            high_pair = pair1_int
            low_pair = pair2_int
          else:
            high_pair = pair2_int
            low_pair = pair1_int
          
          # check highest pair
          if high_pair>highest_pair:
            highest_player = player
            highest_pair = high_pair
            lowest_pair = low_pair
            highest_kicker = kicker_int
            nested_tie = False
            nested_tie_players = [player]
            continue
          elif high_pair < highest_pair:
            continue

          # check lowest pair
          if low_pair>lowest_pair:
            highest_player = player
            highest_pair = high_pair
            lowest_pair = low_pair
            highest_kicker = kicker_int
            nested_tie = False
            nested_tie_players = [player]
            continue
          elif low_pair<lowest_pair:
            continue

          # check kicker
          if kicker_int > highest_kicker:
            highest_player = player
            highest_pair = high_pair
            lowest_pair = low_pair
            highest_kicker = kicker_int
            nested_tie = False
            nested_tie_players = [player]
            continue

          # tie condition
          elif kicker_int == highest_kicker:
            nested_tie = True
            nested_tie_players.append(player)

        # if only one player wins, give them the entire pot
        if nested_tie == False:
          highest_player.stack += self.pot
          self.pot = 0
        # if multiple players win, divide the pot and increment their stacks
        else:
          total_tie_players = len(nested_tie_players)
          for player in nested_tie_players:
            player.stack+=(self.pot/total_tie_players)
          self.pot = 0

          
      # kicker analysis (four of a kind)  [7]
      if winning_player.hand_rank == 7:
        highest_player = None
        highest_kicker = -1
        nested_tie_players = []
        nested_tie = False
        for player in tie_players:
          tokenized_hand_data = player.hand_data[0].split(' ')
          for index, token in enumerate(tokenized_hand_data):
            if token == 'kicker':
              kicker_value = tokenized_hand_data[index-1]
              try:
                kicker_int = int(kicker_value)
              except:
                card_dict = {
                  'J':11,
                  'Q':12,
                  'K':13,
                  'A':14
                }
                kicker_int = card_dict[kicker_value]
              if kicker_int == highest_kicker:
                nested_tie = True
                nested_tie_players.append(player)
              if kicker_int > highest_kicker:
                highest_player = player
                highest_kicker = kicker_int
                nested_tie = False
                nested_tie_players = [player]
        # if only one player wins, give them the entire pot
        if nested_tie == False:
          highest_player.stack += self.pot
          self.pot = 0
        # if multiple players win, divide the pot and increment their stacks
        else:
          total_tie_players = len(nested_tie_players)
          for player in nested_tie_players:
            player.stack+=(self.pot/total_tie_players)
          self.pot = 0

      # full house analysis (full house) [6]
      if winning_player.hand_rank == 6:
        highest_player = None
        highest_trips = -1
        highest_pair = -1
        nested_tie_players = []
        nested_tie = False
        for player in tie_players:
          trips_pair_values = []
          tokenized_hand_data = player.hand_data[0].split(' ')
          kicker_int = -1
          high_pair = -1
          low_pair = -1
          for index, token in enumerate(tokenized_hand_data):
            if '\'s' in token:
              trips_pair_values.append(token.split('\'')[0])
          # convert trips to int
          trips = trips_pair_values[0]
          pair = trips_pair_values[1]
          try:
            trips_int = int(trips)
          except:
            card_dict = {
              'J':11,
              'Q':12,
              'K':13,
              'A':14
            }
            trips_int = card_dict[trips]
          pair_int=-1
          # convert pair to int
          try:
            pair_int = int(pair)
          except:
            card_dict = {
              'J':11,
              'Q':12,
              'K':13,
              'A':14
            }
            pair_int = card_dict[pair]
          # check trips
          if trips_int > highest_trips:
            highest_player = player
            highest_trips = trips_int
            highest_pair = pair_int
            nested_tie = False
            nested_tie_players = [player]
            continue
          if trips_int == highest_trips:
            if pair_int > highest_pair:
              highest_player = player
              highest_trips = trips_int
              highest_pair = pair_int
              nested_tie = False
              continue
              nested_tie_players = [player]
            if pair_int == highest_pair:
              nested_tie = True
              nested_tie_players.append(player)
        # if only one player wins, give them the entire pot
        if nested_tie == False:
          highest_player.stack += self.pot
          self.pot = 0
        # if multiple players win, divide the pot and increment their stacks
        else:
          total_tie_players = len(nested_tie_players)
          for player in nested_tie_players:
            player.stack+=(self.pot/total_tie_players)
          self.pot = 0
        
      # high card analysis (high card, pair, three of a kind) [0, 1, 3]
      if winning_player.hand_rank == 0:
        highest_weight = -1
        highest_player = None
        nested_tie = False
        nested_tie_players = []
        for player in tie_players:
          total_weight = 0
          for card in player.hand_data[1]:
            total_weight += card.weight
          if total_weight > highest_weight:
            highest_player = player
            highest_weight = total_weight
            nested_tie = False
            nested_tie_players = [player]
            continue
          if total_weight == highest_weight:
            nested_tie = True
            nested_tie_players.append(player)
        # if only one player wins, give them the entire pot
        if nested_tie == False:
          highest_player.stack += self.pot
          self.pot = 0
        # if multiple players win, divide the pot and increment their stacks
        else:
          total_tie_players = len(nested_tie_players)
          for player in nested_tie_players:
            player.stack+=(self.pot/total_tie_players)
          self.pot = 0
      
      if winning_player.hand_rank in [1,3]:
        highest_pair = -1
        highet_weight = -1
        highest_player = None
        nested_tie = False
        nested_tie_players = []
        for player in tie_players:
          total_weight = 0
          tokenized_hand_data = player.hand_data[0].split(' ')
          for index, token in enumerate(tokenized_hand_data):
            if '\'s' in token:
              pair = token.split('\'')[0]
          try:
            int_pair = int(pair)
          except:
            card_dict = {
              'J':11,
              'Q':12,
              'K':13,
              'A':14
            }
            int_pair = card_dict[pair]
          for card in player.hand_data[1]:
            total_weight+=card.weight
          
          if int_pair > highest_pair:
            highest_pair = int_pair
            highest_weight = total_weight
            highest_player = player
            nested_tie = False
            nested_tie_players = [player]
            continue
          if int_pair == highest_pair:
            if total_weight > highest_weight:
              highest_pair = int_pair
              highest_weight = total_weight
              highest_player = player
              nested_tie = False
              nested_tie_players = [player]
              continue
            if total_weight == highest_weight:
              nested_tie = True
              nested_tie_players.append(player)
        # if only one player wins, give them the entire pot
        if nested_tie == False:
          highest_player.stack += self.pot
          self.pot = 0
        # if multiple players win, divide the pot and increment their stacks
        else:
          total_tie_players = len(nested_tie_players)
          for player in nested_tie_players:
            player.stack+=(self.pot/total_tie_players)
          self.pot = 0

    # test (delete this later)
    for player in self.players:
      print("Player {} [Stack: ${}]: {}{} {}{}".format(player.player_id, player.stack, player.hand.card1.value, player.hand.card1.suit[0], player.hand.card2.value, player.hand.card2.suit[0]))

  # helper function
  @staticmethod
  def find_high_cards(all_cards, x, excluded_value):
    # default to high card
    high = ''
    high_cards = []
    count = 0
    for val in ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']:
      for card in all_cards:

        #start condition
        if(high == '' and count == 0 and card.value == val and val != excluded_value):
          high = card.value
          count += 1
          high_cards.append(card)
          continue
        
        
        if(card.value == val and val != excluded_value):
          count +=1
          high_cards.append(card)
          if(count == x):
            return high_cards

  #input: table.communitycards, player.hand
  #output: hand rank (royal flush, pair of Aces king kicker, straight to 9, 2s full of threes, ace high flush,)
  def assign_hand_ranking(self, player):
    all_cards = []
    all_cards.append(player.hand.card1)
    all_cards.append(player.hand.card2)
    for card in self.community_cards:
      all_cards.append(card)

    all_cards.sort(key=lambda x: x.weight)

    #print(all_cards)

    #good
    # check for royal flush
    for suit in Deck.suits:
      suit_live = True
      for val in ['10','J','Q','K','A']:
        if(suit_live == True):
          suit_live = False
          for card in all_cards:
            if(card.value == val and card.suit == suit and card.value == 'A'):
              player.hand_rank = 9
              return ["Royal Flush {}".format(card.suit)]
            if(card.value == val and card.suit == suit):
              suit_live = True

    #good
    # check for straight flush
    for suit in Deck.suits:
      count = 0
      high = ''
      for val in ['K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2', 'A']:
        card_found = False
        for card in all_cards:
          if(card_found ==True):
            break
          if(card.value == val and card.suit == suit and count == 0):
            high = card.value
            card_found = True
            count += 1
            continue
          if(card.value == val and card.suit == suit):
            count += 1
            card_found = True
            if(count == 5):
              player.hand_rank = 8
              return ["Straight Flush {} high".format(high)]
            continue
        if(card_found == False):
          count = 0
          high = ''

              
    # good
    # check for 4 of a kind
    for card in all_cards:
      pair_counter = 0
      for i in all_cards:
        if(card.value == i.value):
          pair_counter += 1
          if(pair_counter == 4):
            kicker_weight = 0
            for j in all_cards:
              if(kicker_weight < j.weight):
                kicker = j
                kicker_weight = j.weight

            player.hand_rank = 7
            return ["4 of a kind ({}'s) {} kicker".format(card.value, kicker.value)]
            #return kicker
    
    # done
    # check for full house
    trips = ''
    pair = ''

    # find three of a kind
    for val in ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']:
      pair_counter = 0
      for card in all_cards:
        if (card.value == val):
          pair_counter += 1
          if(pair_counter == 3):
            trips = card.value
    
    # find pair
    for val in ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']:
      pair_counter = 0
      for card in all_cards:
        if(card.value == trips):
          continue
        if (card.value == val):
          pair_counter += 1
          if(pair_counter == 2):
            pair = card.value

    if(trips != '' and pair != ''):
      player.hand_rank = 6
      return ["Full House {}'s full of {}'s".format(trips, pair)]

    #done
    # check for flush
    for suit in Deck.suits:
      high = ''
      flush_cards = []
      count = 0
      for val in ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']:
        for card in all_cards:

          #start condition
          if(high == '' and count == 0 and card.suit == suit and card.value == val):
            high = card.value
            count += 1
            flush_cards.append(card)
            continue
          
          
          if(card.suit == suit and card.value == val):
            count +=1
            flush_cards.append(card)

            # stop condition
            if(count == 5):
              player.hand_rank = 5
              return ["Flush {} high".format(high), flush_cards]




    #done
    # check for straight
    count = 0
    high = ''
    for val in ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2', 'A']:
      card_found = False
      for card in all_cards:
        if(card_found ==True):
          break

        # start condition
        if(card.value == val and count == 0):
          high = card.value
          card_found = True
          count += 1
          continue
        if(card.value == val):
          count += 1
          card_found = True

          # stop condition
          if(count == 5):
            player.hand_rank = 4
            return ["Straight {} high".format(high)]
          continue
        
      if(card_found == False):
        count = 0
        high = ''

    # done     
    # check for 3 of a kind
    for card in all_cards:
      pair_counter = 0
      for i in all_cards:
        if(card.value == i.value):
          pair_counter += 1
          if(pair_counter == 3):
            player.hand_rank = 3
            return ["3 of a kind {}'s".format(card.value), self.find_high_cards(all_cards, 2, card.value)]
            

    # check for 2 pair
    pair1 = ''
    pair2 = ''

    # find pair 1
    for val in ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']:
      pair_counter = 0
      for card in all_cards:
        if (card.value == val):
          pair_counter += 1
          if(pair_counter == 2):
            pair1 = card.value
    
    # find pair 2
    for val in ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']:
      pair_counter = 0
      for card in all_cards:
        if(card.value == pair1):
          continue
        if (card.value == val):
          pair_counter += 1
          if(pair_counter == 2):
            pair2 = card.value



    if(pair1 != '' and pair2 != ''):
      for val in ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']:
        for card in all_cards:
          if (card.value == val and card.value != pair1 and card.value != pair2):
            kicker = card
            player.hand_rank = 2
            return ["Two Pair {}'s and {}'s {} kicker".format(pair1, pair2, kicker.value)]

    # done
    # check for pair
    for card in all_cards:
      pair_counter = 0
      for i in all_cards:
        if(card.value == i.value):
          pair_counter += 1
          if(pair_counter == 2):
            player.hand_rank = 1
            return ["Pair of {}'s".format(card.value), self.find_high_cards(all_cards, 3, card.value)]

    #done
    # default to high card
    high_cards = self.find_high_cards(all_cards, 5, '')
    player.hand_rank = 0
    return ["High card {}".format(high_cards[0].value), high_cards]

  def send_action(self):
  
    # find player whos turn it is
    for player in self.players:
      if player.action == True:
        for connection in self.connections:
          connection.send(bytes("Action: {}".format(player.seat_number),'utf-8'))
        break
    # tell all clients whos turn it is
  
  def preflop(self):
    self.current_betting_round = 'preflop'
    # add all players that are dealt in to the active players list
    for player in self.players:
      player.status = "starting round"
      self.active_players.append(player)
    #self.print_table()
    self.send_action()
  
  def flop(self):
    self.deck.cards.remove(self.deck.cards[0]) # burn
    self.community_cards.append(self.deck.cards[0])
    self.community_cards.append(self.deck.cards[1])
    self.community_cards.append(self.deck.cards[2])

    self.deck.cards.remove(self.deck.cards[0])
    self.deck.cards.remove(self.deck.cards[0])
    self.deck.cards.remove(self.deck.cards[0])

    server_response = "Flop: {}{} {}{} {}{}".format(self.community_cards[0].value, self.community_cards[0].suit[0], self.community_cards[1].value, self.community_cards[1].suit[0], self.community_cards[2].value, self.community_cards[2].suit[0])

    for connection in self.connections:
      connection.send(bytes(server_response, 'utf-8'))
    
    time.sleep(0.1)

    self.reset_player_round_amounts()
    self.active_players = []
    for player in self.players:
      if player.status != "out":
        player.status = "starting round"
        self.active_players.append(player)
    self.send_action()

  def turn(self):
    self.reset_player_round_amounts()

    self.deck.cards.remove(self.deck.cards[0]) # burn
    self.community_cards.append(self.deck.cards[0])
    self.deck.cards.remove(self.deck.cards[0])

    server_response = "Turn: {}{} {}{} {}{} {}{}".format(self.community_cards[0].value, self.community_cards[0].suit[0], self.community_cards[1].value, self.community_cards[1].suit[0], self.community_cards[2].value, self.community_cards[2].suit[0], self.community_cards[3].value, self.community_cards[3].suit[0])

    for connection in self.connections:
      connection.send(bytes(server_response, 'utf-8'))
    
    time.sleep(0.1)

    self.reset_player_round_amounts()
    self.active_players = []
    for player in self.players:
      if player.status != "out":
        player.status = "starting round"
        self.active_players.append(player)
    self.send_action()
  
  def river(self):
    self.reset_player_round_amounts()
    #self.print_table()

    self.deck.cards.remove(self.deck.cards[0]) # burn
    self.community_cards.append(self.deck.cards[0])
    self.deck.cards.remove(self.deck.cards[0])

    server_response = "River: {}{} {}{} {}{} {}{} {}{}".format(self.community_cards[0].value, self.community_cards[0].suit[0], self.community_cards[1].value, self.community_cards[1].suit[0], self.community_cards[2].value, self.community_cards[2].suit[0], self.community_cards[3].value, self.community_cards[3].suit[0], self.community_cards[4].value, self.community_cards[4].suit[0])

    for connection in self.connections:
      connection.send(bytes(server_response, 'utf-8'))
    
    time.sleep(0.1)

    self.reset_player_round_amounts()
    self.active_players = []
    for player in self.players:
      if player.status != "out":
        player.status = "starting round"
        self.active_players.append(player)
    self.send_action()
  
  def deal(self):
    # shuffle and deal
    self.deck.shuffle()
    seats_and_hands = []
    for player in self.players:
      player.hand = Hand(self.deck.cards[0], self.deck.cards[1])
      self.deck.cards.remove(self.deck.cards[0])
      self.deck.cards.remove(self.deck.cards[0])
      seats_and_hands.append((player.seat_number, Hand.__str__(player.hand)))
    for connection in self.connections:
      for i in seats_and_hands:
        connection.send(bytes("Dealt: {} {}".format(i[0], i[1]), 'utf-8'))
        time.sleep(0.1)
    
    self.preflop()