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


    self.print_community_cards()

    self.decision()

    # # delete this later (testing hand assign hand rankings function)
    for player in self.players:
      player.hand.card1 = Card('8', 'diamond',8)
      player.hand.card2 = Card('3', 'diamond',3)

      self.community_cards[0] = Card('A', 'heart', 14)
      self.community_cards[1] = Card('5', 'spade', 5)
      self.community_cards[2] = Card('A', 'diamond', 14)
      self.community_cards[3] = Card('8', 'heart', 8)
      self.community_cards[4] = Card('9', 'spade', 9)

      print('{}'.format(self.assign_hand_ranking(player)))
  
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
              return "Royal Flush {}".format(card.suit)
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
              return "Straight Flush {} high".format(high)
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

            return "4 of a kind ({}'s) [{} kicker]".format(card.value, kicker.value)
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
      return "Full House {}'s full of {}'s".format(trips, pair)

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
              return "Flush {} high".format(high), flush_cards




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
            return "Straight {} high".format(high)
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
            return "3 of a kind ({}'s)".format(card.value), self.find_high_cards(all_cards, 2, card.value)
            

    # check for 2 pair
    pair1 = ''
    pair2 = ''

    # find three of a kind
    for val in ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']:
      pair_counter = 0
      for card in all_cards:
        if (card.value == val):
          pair_counter += 1
          if(pair_counter == 2):
            pair1 = card.value
    
    # find pair
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
            return"Two Pair {}'s and {}'s".format(pair1, pair2), kicker

    # done
    # check for pair
    for card in all_cards:
      pair_counter = 0
      for i in all_cards:
        if(card.value == i.value):
          pair_counter += 1
          if(pair_counter == 2):
            return "pair of ({}'s)".format(card.value), self.find_high_cards(all_cards, 3, card.value)

    #done
    # default to high card
    high_cards = self.find_high_cards(all_cards, 5, '')
    return "High card {}".format(high_cards[0].value), high_cards



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
  def __init__(self, room_frame, x, y, img_chips, img_card_back, img_buy_in):
    #frame for each player
    player_frame = Frame(room_frame, bg="#505b62", width=104, height=140)
    player_frame.place(x=x, y=y)

    card_one_frame = return_card_frame(player_frame, "gray")
    card_two_frame = return_card_frame(player_frame, "gray")
    
    card_one_frame.grid(row=0,column=0)
    card_two_frame.grid(row=0,column=1)

    lb_img_chips = Label(player_frame, bg="#505b62", image=img_chips)
    lb_img_chips.grid(row=2, column=0)

    #player frame widgets
    #if player is seated
    player_is_seated = True
    if player_is_seated == True:
      lb_img_card_one = Label(card_one_frame, bg="#505b62", image=img_card_back)
      lb_img_card_two = Label(card_two_frame, bg="#505b62", image=img_card_back)
      lb_player_name = Label(player_frame, bg="#505b62", text="Test Player Name", font="Helvetica 10 bold")
      lb_player_stack = Label(player_frame, bg="#505b62", text="$200", font="Helvetica 10 bold")
      lb_player_action = Label(player_frame, bg="#505b62", text="Action", font="Helvetica 10 bold")

      lb_player_name.grid(row=1, column=0, columnspan=2)
      lb_player_stack.grid(row=2, column=1)
      lb_player_action.grid(row=3, column=1)

      lb_img_card_one.pack()
      lb_img_card_two.pack()
    else:
      #player is not seated, allow buy-in
      bttn_buy_in = Button(player_frame, image=img_buy_in, borderwidth=0, bg="#505b62", activebackground="#505b62")
      entry_buy_in = Entry(player_frame, width=6, bg="#505b62")
      buy_in_min = 10
      entry_buy_in.insert(0, str(buy_in_min))
      #add later, if player bank < max buyin, buy_in_max = bank 
      buy_in_max = 200
      buy_in_range = "$" + str(buy_in_min) + "-" + "$" + str(buy_in_max)
      lb_buy_in_range = Label(player_frame, bg="#505b62", text=buy_in_range, font="Helvetica 10 bold")
      
      bttn_buy_in.grid(row=1, column=0, columnspan=2)
      entry_buy_in.grid(row=2, column=1)
      lb_buy_in_range.grid(row=3, column=1)
    lb_player_seat = Label(player_frame, bg="#505b62", text="Seat #")
    lb_player_seat.grid(row=3, column=0)

def initialize_card_images():
  card_images = {}
  suits = ("h", "d", "c", "s")
  for suit in suits:
    for n in range(1,14):
      card_name = suit+str(n)
      file_string = "img/cards/" + card_name + ".png"
      card_images[card_name] = PhotoImage(file=file_string)
  return card_images

def return_card_frame(parent, color):
  if color == "gray":
    bg = "#505b62"
  else:
    bg = "#35654d"
  card_frame = LabelFrame(parent, bg=bg, width=50, height=68, borderwidth=2, relief="groove")
  return card_frame

