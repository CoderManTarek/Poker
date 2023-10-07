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

def initialize_card_images():
  card_images = {}
  suits = ("h", "d", "c", "s")
  for suit in suits:
    for n in range(1,14):
      card_name = suit+str(n)
      file_string = "img/cards/" + card_name + ".png"
      card_images[card_name] = PhotoImage(file=file_string)
  return card_images

class Client:

  # instantiate socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  def sendMsg(self, msg):
      self.sock.send(bytes(msg, 'utf-8'))

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

      # format message
      formattedMessage = ""
      x = 0
      for i in tokens:
        if(x!=0 and x!=1):
          formattedMessage+=i+' '
        x+=1
      if tokens[0] == 'Win:':
        self.table.print_all_players()

      if(tokens[0] == "Action:"):
        for player in self.table.players:
          #find player whos turn it is
          if(int(tokens[1]) == player.seat_number):       
            # is that player on this client
            if(player.player_id == self.this_player):  
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
      # for player in players:
      #   if player not in self.table.players:
      #     print("hello")
      #     self.table.players.append(player)
    
        
        
      if tokens[0] == "Decision:":
        temp_player_id = tokens[2]
        choice = tokens[3]

        if choice == 'bet':
          # convert amount to int
          amount = int(tokens[4])
          # increment pot
          self.table.pot += amount
          for player in self.table.players:
            if player.player_id == temp_player_id:
              player.stack -= amount
              player.status = "in (money not owed)"

          self.table.print_all_players()

        if choice == 'call':
          amount = int(tokens[4])
          self.table.pot += amount
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

  def run_gui(self):
    while True:
      if self.gui_thread_check == True:
        self.gui.mainloop()

  def login(self, username, password):
    msg = "login {} {}".format(username, password)
    self.sendMsg(msg)

  def create_login_view(self):
    #log-in frame
    login_frame = Frame(self.top_frame, width=400, height=600, bg = "#35654d")
    login_frame.place(relx=0.5, rely=0.5, anchor="c")

    lbframe_app_name = LabelFrame(login_frame, bg="#35654d", relief="groove")
    lb_app_name = Label(lbframe_app_name, bg="#35654d", text="Poker App", font="Helvetica 32 bold")
    lb_username = Label(login_frame, bg="#35654d", text="Username:", font="Helvetica 16 bold")
    #ADD validation
    entry_username = Entry(login_frame, width=20)
    lb_password = Label(login_frame, bg="#35654d", text="Password:", font="Helvetica 16 bold")
    entry_password = Entry(login_frame, width=20)
    bttn_register = Button(login_frame, image=self.Images.register, borderwidth=0, bg="#35654d", activebackground="#35654d")
    bttn_log_in = Button(login_frame, image=self.Images.log_in, borderwidth=0, bg="#35654d", activebackground="#35654d", command=lambda:self.login(entry_username.get(), entry_password.get()))
    lb_error_alert = Label(login_frame, bg="#E69394", font="Helvetica 12 bold", fg="#8E282A")
    
    lbframe_app_name.grid(row=0, column=0, columnspan=2, pady=32)
    lb_app_name.pack(anchor="c", padx=10, pady=10)
    lb_username.grid(row=1, column=0, columnspan=2, pady=5)
    entry_username.grid(row=2, column=0, columnspan=2, pady=5)
    lb_password.grid(row=3, column=0, columnspan=2, pady=5)
    entry_password.grid(row=4, column=0, columnspan=2, pady=5)
    bttn_register.grid(row=5, column=0, padx=15, pady=15)
    bttn_log_in.grid(row=5, column=1, padx=15, pady=15)

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
    self.Images.card_images = initialize_card_images()
    self.create_login_view()


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
