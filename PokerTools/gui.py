from tkinter import *
import tkinter as tk
from PokerTools.assets import Assets
#import psycopg2
from configparser import ConfigParser
import hashlib
from PokerTools.playergui import PlayerGUI

def return_card_frame(parent, color):
  if color == "gray":
    #room frame background color (gray)
    bg = "#505b62"
  else:
    #table frame background color (felt green)
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
  gui.iconbitmap("../img/app_icon.ico")

  top_frame = Frame(gui, width=1200, height=800)
  top_frame.pack()

  #initialize images
  Images = Assets()
  Images.register = PhotoImage(file="../img/register.png")
  Images.log_in = PhotoImage(file="../img/log_in.png")
  Images.join_table = PhotoImage(file="../img/join_table.png")
  Images.leave_table = PhotoImage(file="../img/leave_table.png")
  Images.buy_in = PhotoImage(file="../img/buy_in.png")
  Images.cash_out = PhotoImage(file="../img/cash_out.png")
  Images.chips = PhotoImage(file="../img/chips.png")
  Images.pot = PhotoImage(file="../img/pot.png")
  Images.card_back = PhotoImage(file="../img/card_back.png")
  Images.fold = PhotoImage(file="../img/fold.png")
  Images.check = PhotoImage(file="../img/check.png")
  Images.call = PhotoImage(file="../img/call.png")
  Images.bet = PhotoImage(file="../img/bet.png")
  Images.raise_img = PhotoImage(file="../img/raise.png")
  Images.reraise= PhotoImage(file="../img/re-raise.png")
  Images.card_images = initialize_card_images()
  
  top_frame.config(bg = "#35654d")

  #log-in frame
  login_frame = Frame(top_frame, width=400, height=600, bg = "#35654d")
  login_frame.place(relx=0.5, rely=0.5, anchor="c")

  lbframe_app_name = LabelFrame(login_frame, bg="#35654d", relief="groove")
  lb_app_name = Label(lbframe_app_name, bg="#35654d", text="Poker App", font="Helvetica 32 bold")
  lb_username = Label(login_frame, bg="#35654d", text="Username:", font="Helvetica 16 bold")
  #ADD validation
  entry_username = Entry(login_frame, width=20)
  lb_password = Label(login_frame, bg="#35654d", text="Password:", font="Helvetica 16 bold")
  entry_password = Entry(login_frame, width=20)
  bttn_register = Button(login_frame, image=Images.register, borderwidth=0, bg="#35654d", activebackground="#35654d")
  bttn_log_in = Button(login_frame, image=Images.log_in, borderwidth=0, bg="#35654d", activebackground="#35654d", command=lambda:check_login(entry_username.get(), entry_password.get(), top_frame, lb_error_alert, Images))
  lb_error_alert = Label(login_frame, bg="#E69394", font="Helvetica 12 bold", fg="#8E282A")
  
  lbframe_app_name.grid(row=0, column=0, columnspan=2, pady=32)
  lb_app_name.pack(anchor="c", padx=10, pady=10)
  lb_username.grid(row=1, column=0, columnspan=2, pady=5)
  entry_username.grid(row=2, column=0, columnspan=2, pady=5)
  lb_password.grid(row=3, column=0, columnspan=2, pady=5)
  entry_password.grid(row=4, column=0, columnspan=2, pady=5)
  bttn_register.grid(row=5, column=0, padx=15, pady=15)
  bttn_log_in.grid(row=5, column=1, padx=15, pady=15)

  gui.mainloop()

def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db

def validate_password(password):

  # Validate password length
  len_password = len(password)
  if len_password < 8 or len_password > 32:
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

def authenticate_password(username, password):

  # Retrieve stored key and salt from database
  login_info = retrieve_login_info(username)

  # If None returned, there is no user with that username in the database
  if login_info == None:
    return "nouser"

  key, salt = login_info
  key = bytes(key)

  # Generate new key based on submitted password
  new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)

  if new_key == key:
    return "authenticated"
  else:
    return "wrong"

def set_login_error(lb_error_alert, entry_type, error_type):

  if entry_type == "username":
    if error_type == 'length':
      error_text = "Username must be between 4 and 32 characters"
    if error_type == 'alphanumeric':
      error_text = "Username must be alphanumeric"

  if entry_type == "password":
    if error_type == 'length':
      error_text = "Password must be between 8 and 32 characters"
    if error_type == 'character':
      error_text = "Password must only use letters, numbers, and certain special characters"

  if entry_type == "authentication":
    if error_type == "nouser":
      error_text = "There is no user with that username"
    if error_type == "wrong":
      error_text = "Incorrect password"

  #set error label text and place on grid
  lb_error_alert.config(text = error_text)
  lb_error_alert.grid(row=6, column=0, columnspan=2, padx=15, pady=15, ipadx=3, ipady=3)