def gui():
  #GUI window
  gui = Tk()
  canvas = Canvas()
  gui.title("Poker App")
  gui.config(bg="#D3D3D3")
  gui.geometry("1200x800")
  gui.resizable(False, False)

  #initialize images
  img_leave_table = PhotoImage(file="img/leave_table.png")
  img_buy_in = PhotoImage(file="img/buy_in.png")
  img_cash_out = PhotoImage(file="img/cash_out.png")
  img_chips = PhotoImage(file="img/chips.png")
  img_pot = PhotoImage(file="img/pot.png")
  img_card_back = PhotoImage(file="img/card_back.png")
  img_fold = PhotoImage(file="img/fold.png")
  img_check = PhotoImage(file="img/check.png")
  img_call = PhotoImage(file="img/call.png")
  img_bet = PhotoImage(file="img/bet.png")
  img_raise = PhotoImage(file="img/raise.png")
  img_reraise= PhotoImage(file="img/re-raise.png")
  card_images = initialize_card_images()

  #window widgets

  #room frame
  room_frame = Frame(gui, bg="#505b62", width=1200, height=600)
  room_frame.pack()

  #table frame
  table_frame = Canvas(room_frame, bg="#505b62", width=800, height=300, highlightthickness=0)
  table_frame.create_oval(0, 0, 800, 300, outline = "#65354d", fill = "#35654d",width = 2)
  table_frame.place(relx=0.5, rely=0.5, anchor="c")

  lb_img_pot = Label(table_frame, bg="#35654d", image=img_pot)
  lb_pot = Label(table_frame, bg="#35654d", text="$1000", font="Helvetica 16 bold")

  lb_img_pot.place(x=400, y=80, anchor="c")
  lb_pot.place(x=400, y=120, anchor="c")

  community_cards_frame = Frame(table_frame, bg="#35654d", width=300, height=72)
  community_cards_frame.place(x=400, y=185, anchor="c")

  lbframe_community_card1 = return_card_frame(community_cards_frame, "green")
  lbframe_community_card2 = return_card_frame(community_cards_frame, "green")
  lbframe_community_card3 = return_card_frame(community_cards_frame, "green")
  lbframe_community_card4 = return_card_frame(community_cards_frame, "green")
  lbframe_community_card5 = return_card_frame(community_cards_frame, "green")

  lbframe_community_card1.grid(row=0, column=0)
  lbframe_community_card2.grid(row=0, column=1)
  lbframe_community_card3.grid(row=0, column=2)
  lbframe_community_card4.grid(row=0, column=3)
  lbframe_community_card5.grid(row=0, column=4)

  img_community_card1 = Label(lbframe_community_card1, bg="#35654d", image=card_images["d3"])
  img_community_card2 = Label(lbframe_community_card2, bg="#35654d", image=card_images["h13"])
  img_community_card3 = Label(lbframe_community_card3, bg="#35654d", image=card_images["s1"])
  img_community_card4 = Label(lbframe_community_card4, bg="#35654d", image=card_images["s6"])
  img_community_card5 = Label(lbframe_community_card5, bg="#35654d", image=card_images["c11"])

  img_community_card1.pack()
  img_community_card2.pack()
  img_community_card3.pack()
  img_community_card4.pack()
  img_community_card5.pack()

  #Coordinates of each player frame
  coord_list = [(548, 458), (268, 438), (48, 258), (190, 40), (428, 6), (668, 6), (906, 40), (1048, 258), (828, 438)] 

  #Loop to create frame for each player
  player_gui_list = []
  for x, y in coord_list:
    player_gui_list.append(PlayerGUI(room_frame, x, y, img_chips, img_card_back, img_buy_in))
  
  #Chat frame
  chat_frame = Frame(gui, bg="#ffffff", width=796, height=196)
  chat_frame.place(x=2, y=798, anchor="sw")

  #Frame for action buttons
  action_frame = Frame(gui, width=396, height=196)
  action_frame.place(x=1198, y=798, anchor="se")

  is_player_turn = False
  #if player's turn allow action buttons
  if is_player_turn:
    action_status = NORMAL
  #else disable action buttons
  else:
    action_status = DISABLED

  bttn_action1 = Button(action_frame, image=img_fold, borderwidth=0, state=action_status)

  table_bet_status = 0
  #if no bets yet
  if table_bet_status == 0:
    action_2 = img_check
    action_3 = img_bet
  #if one bet on table
  if table_bet_status == 1:
    action_2 = img_call
    action_3 = img_raise
  #if someone has raised
  if table_bet_status == 2:
    action_2 = img_call
    action_3 = img_reraise

  bttn_action2 = Button(action_frame, image=action_2, borderwidth=0, state=action_status)
  bttn_action3 = Button(action_frame, image=action_3, borderwidth=0, state=action_status)
  entry_bet_amount = Entry(action_frame, width=6)
  bet_min = 2
  bet_max = 200
  entry_bet_amount.insert(0, str(bet_min))
  bet_range = "$" + str(bet_min) + "-" + "$" + str(bet_max)
  lb_bet_range = Label(action_frame, text=bet_range, font="Helvetica 10 bold")

  player_is_seated = True
  #if player is seated
  if player_is_seated == True:
    action_4 = img_cash_out
  #else player is not seated
  else:
    action_4 = img_leave_table
  bttn_action4 = Button(action_frame, image=action_4, borderwidth=0)

  bttn_action1.place(x=100, y=25, anchor="n")
  bttn_action2.place(x=200, y=25, anchor="n")
  bttn_action3.place(x=300, y=25, anchor="n")
  bttn_action4.place(x=200, y=171, anchor="s")
  entry_bet_amount.place(x=300, y=70, anchor="n")
  lb_bet_range.place(x=300, y= 100, anchor="n")

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