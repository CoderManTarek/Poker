import random
#done
class Card:
  def __init__(self, value, suit):
    self.value = value
    self.suit = suit

#add shuffle
class Deck:
  values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
  suits = ['heart', 'club', 'diamond', 'spade']
  def __init__(self):
    self.cards = []
    for i in self.values:
      for j in self.suits:
        card = Card(i, j)
        self.cards.append(card)
  
  def shuffle(self):
    random.shuffle(self.cards)

  def print_cards_remaining(self):
    for card in self.cards:
      print("{} {}".format(card.value, card.suit))
#done
class Hand:
  def __init__(self, card1, card2):
    self.card1 = card1
    self.card2 = card2

#add must be able to handle players playing through hands. most code will be here  
class Table:
  cap = 10000
  def __init__(self, deck, total_seats,players = None, button_seat_number = 1):
    self.total_seats = total_seats
    self.button_seat_number = button_seat_number
    self.deck = deck
    self.action = -1
    self.pot = 0

    if players == None:
      self.players = []
    else:
      self.players = players
  
  def deal(self):
    # shuffle and deal
    self.deck.shuffle()
    for player in self.players:
      # change all players status
      player.status = "in"

      player.hand = Hand(self.deck.cards[0], self.deck.cards[len(self.players)])
      self.deck.cards.remove(self.deck.cards[0])
      self.deck.cards.remove(self.deck.cards[len(self.players)-1])
    
    # preflop
    self.preflop()

  def print_table(self):
    print("Pot: ${}".format(self.pot))
    for player in self.players:
      print("Player {} [Starting Stack: ${}]: {}{} {}{}".format(player.player_id, player.stack, player.hand.card1.value, player.hand.card1.suit[0], player.hand.card2.value, player.hand.card2.suit[0]))

  def preflop(self):
    #set action at utg+1
    x = 1
    self.action = x
    #check to see if someone has the action and we need to wait
    while True:
      active_action = False
      for player in self.players:
        active_action = False
        if(player.action == True):
          active_action = True
          break;

      for player in self.players:
        if(active_action == False):  
          if(player.player_id == self.action and player.status != "out"):
            x = 0
            self.print_table()
            player.action = True
            x = player.listen_for_action()
            self.pot += x
            #iterate action,
            self.action += 1
            if(self.action == 10):
              self.action = self.action%9
            break;
      
    
  

# add raise(amount), check(), fold(), rebuy(amount)
class Player:
  num_of_players = 0
  def __init__(self, player_id, seat_number, stack, hand = None):
    self.player_id = player_id
    self.seat_number = seat_number
    self.stack = stack
    self.hand = hand
    self.action = False
    self.listen_for_action()
    self.status = "out" # out, in (check possible),to call x, good
    self.owed = 0
  
  def listen_for_action(self):
    if(self.action == True):
      choice = input("Player {} has the action: ".format(self.player_id))
      # if player checks
      if(choice == 'c'):
        self.check()
        return 0
      if(choice == 'f'):
        self.fold()
        return 0
      if(choice[0] == 'b'):
        tmp, amount = choice.split(' ')
        self.bet(int(amount))
        return int(amount)
  
  def check(self):
    self.action = False
    #self.status = "good"
  
  def fold(self):
    self.action = False
    self.status = "out"
  
  def bet(self, amount):
    self.stack -= amount
    self.action = False
    self.status = "bet {}".format(amount)


def main():
  players = []

  #instantiate players
  for i in range(9):
    x = Player(i+1, i+1, 200)
    players.append(x)


  # instantiate deck and table
  deck = Deck()
  table = Table(deck, 9, players)

  #test shuffle
  table.deal()


main()