def create_table_view(top_frame, Images):
  clear_frame(top_frame)
   #window widgets
  top_frame.config(bg="")
  #room frame
  room_frame = Frame(top_frame, bg="#505b62", width=1200, height=600)
  room_frame.place(x=0, y=0, anchor="nw")

  #table frame
  table_frame = Canvas(room_frame, bg="#505b62", width=800, height=300, highlightthickness=0)
  table_frame.create_oval(0, 0, 800, 300, outline = "#65354d", fill = "#35654d",width = 2)
  table_frame.place(relx=0.5, rely=0.5, anchor="c")

  lb_img_pot = Label(table_frame, bg="#35654d", image=Images.pot)
  lb_pot = Label(table_frame, bg="#35654d", text="$1000", font="Helvetica 16 bold")

  lb_img_pot.place(x=400, y=80, anchor="c")
  lb_pot.place(x=400, y=120, anchor="c")

  #Display community cards
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

  img_community_card1 = Label(lbframe_community_card1, bg="#35654d", image=Images.card_images["3d"])
  img_community_card2 = Label(lbframe_community_card2, bg="#35654d", image=Images.card_images["13h"])
  img_community_card3 = Label(lbframe_community_card3, bg="#35654d", image=Images.card_images["1s"])
  img_community_card4 = Label(lbframe_community_card4, bg="#35654d", image=Images.card_images["6s"])
  img_community_card5 = Label(lbframe_community_card5, bg="#35654d", image=Images.card_images["11c"])

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
    player_gui_list.append(PlayerGUI(room_frame, x, y, Images.chips, Images.card_back, Images.buy_in))
  
  #Chat frame
  chat_frame = Frame(top_frame, bg="#ffffff", width=796, height=196)
  chat_frame.place(x=2, y=798, anchor="sw")

  #Frame for action buttons
  action_frame = Frame(top_frame, width=396, height=196)
  action_frame.place(x=1198, y=798, anchor="se")

  is_player_turn = False
  #if player's turn allow action buttons
  if is_player_turn:
    action_status = NORMAL
  #else disable action buttons
  else:
    action_status = DISABLED

  bttn_action1 = Button(action_frame, image=Images.fold, borderwidth=0, state=action_status)

  table_bet_status = 0
  #if no bets yet: show check/bet buttons
  if table_bet_status == 0:
    action_2 = Images.check
    action_3 = Images.bet
  #if one bet on table: raise instead of bet button
  if table_bet_status == 1:
    action_2 = Images.call
    action_3 = Images.raise_img
  #if someone has raised: re-raise button instead of raise
  if table_bet_status == 2:
    action_2 = Images.call
    action_3 = Images.reraise

  bttn_action2 = Button(action_frame, image=action_2, borderwidth=0, state=action_status)
  bttn_action3 = Button(action_frame, image=action_3, borderwidth=0, state=action_status)
  # Bet/Raise/Re-raise amount Entry box
  #ADD validation, dynamic min/max values
  entry_bet_amount = Entry(action_frame, width=6)
  bet_min = 2
  bet_max = 200
  entry_bet_amount.insert(0, str(bet_min))
  bet_range = "$" + str(bet_min) + "-" + "$" + str(bet_max)
  lb_bet_range = Label(action_frame, text=bet_range, font="Helvetica 10 bold")

  player_is_seated = True
  #if player is seated: show cash out button
  if player_is_seated == True:
    action_4 = Images.cash_out
  #else player is not seated: show leave table button
  else:
    action_4 = Images.leave_table
  bttn_action4 = Button(action_frame, image=action_4, borderwidth=0)

  bttn_action1.place(x=100, y=25, anchor="n")
  bttn_action2.place(x=200, y=25, anchor="n")
  bttn_action3.place(x=300, y=25, anchor="n")
  bttn_action4.place(x=200, y=171, anchor="s")
  entry_bet_amount.place(x=300, y=70, anchor="n")
  lb_bet_range.place(x=300, y= 100, anchor="n")


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


def create_dashboard_view(top_frame, Images):
  clear_frame(top_frame)
  top_frame.config(bg="#ffffff")
  #Label(top_frame, bg="#35654d", text="Poker App", font="Helvetica 32 bold").pack()
  bttn_join_table = Button(top_frame, image=Images.join_table, command=lambda:create_table_view(top_frame, Images))
  bttn_join_table.place(relx=0.5, rely=0.5, anchor="c")

