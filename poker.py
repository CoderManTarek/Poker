import random
from operator import attrgetter
from tkinter import *
import tkinter as tk
import os

class Card:
  #constructor
  def __init__(self, value, suit, weight):
    self.value = value
    self.suit = suit
    self.weight = weight

  def __repr__(self):
        return '{' + self.value + ', ' + self.suit + ', ' + str(self.weight) + '}'


#add shuffle
class Deck:
  values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
  suits = ['heart', 'club', 'diamond', 'spade']
  def __init__(self):
    self.cards = []
    for i in self.values:
      for j in self.suits:
        # get card weights
        try:
          # deal with numerical card values
          k = int(i)
        except:
          #deal with face cards
          face_card_weights = {
            'J':11,
            'Q':12,
            'K':13,
            'A':14
          }
          k = face_card_weights[i]
        card = Card(i, j, k)
        self.cards.append(card)
  
  def shuffle(self):
    random.shuffle(self.cards)

  def print_cards_remaining(self):
    for card in self.cards:
      print("{} {} {}".format(card.value, card.suit, card.weight))

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
    self.active_players = []
    self.community_cards = []

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
    
    # add condition to see if everyone folded ex: if len(active_players > 1)
    self.preflop()
    self.flop()
    self.turn()
    self.river()
    for player in self.active_players:
      if(player.status!="out"):
        pass
        self.assign_hand_ranking(player)
    #self.showdown()

  def print_table(self):
    print("Pot: ${}".format(self.pot))
    for player in self.active_players:
      if(player.status != "out"):
        print("Player {} [Starting Stack: ${}]: {}{} {}{}".format(player.player_id, player.stack, player.hand.card1.value, player.hand.card1.suit[0], player.hand.card2.value, player.hand.card2.suit[0]))

  def decision(self):
    
    # circle action around and track decisions, until stop conditions are met
    while(True):
      for player in self.active_players:
        # stop condition
        stop = True
        for plyr in self.active_players:
          if(plyr.status == "starting round"):
            stop = False
          if(plyr.status == "in (money owed)"):
            stop = False
        
        if(stop == True):
          print("betting round is over")
          for plyr in self.active_players:
            if(plyr.status == "in (money not owed)"):
              plyr.status = "starting round"
          return

        if(player.status == "out"):
          continue
        self.print_table()
        
        # make a decision 
        choice, amount = player.handle_action()

        # change their status to folded
        if(choice == "fold"):
          player.status = "out"
        if(choice == "bet"):
          self.pot += amount
          # change players amount owed
          for plyr in self.active_players:
            if(plyr == player):
              continue
            if(plyr.status != "out"):
              plyr.owed = player.money_out
              plyr.status = "in (money owed)"
        if(choice == "call"):
          self.pot += amount
        if(choice == "check"):
          pass

  def reset_player_round_amounts(self):
    for player in self.active_players:
      player.money_out = 0
      player.owed = 0

  def print_community_cards(self):
    for i in self.community_cards:
      print("{}{}".format(i.value, i.suit[0]))

  def preflop(self):
    # add all players that are dealt in to the active players list
    for player in self.players:
      player.status = "starting round"
      self.active_players.append(player)
    #self.print_table()
    self.decision()
  
  def flop(self):
    self.reset_player_round_amounts()

    # deal 3 community cards
    self.community_cards.append(self.deck.cards[0])
    self.community_cards.append(self.deck.cards[1])
    self.community_cards.append(self.deck.cards[2])
    self.deck.cards.remove(self.deck.cards[2])
    self.deck.cards.remove(self.deck.cards[1])
    self.deck.cards.remove(self.deck.cards[0])

    self.print_community_cards()

    self.decision()

  def turn(self):
    self.reset_player_round_amounts()

    self.community_cards.append(self.deck.cards[0])
    self.deck.cards.remove(self.deck.cards[0])

    self.print_community_cards()


    #self.print_table()
    self.decision()
  
  def river(self):
    self.reset_player_round_amounts()
    #self.print_table()

    self.community_cards.append(self.deck.cards[0])
    self.deck.cards.remove(self.deck.cards[0])

    # # delete this later (testing hand assign hand rankings function)
    for player in self.players:
      player.hand.card1 = Card('A', 'diamond',14)
      player.hand.card2 = Card('K', 'diamond',13)

      self.community_cards[0] = Card('A', 'spade', 12)
      self.community_cards[1] = Card('A', 'diamond', 11)
      self.community_cards[2] = Card('10', 'diamond', 10)

      print('{}'.format(self.assign_hand_ranking(player)))



    self.print_community_cards()

    self.decision()
  
  def showdown(self):
    pass
    # objective: find the player that has the best hand and give them the pot

    # steps

    # find the player with the best hand
    # iterate through all players
      # assign all of their hand rankings (make separate assign function assign(table.communitycards, player.hand) will return hand ranking)
      # compare to see who had the highest hand type
      #  if one player has a clear win (higher hand type than all other players)
          # give them the pot
      #   if  two players tie for best hand type
      #       compare hand values (2-A)
              # if values are the same
              #     tie()
              # else:
              #     give winner pot
    #
    # give the player the pot

  #input: table.communitycards, player.hand
  #output: hand rank (royal flush, pair of Aces king kicker, straight to 9, 2s full of threes, ace high flush,)
  def assign_hand_ranking(self, player):
    all_cards = []
    all_cards.append(player.hand.card1)
    all_cards.append(player.hand.card2)
    for card in self.community_cards:
      all_cards.append(card)

    all_cards.sort(key=lambda x: x.weight)

    print(all_cards)

    best = []
    desc = []
    hand_max = 5

    # check for royal flush
    for suit in Deck.suits:
      suit_live = True
      ind = []
      for val in ['10','J','Q','K','A']:
        if(suit_live == True):
          suit_live = False
          for i in range(len(all_cards)):
            if(all_cards[i].value == val and all_cards[i].suit == suit and all_cards[i].value == 'A'):
              for j in range(len(ind)):
                best.append(all_cards[ind[j]-j])
                all_cards.remove(all_cards[ind[j]-j])
                desc.append("Royal Flush {}".format(all_cards[i].suit))
              # return "Royal Flush {}".format(all_cards[i].suit)
            if(all_cards[i].value == val and all_cards[i].suit == suit):
              ind.append(i)
              suit_live = True

    # check for straight flush


    # check for 4 of a kind
    if hand_max-len(best) >= 4:
      for card in all_cards:
        pair_counter = 0
        ind = []
        for i in range(len(all_cards)):
          if(card.value == all_cards[i].value):
            if i not in ind:
              ind.append(i)
            pair_counter += 1
            if(pair_counter == 4):
              for j in range(len(ind)):
                best.append(all_cards[ind[j]-j])
                all_cards.remove(all_cards[ind[j]-j])
              desc.append("4 of a kind ({}'s)".format(card.value))
              break
              # return "4 of a kind ({}'s)".format(card.value)
    

      

    # check for full house

    # check for flush

    # check for straight
    # for card in all_cards:
    #   last_card_weight = 0
    #   x = card.weight
    
      
    # check for 3 of a kind
    if hand_max-len(best) >= 3:
      for card in all_cards:
        pair_counter = 0
        ind = []
        for i in range(len(all_cards)):
          if(card.value == all_cards[i].value):
            if i not in ind:
              ind.append(i)
            pair_counter += 1
            if(pair_counter == 3):
              for j in range(len(ind)):
                best.append(all_cards[ind[j]-j])
                all_cards.remove(all_cards[ind[j]-j])
              desc.append("3 of a kind ({}'s)".format(card.value))
              break
              # return "3 of a kind ({}'s)".format(card.value)

    # check for 2 pair

    # check for pair
    while hand_max-len(best) >= 2:
      for card in all_cards:
        pair_counter = 0
        ind = []
        for i in range(len(all_cards)):
          if(card.value == all_cards[i].value):
            if i not in ind:
                ind.append(i)
            pair_counter += 1
            if(pair_counter == 2):
              for j in range(len(ind)):
                best.append(all_cards[ind[j]-j])
                all_cards.remove(all_cards[ind[j]-j])
              desc.append("pair of ({}'s)".format(card.value))
              break
              # return "pair of ({}'s)".format(card.value)

    # default to high card
    junk = False
    while hand_max-len(best) >= 1:
      best.append(all_cards[-1])
      if junk == False:
        desc.append("high card ({})".format(all_cards[-1].value))
        junk = True
      all_cards.remove(all_cards[-1])

    return (best, desc)



