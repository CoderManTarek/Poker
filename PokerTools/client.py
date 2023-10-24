import socket
from PokerTools.card import Card
from PokerTools.hand import Hand
from PokerTools.deck import Deck
from PokerTools.player import Player
from tkinter import *
import tkinter as tk
import threading
from PokerTools.clienttable import ClientTable
from PokerTools.assets import Assets
from PokerTools.playergui import PlayerGUI

def initialize_card_images():
  card_images = {}
  suits = ("h", "d", "c", "s")
  for suit in suits:
    for n in range(2,15):
      card_name = str(n)+suit
      file_string = "img/cards/" + card_name + ".png"
      card_images[card_name] = PhotoImage(file=file_string)
  return card_images

class Client:

  # instantiate socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  def sendMsg(self, msg):
      self.sock.send(bytes(msg, 'utf-8'))

  #instantiate thread
  def __init__(self, address):
     #GUI window
    self.gui = Tk()
    self.canvas = Canvas()
    self.gui.title("Poker App")
    self.gui.config(bg="#D3D3D3")
    self.gui.geometry("1200x800")
    self.gui.resizable(False, False)
    self.gui.iconbitmap("img/app_icon.ico")
    self.top_frame = Frame(self.gui, width=1200, height=800)
    self.top_frame.pack()
    self.top_frame.config(bg = "#35654d")
     #initialize images
    self.Images = Assets()
    self.Images.register = PhotoImage(file="img/register.png")
    self.Images.log_in = PhotoImage(file="img/log_in.png")
    self.Images.join_table = PhotoImage(file="img/join_table.png")
    self.Images.leave_table = PhotoImage(file="img/leave_table.png")
    self.Images.buy_in = PhotoImage(file="img/buy_in.png")
    self.Images.cash_out = PhotoImage(file="img/cash_out.png")
    self.Images.chips = PhotoImage(file="img/chips.png")
    self.Images.pot = PhotoImage(file="img/pot.png")
    self.Images.card_back = PhotoImage(file="img/card_back.png")
    self.Images.fold = PhotoImage(file="img/fold.png")
    self.Images.check = PhotoImage(file="img/check.png")
    self.Images.call = PhotoImage(file="img/call.png")
    self.Images.bet = PhotoImage(file="img/bet.png")
    self.Images.raise_img = PhotoImage(file="img/raise.png")
    self.Images.reraise= PhotoImage(file="img/re-raise.png")
    self.Images.start_game = PhotoImage(file="img/start_game.png")
    self.Images.card_images = initialize_card_images()
    self.login_frame = self.create_login_view()
    self.is_on_table = False
    self.table_bet_status = 0
    self.bttn_action1 = None
    self.bttn_action2 = None
    self.bttn_action3 = None
    self.bttn_action4 = None
    self.entry_bet_amount = None
    self.lb_pot = None
    self.img_community_card1 = None
    self.img_community_card2 = None
    self.img_community_card3 = None
    self.img_community_card4 = None
    self.img_community_card5 = None
    self.player_gui_list = []
    self.this_player = ''
    self.table = None
    self.deck = None
    self.players = []
    addressAndPort = address.split(':')
    try:
      self.sock.connect((addressAndPort[0], int(addressAndPort[1])))
      iThread = threading.Thread(target=self.receive_loop)
      iThread.daemon = True
      iThread.start()
    except:
      print("attempt to connect to server was unsuccessful")
      exit(0)

    self.gui.mainloop()




  def receive_loop(self):
    while True:
      try:
        data = self.sock.recv(1024)
      except:
        print("connection to server was lost")
        break
      if not data:
        break
      print(str(data, 'utf-8'))

      message = str(data, 'utf-8')
      tokens = message.split(' ')
      print(tokens)
      # format message
      formattedMessage = ""
      x = 0
      for i in tokens:
        if(x!=0 and x!=1):
          formattedMessage+=i+' '
        x+=1

      # Handle login response from server
      if tokens[0] == 'login':
        if tokens[1] == 'success':
          self.create_dashboard_view(tokens[2], tokens[3])
        #Wrong user or password
        else:
          lb_error_alert = Label(self.login_frame, bg="#E69394", font="Helvetica 12 bold", fg="#8E282A")
          self.set_login_error(lb_error_alert, "authentication", 0)

      if tokens[0] == 'Win:':
        self.table.print_all_players()

      if(tokens[0] == "Action:"):
        for player in self.table.players:
          #find player whos turn it is
          if(int(tokens[1]) == player.seat_number):       
            # is that player on this client
            if(player.player_id == self.this_player):
              # This player has action
              if self.table_bet_status == 0:  
                self.bttn_action1.config(image=self.Images.fold, state=NORMAL, command=lambda:self.decision_fold())
                self.bttn_action2.config(image=self.Images.check, state=NORMAL, command=lambda:self.decision_check())
                self.bttn_action3.config(image=self.Images.bet, state=NORMAL, command=lambda:self.decision_bet(self.entry_bet_amount.get()))
              if self.table_bet_status == 1:
                self.bttn_action1.config(image=self.Images.fold, state=NORMAL, command=lambda:self.decision_fold())
                self.bttn_action2.config(image=self.Images.call, state=NORMAL, command=lambda:self.decision_call())
                self.bttn_action3.config(image=self.Images.raise_img, state=NORMAL, command=lambda:self.decision_bet(self.entry_bet_amount.get()))

              print("you have the action {}, Stack: {}".format(player.player_id, player.stack))


      # if cards have been dealt to players
      if(tokens[0] == "Dealt:"):
        #load cards in player objects within client
        for player in self.table.players:
          if(int(tokens[1]) == player.seat_number):
            try:
              weight = int(tokens[2])
            except:
              #deal with face cards
              face_card_weights = {
                'J':11,
                'Q':12,
                'K':13,
                'A':14
              }
              weight = face_card_weights[tokens[2]]
            card1 = Card(tokens[2], tokens[3], weight)
            try:
              weight = int(tokens[4])
            except:
              #deal with face cards
              face_card_weights = {
                'J':11,
                'Q':12,
                'K':13,
                'A':14
              }
              weight = face_card_weights[tokens[4]]
            card2 = Card(tokens[4], tokens[5], weight)
            player.hand = Hand(card1, card2)
        
        for player in self.table.players:
          if self.this_player == player.player_id:
            for player_gui in self.player_gui_list:
              if self.this_player == player_gui.player_name and player.seat_number == int(tokens[1]):
                card1 = str(player.hand.card1.weight) + player.hand.card1.suit[0]
                card2 = str(player.hand.card2.weight) + player.hand.card2.suit[0]
                img_card1 = self.Images.card_images[card1]
                img_card2 = self.Images.card_images[card2]
                player_gui.update_img_card(img_card1, img_card2)

      # if someone joins the table
      if(tokens[0] == "joined"):
        self.deck = Deck()
        # create a table
        if self.table == None:
          self.table = ClientTable(self.deck, 9, self.players)
        print("table joined")

        # find player whom client belongs to
        if(self.this_player == ''):
          for c in tokens[1]:
            if(c == '('):
              break
            else:
              self.this_player+= c
        check = 0
        temp_player_id = ""
        temp_stack = ""
        temp_player_seat = 0

        # parse all other player data
        for c in message:
          if(c == ')'):
            check = 0
            tmp_player = Player(temp_player_id, int(temp_player_seat), int(temp_stack), None)
            already_seated = False
            for seated_player in self.table.players:
              if seated_player.player_id == tmp_player.player_id:
                already_seated = True
            if(already_seated == False):
              self.table.players.append(tmp_player)
            temp_player_id = ""
            temp_stack = ""
            temp_player_seat = 0
            continue
          if(c == '('):
            check = 1
            continue
          if(c == ' '):
            continue
          if(c == ',' and check == 1):
            check = 2
            continue
          if(c == ',' and check == 3):
            check = 4
            continue
          if(c == ',' and check == 4):
            check = 5
          if(check == 1):
            temp_player_id += c
          if(check == 2):
            temp_player_seat = c
            check = 3
            continue
          if(check == 4):
            temp_stack += c
          if(check == 5):
            continue
        if self.is_on_table == False:
          self.create_table_view()
          self.is_on_table = True
        # update GUI players here
        for player in self.table.players:
          player_is_seated = False
          for player_gui in self.player_gui_list:
            #check if player is alreagy on GUI
            if player.player_id == player_gui.player_name:
              player_is_seated = True

          if player_is_seated == False:
            for player_gui in self.player_gui_list:
              if player_gui.seat_num == player.seat_number:
                player_gui.update_player_name(player.player_id)
                player_gui.update_player_stack(player.stack)
        
        
        
      if tokens[0] == "Decision:":
        temp_player_id = tokens[2]
        choice = tokens[3]

        if choice == 'bet':
          self.table_bet_status = 1
          # convert amount to int
          amount = int(tokens[4])
          # increment pot
          self.table.pot += amount
          self.lb_pot.config(text="${}".format(self.table.pot))
          for player in self.table.players:
            if player.player_id == temp_player_id:
              player.stack -= amount
              player.status = "in (money not owed)"
              for player_gui in self.player_gui_list:
                if player_gui.player_name == temp_player_id:
                  player_gui.lb_player_stack.config(text="${}".format(player.stack))
                  player_gui.lb_player_action.config(text="Bet ${}".format(amount))

          self.table.print_all_players()

        if choice == 'call':
          amount = int(tokens[4])
          self.table.pot += amount
          self.lb_pot.config(text="${}".format(self.table.pot))
          for player in self.table.players:
            if player.player_id == temp_player_id:
              player.stack -= amount
              player.status = "in (money not owed)"
          
          self.table.print_all_players()
        
        if choice == 'check':
          for player in self.table.players:
            if player.player_id == temp_player_id:
              player.status = "in (money not owed)"

          self.table.print_all_players()
        
        if choice == 'fold':
          for player in self.table.players:
            if player == temp_player_id:
              player.status = "out"

      if tokens[0] == "Flop:":
        self.table_bet_status = 0
        card1 = self.check_card_weight(tokens[1])
        card2 = self.check_card_weight(tokens[2])
        card3 = self.check_card_weight(tokens[3])
        self.img_community_card1.config(image=self.Images.card_images[card1])
        self.img_community_card2.config(image=self.Images.card_images[card2])
        self.img_community_card3.config(image=self.Images.card_images[card3])

      if tokens[0] == "Turn:":
        self.table_bet_status = 0
        card4 = self.check_card_weight(tokens[4]) 
        self.img_community_card4.config(image=self.Images.card_images[card4])

      if tokens[0] == "River:":
        self.table_bet_status = 0
        card5 = self.check_card_weight(tokens[5]) 
        self.img_community_card5.config(image=self.Images.card_images[card5])
        
  @staticmethod
  def check_card_weight(card):
    if len(card) == 2:
      value = card[0]
      suit = card[1]
    else:
      value = card[0]+card[1]
      suit = card[2]
    try:
      # deal with numerical card values
      k = int(value)
      return value+suit
    except:
      #deal with face cards
      face_card_weights = {
        'J':"11",
        'Q':"12",
        'K':"13",
        'A':"14"
      }
      value = face_card_weights[value]
      return value+suit

  def run_gui(self):
    while True:
      if self.gui_thread_check == True:
        self.gui.mainloop()

  def create_login_view(self):
    #log-in frame
    login_frame = Frame(self.top_frame, width=400, height=600, bg = "#35654d")
    login_frame.place(relx=0.5, rely=0.5, anchor="c")

    lbframe_app_name = LabelFrame(login_frame, bg="#35654d", relief="groove")
    lb_app_name = Label(lbframe_app_name, bg="#35654d", text="Poker App", font="Helvetica 32 bold")
    lb_username = Label(login_frame, bg="#35654d", text="Username:", font="Helvetica 16 bold")
    entry_username = Entry(login_frame, width=20)
    lb_password = Label(login_frame, bg="#35654d", text="Password:", font="Helvetica 16 bold")
    entry_password = Entry(login_frame, width=20, show='*')
    bttn_register = Button(login_frame, image=self.Images.register, borderwidth=0, bg="#35654d", activebackground="#35654d")
    bttn_log_in = Button(login_frame, image=self.Images.log_in, borderwidth=0, bg="#35654d", activebackground="#35654d", command=lambda:self.check_login(entry_username.get(), entry_password.get(), lb_error_alert))
    lb_error_alert = Label(login_frame, bg="#E69394", font="Helvetica 12 bold", fg="#8E282A")
    
    lbframe_app_name.grid(row=0, column=0, columnspan=2, pady=32)
    lb_app_name.pack(anchor="c", padx=10, pady=10)
    lb_username.grid(row=1, column=0, columnspan=2, pady=5)
    entry_username.grid(row=2, column=0, columnspan=2, pady=5)
    lb_password.grid(row=3, column=0, columnspan=2, pady=5)
    entry_password.grid(row=4, column=0, columnspan=2, pady=5)
    bttn_register.grid(row=5, column=0, padx=15, pady=15)
    bttn_log_in.grid(row=5, column=1, padx=15, pady=15)
    return login_frame
  
  @staticmethod
  def set_login_error(lb_error_alert, entry_type, error_type):

    if entry_type == "username":
      if error_type == 'length':
        error_text = "Username must be between 4 and 32 characters"
      if error_type == 'alphanumeric':
        error_text = "Username must be alphanumeric"

    if entry_type == "password":
      if error_type == 'length':
        error_text = "Password must be between 4 and 32 characters"
      if error_type == 'character':
        error_text = "Password must only use letters, numbers, and certain special characters"

    if entry_type == "authentication":
      error_text = "Wrong username or password."
      

    #set error label text and place on grid
    lb_error_alert.config(text = error_text)
    lb_error_alert.grid(row=6, column=0, columnspan=2, padx=15, pady=15, ipadx=3, ipady=3)
  
  @staticmethod
  def clear_frame(frame):
    for widget in frame.winfo_children():
      widget.destroy()

 
  @staticmethod
  def validate_username(username):

    # Validate username length
    len_username = len(username)
    if len_username < 4 or len_username > 32:
      return "length"

    # Validate username characters
    if not username.isalnum():
      return "alphanumeric"

    # Validated username
    else: 
      return "validated"
    
  @staticmethod
  def validate_password(password):

    # Validate password length
    len_password = len(password)
    if len_password < 4 or len_password > 32:
      return "length"
    
    # Validate password characters
    accepted_special_characters = ["@", "%", "+", "/", "'", "!", "#", "$", "^", "?", ":", ",", ")", "(", "{", "}", "[", "]", "`", "-", "_", "."]
    # Remove any accepted special characters from password
    temp_password = password
    for char in accepted_special_characters:
      temp_password = temp_password.replace(char, "")
    # Check if resulting password is alphanumeric
    if not temp_password.isalnum():
      return "character"
    
    # Validated password
    else:
      return "validated"
    
  def check_login(self,username, password, lb_error_alert):

    username_error = self.validate_username(username)
    if username_error == "validated":

      #Remove any previous error label due to username validation failure
      lb_error_alert.grid_forget()

      #Validate submitted password
      password_error = self.validate_password(password)
      if password_error == "validated":
        
        #Remove any previous error label due to password validation failure
        lb_error_alert.grid_forget()

        msg = "login {} {}".format(username, password)
        self.sendMsg(msg)

      # Password failed validation
      else:
        self.set_login_error(lb_error_alert, "password", password_error)

    # Username failed validation
    else:
      self.set_login_error(lb_error_alert, "username", username_error)
  
  def return_card_frame(self, parent, color):
    if color == "gray":
      #room frame background color (gray)
      bg = "#dad7cd"
    else:
      #table frame background color (felt green)
      bg = "#35654d"
    card_frame = LabelFrame(parent, bg=bg, width=50, height=68, borderwidth=2, relief="groove")
    return card_frame
  
  def set_buy_in_error(self, lb_buy_in_error, error_type):
    if error_type == "range":
      error_text = "Buy-in must be between 200 and 1000"
    if error_type == "not_int":
      error_text = "Buy-in must be an integer"

    lb_buy_in_error.config(text=error_text)
    lb_buy_in_error.pack(pady=10)

  @staticmethod
  def is_integer(num):

    try:
      int(num)
      return True
    
    except ValueError:
      return False

  def validate_buy_in(self, buy_in, lb_buy_in_error):
    #check if buy-in is an integer
    if self.is_integer(buy_in):

      buy_in = int(buy_in)

      if buy_in < 200 or buy_in > 1000:
        #buy_in is out of range
        self.set_buy_in_error(lb_buy_in_error, "range")

      else:
        #validation passed, send to server
        self.join_table(buy_in)

    #buy-in is not an integer
    else:
      self.set_buy_in_error(lb_buy_in_error, "not_int")

  def join_table(self, buy_in):
    self.sendMsg("join {}".format(buy_in))

  def create_dashboard_view(self, username, bankroll):
    
    self.clear_frame(self.top_frame)
    # self.top_frame = Frame(self.gui, width=1200, height=800)
    self.top_frame.config(width=1200, height=800, bg="#35654d")
    self.top_frame.pack(fill=tk.BOTH, expand=TRUE)

    left_frame = Frame(self.top_frame, width=600, height=800, bg="#35654d")
    right_frame = Frame(self.top_frame, width=600, height=800, bg="#35654d")
    left_frame.pack(fill=tk.BOTH, expand=TRUE, side=tk.LEFT)
    right_frame.pack(fill=tk.BOTH, expand=TRUE, side=tk.RIGHT)

    lb_username = Label(left_frame, bg="#35654d", text="Welcome {}".format(username), font="Helvetica 32 bold")
    lb_bankroll = Label(left_frame, bg="#35654d", text="Bankroll:  ${}".format(bankroll), font="Helvetica 32 bold")

    lb_buy_in = Label(right_frame, bg="#35654d", text="Buy-in:", font="Helvetica 16 bold")
    entry_buy_in = Entry(right_frame, width=20)
    bttn_join_table = Button(right_frame, bg="#35654d", borderwidth=0, activebackground="#35654d",image=self.Images.join_table, command=lambda:self.validate_buy_in(entry_buy_in.get(), lb_buy_in_error))
    lb_buy_in_error = Label(right_frame, bg="#E69394", font="Helvetica 12 bold", fg="#8E282A")
    
    lb_username.pack(anchor=tk.CENTER)
    lb_bankroll.pack(anchor=tk.CENTER)
    lb_buy_in.pack(anchor=tk.CENTER, pady=10)
    entry_buy_in.pack(anchor=tk.CENTER, pady=10)
    bttn_join_table.pack(anchor=tk.CENTER, pady=10)

  
  
  def create_table_view(self):
    self.clear_frame(self.top_frame)
    #window widgets
    self.top_frame.config(bg="")
    #room frame
    room_frame = Frame(self.top_frame, bg="#dad7cd", width=1200, height=600)
    room_frame.place(x=0, y=0, anchor="nw")

    #table frame
    table_frame = Canvas(room_frame, bg="#dad7cd", width=800, height=300, highlightthickness=0)
    table_frame.create_oval(0, 0, 800, 300, outline = "#65354d", fill = "#35654d",width = 2)
    table_frame.place(relx=0.5, rely=0.5, anchor="c")

    lb_img_pot = Label(table_frame, bg="#35654d", image=self.Images.pot)
    self.lb_pot = Label(table_frame, bg="#35654d", text="$0", font="Helvetica 16 bold")

    lb_img_pot.place(x=400, y=80, anchor="c")
    self.lb_pot.place(x=400, y=120, anchor="c")

    #Display community cards
    community_cards_frame = Frame(table_frame, bg="#35654d", width=300, height=72)
    community_cards_frame.place(x=400, y=185, anchor="c")

    lbframe_community_card1 = self.return_card_frame(community_cards_frame, "green")
    lbframe_community_card2 = self.return_card_frame(community_cards_frame, "green")
    lbframe_community_card3 = self.return_card_frame(community_cards_frame, "green")
    lbframe_community_card4 = self.return_card_frame(community_cards_frame, "green")
    lbframe_community_card5 = self.return_card_frame(community_cards_frame, "green")

    lbframe_community_card1.grid(row=0, column=0)
    lbframe_community_card2.grid(row=0, column=1)
    lbframe_community_card3.grid(row=0, column=2)
    lbframe_community_card4.grid(row=0, column=3)
    lbframe_community_card5.grid(row=0, column=4)

    self.img_community_card1 = Label(lbframe_community_card1, bg="#35654d", image=self.Images.card_back)
    self.img_community_card2 = Label(lbframe_community_card2, bg="#35654d", image=self.Images.card_back)
    self.img_community_card3 = Label(lbframe_community_card3, bg="#35654d", image=self.Images.card_back)
    self.img_community_card4 = Label(lbframe_community_card4, bg="#35654d", image=self.Images.card_back)
    self.img_community_card5 = Label(lbframe_community_card5, bg="#35654d", image=self.Images.card_back)

    self.img_community_card1.pack()
    self.img_community_card2.pack()
    self.img_community_card3.pack()
    self.img_community_card4.pack()
    self.img_community_card5.pack()

    #Coordinates of each player frame
    coord_list = [(548, 458, 1), (268, 438, 2), (48, 258, 3), (190, 40, 4), (428, 6, 5), (668, 6, 6), (906, 40, 7), (1048, 258, 8), (828, 438, 9)] 

    #Loop to create frame for each player
    for x, y, z in coord_list:
      self.player_gui_list.append(PlayerGUI(room_frame, x, y, self.Images.chips, self.Images.card_back, self.Images.buy_in, z, "Empty Seat", 0))
    
    #Chat frame
    chat_frame = Frame(self.top_frame, bg="#ffffff", width=796, height=196)
    chat_frame.place(x=2, y=798, anchor="sw")

    #Frame for action buttons
    action_frame = Frame(self.top_frame, width=396, height=196)
    action_frame.place(x=1198, y=798, anchor="se")

    # is_player_turn = False
    # #if player's turn allow action buttons
    # if is_player_turn:
    #   action_status = NORMAL
    # #else disable action buttons
    # else:
    #   action_status = DISABLED

    self.bttn_action1 = Button(action_frame, image=self.Images.fold, borderwidth=0, state=DISABLED)

    #if no bets yet: show check/bet buttons
    if self.table_bet_status == 0:
      action_2 = self.Images.check
      action_3 = self.Images.bet
    #if one bet on table: raise instead of bet button
    if self.table_bet_status == 1:
      action_2 = self.Images.call
      action_3 = self.Images.raise_img

    self.bttn_action2 = Button(action_frame, image=action_2, borderwidth=0, state=DISABLED)
    self.bttn_action3 = Button(action_frame, image=action_3, borderwidth=0, state=DISABLED)
    # Bet/Raise/Re-raise amount Entry box
    #ADD validation, dynamic min/max values
    self.entry_bet_amount = Entry(action_frame, width=6)
    bet_min = 1
    bet_max = 200
    self.entry_bet_amount.insert(0, str(bet_min))
    # bet_range = "$" + str(bet_min) + "-" + "$" + str(bet_max)
    # lb_bet_range = Label(action_frame, text=bet_range, font="Helvetica 10 bold")

    player_is_seated = True
    #if player is seated: show cash out button
    if player_is_seated == True:
      action_4 = self.Images.cash_out
    #else player is not seated: show leave table button
    else:
      action_4 = self.Images.leave_table
    bttn_action4 = Button(action_frame, image=action_4, borderwidth=0)

    self.bttn_action1.place(x=100, y=25, anchor="n")
    self.bttn_action2.place(x=200, y=25, anchor="n")
    self.bttn_action3.place(x=300, y=25, anchor="n")
    bttn_action4.place(x=200, y=171, anchor="s")
    self.entry_bet_amount.place(x=300, y=70, anchor="n")
    # lb_bet_range.place(x=300, y= 100, anchor="n")

    bttn_start_game = Button(chat_frame, image=self.Images.start_game, borderwidth=0, command=lambda:self.start_game())
    bttn_start_game.pack()

  def start_game(self):
    self.sendMsg("start")

  def decision_fold(self):
    self.sendMsg("decision fold")
    self.bttn_action1.config(state=DISABLED)
    self.bttn_action2.config(state=DISABLED)
    self.bttn_action3.config(state=DISABLED)

  def decision_check(self):
    self.sendMsg("decision check")
    self.bttn_action1.config(state=DISABLED)
    self.bttn_action2.config(state=DISABLED)
    self.bttn_action3.config(state=DISABLED)

  def decision_bet(self, bet_amount):
    self.sendMsg("decision bet {}".format(bet_amount))
    self.bttn_action1.config(state=DISABLED)
    self.bttn_action2.config(state=DISABLED)
    self.bttn_action3.config(state=DISABLED)
  
  def decision_call(self):
    self.sendMsg("decision call")
    self.bttn_action1.config(state=DISABLED)
    self.bttn_action2.config(state=DISABLED)
    self.bttn_action3.config(state=DISABLED)