def clear_frame(frame):
  for widget in frame.winfo_children():
    widget.destroy()

def check_login(username, password, top_frame, lb_error_alert, Images):

  username_error = validate_username(username)
  if username_error == "validated":

    #Remove any previous error label due to username validation failure
    lb_error_alert.grid_forget()

    #Validate submitted password
    password_error = validate_password(password)
    if password_error == "validated":
      
      #Remove any previous error label due to password validation failure
      lb_error_alert.grid_forget()

      authentication_error = authenticate_password(username, password)
      if authentication_error == "authenticated":
        create_dashboard_view(top_frame, Images)
      
      # Authentication failed
      else:
        set_login_error(lb_error_alert, "authentication", authentication_error)

    # Password failed validation
    else:
      set_login_error(lb_error_alert, "password", password_error)

  # Username failed validation
  else:
    set_login_error(lb_error_alert, "username", username_error)

def retrieve_login_info(username):
  conn = None
  try:
        params = config()
        conn = psycopg2.connect(**params)

        cur = conn.cursor()

        sql = '''SELECT password_key, password_salt
	            FROM public.users WHERE LOWER(username)=LOWER(%s);'''

        cur.execute(sql, (username,))
        login_info = cur.fetchone()

        conn.close()

        return login_info
        
  except (Exception, psycopg2.DatabaseError) as error:
      print(error)
  finally:
      if conn is not None:
          conn.close()

def initialize_card_images():
  card_images = {}
  suits = ("h", "d", "c", "s")
  for suit in suits:
    for n in range(1,14):
      card_name = suit+str(n)
      file_string = "../img/cards/" + card_name + ".png"
      card_images[card_name] = PhotoImage(file=file_string)
  return card_images

class GUI:
  def __init__(self):
     #GUI window
    self.gui = Tk()
    self.canvas = Canvas()
    self.gui.title("Poker App")
    self.gui.config(bg="#D3D3D3")
    self.gui.geometry("1200x800")
    self.gui.resizable(False, False)
    self.gui.iconbitmap("../img/app_icon.ico")
    self.top_frame = Frame(self.gui, width=1200, height=800)
    self.top_frame.pack()
    self.top_frame.config(bg = "#35654d")
     #initialize images
    self.Images = Assets()
    self.Images.register = PhotoImage(file="../img/register.png")
    self.Images.log_in = PhotoImage(file="../img/log_in.png")
    self.Images.join_table = PhotoImage(file="../img/join_table.png")
    self.Images.leave_table = PhotoImage(file="../img/leave_table.png")
    self.Images.buy_in = PhotoImage(file="../img/buy_in.png")
    self.Images.cash_out = PhotoImage(file="../img/cash_out.png")
    self.Images.chips = PhotoImage(file="../img/chips.png")
    self.Images.pot = PhotoImage(file="../img/pot.png")
    self.Images.card_back = PhotoImage(file="../img/card_back.png")
    self.Images.fold = PhotoImage(file="../img/fold.png")
    self.Images.check = PhotoImage(file="../img/check.png")
    self.Images.call = PhotoImage(file="../img/call.png")
    self.Images.bet = PhotoImage(file="../img/bet.png")
    self.Images.raise_img = PhotoImage(file="../img/raise.png")
    self.Images.reraise= PhotoImage(file="../img/re-raise.png")
    self.Images.card_images = initialize_card_images()

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
    bttn_log_in = Button(login_frame, image=self.Images.log_in, borderwidth=0, bg="#35654d", activebackground="#35654d", command=lambda:check_login(entry_username.get(), entry_password.get(), self.top_frame, lb_error_alert, self.Images))
    lb_error_alert = Label(login_frame, bg="#E69394", font="Helvetica 12 bold", fg="#8E282A")
    
    lbframe_app_name.grid(row=0, column=0, columnspan=2, pady=32)
    lb_app_name.pack(anchor="c", padx=10, pady=10)
    lb_username.grid(row=1, column=0, columnspan=2, pady=5)
    entry_username.grid(row=2, column=0, columnspan=2, pady=5)
    lb_password.grid(row=3, column=0, columnspan=2, pady=5)
    entry_password.grid(row=4, column=0, columnspan=2, pady=5)
    bttn_register.grid(row=5, column=0, padx=15, pady=15)
    bttn_log_in.grid(row=5, column=1, padx=15, pady=15)