# add rebuy(amount)
class Player:
  num_of_players = 0
  def __init__(self, player_id, seat_number, stack, hand = None):
    self.player_id = player_id
    self.seat_number = seat_number
    self.stack = stack
    self.hand = hand
    self.status = "out" # out (folded), starting round, in (money owed), in (money not owed), all in
    self.owed = 0
    self.money_out = 0
  
  # check to see if player has action (is it my turn?) if they do have the action, give them the ability to check, bet, fold, call, etc
  def handle_action(self):
    # check status
    if(self.status == "in (money not owed)" or self.status == "starting round" or self.status == "in (money owed)"):
      # player decision
      choice = input("Player {} has the action: ".format(self.player_id))
      # if player checks
      x = -1
      if(choice == "call"):
        return "call",self.call()
      if(choice[0]=='c'):
        return "check",self.check()
      if(choice[0]=='f'):
        return "fold",self.fold()
      if(choice[0]=='b'):
        c, amount = choice.split(' ')
        self.bet(amount)
        return "bet",int(amount)
      #input to test gui
      if(choice =='gui'):
        gui()
      else:
        return 0
    # if all in or out (folded), skip player
    # if(self.status == "all in" or self.status == "out"):
     
    #  pass
    
    else:
      return 0
  
  def check(self):
    print("Player {} checks".format(self.player_id))
    self.status = "in (money not owed)"
    return 0
  
  def fold(self):
    self.status = "out"
    print("Player {} folds".format(self.player_id))
    return 'f'

  def bet(self, amount):
    bet = int(amount)
    # check if player stack is less than owed plus attempted bet
    # if (self.stack < self.owed+bet)
      #  return "[insert faiure]"
    print("Player {} bets {}".format(self.player_id, amount))
    #change player stack
    self.stack -= int(amount)
    #change player owed
    self.money_out += bet
    #change player status
    if (self.stack == 0):
      self.status = "all in"
    else:
      self.status = "in (money not owed)"
    return bet
    
  def call(self):
    amount = self.owed - self.money_out
    #change player stack
    self.stack -= amount
    #change owed
    self.owed = 0
    self.money_out += amount
    #change status
    print("Player {} calls {}".format(self.player_id, amount))
    if (self.stack == 0):
      self.status = "all in"
    else:
      self.status = "in (money not owed)"
    return amount
  
  def __str__(self):
    return "Player {}".format(self.player_id)

class PlayerGUI:
  def __init__(self, room_frame, x, y, img_chips):
    #frame for each player
    player_frame = Frame(room_frame, bg="#505b62", width=104, height=140)
    player_frame.place(x=x, y=y)

    #player frame widgets
    card_one_frame= LabelFrame(player_frame, bg="#505b62", width=50, height=70, borderwidth=2, relief="groove")
    card_two_frame= LabelFrame(player_frame, bg="#505b62", width=50, height=70, borderwidth=2, relief="groove")
    lb_player_name = Label(player_frame, bg="#505b62", text="Test Player Name", font="Helvetica 10 bold")
    lb_img_chips = Label(player_frame, bg="#505b62", image=img_chips)
    lb_player_stack = Label(player_frame, bg="#505b62", text="$200", font="Helvetica 10 bold")
    lb_player_seat = Label(player_frame, bg="#505b62", text="Seat #")
    lb_player_action = Label(player_frame, bg="#505b62", text="Action text", font="Helvetica 10 bold")


    card_one_frame.grid(row=0,column=0)
    card_two_frame.grid(row=0,column=1)
    lb_player_name.grid(row=1, column=0, columnspan=2)
    lb_img_chips.grid(row=2, column=0)
    lb_player_stack.grid(row=2, column=1)
    lb_player_seat.grid(row=3, column=0)
    lb_player_action.grid(row=3, column=1)

def gui():
  #GUI window
  gui = Tk()
  canvas = Canvas()
  gui.title("Poker App")
  gui.config(bg="#D3D3D3")
  gui.geometry("1200x800")
  gui.resizable(False, False)

  #initialize images
  img_chips = PhotoImage(file="img/chips.png")
  img_pot = PhotoImage(file="img/pot.png")
  #window widgets
  #room frame
  room_frame = Frame(gui, bg="#505b62", width=1200, height=600)
  room_frame.pack(padx=5, pady=5)

  #table frame
  table_frame = Canvas(room_frame, bg="#505b62", width=800, height=300, highlightthickness=0)
  table_frame.create_oval(0, 0, 800, 300, outline = "#65354d", fill = "#35654d",width = 2)
  table_frame.place(relx=0.5, rely=0.5, anchor="center")

  lb_img_pot = Label(table_frame, bg="#35654d", image=img_pot)
  lb_pot = Label(table_frame, bg="#35654d", text="$1000", font="Helvetica 16 bold")

  lb_img_pot.place(x=375, y=100)
  lb_pot.place(x=375, y=160)

  #Coordinates of each player frame
  coord_list = [(548, 458), (278, 438), (48, 258), (200, 50), (428, 6), (668, 6), (896, 50), (1048, 258), (818, 438)] 

  #Loop to create frame for each player
  player_gui_list = []
  for x, y in coord_list:
    player_gui_list.append(PlayerGUI(room_frame, x, y, img_chips))

  # #35654d poker green
  gui.mainloop()

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