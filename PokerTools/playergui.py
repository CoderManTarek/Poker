from tkinter import *
import tkinter as tk

def return_card_frame(parent, color):
  if color == "gray":
    #room frame background color (gray)
    bg = "#dad7cd"
  else:
    #table frame background color (felt green)
    bg = "#35654d"
  card_frame = LabelFrame(parent, bg=bg, width=50, height=68, borderwidth=2, relief="groove")
  return card_frame

class PlayerGUI:
  def __init__(self, room_frame, x, y, img_chips, img_card_back, img_buy_in, seat_num, player_name, player_stack):
    #frame for each player
    player_frame = Frame(room_frame, bg="#dad7cd", width=104, height=140)
    player_frame.place(x=x, y=y)

    card_one_frame = return_card_frame(player_frame, "gray")
    card_two_frame = return_card_frame(player_frame, "gray")
    
    card_one_frame.grid(row=0,column=0)
    card_two_frame.grid(row=0,column=1)

    lb_img_chips = Label(player_frame, bg="#dad7cd", image=img_chips)
    lb_img_chips.grid(row=2, column=0)

    self.seat_num = seat_num
    self.player_name = player_name
    self.player_stack = player_stack

    #player frame widgets
    #if player is seated, display player info
    #ADD if player is seated AND seat is empty, display empty seat
    # player_is_seated = True
    # if player_is_seated == True:
    self.lb_img_card_one = Label(card_one_frame, bg="#dad7cd", image=img_card_back)
    self.lb_img_card_two = Label(card_two_frame, bg="#dad7cd", image=img_card_back)
    self.lb_player_name = Label(player_frame, bg="#dad7cd", text="Empty", font="Helvetica 10 bold")
    self.lb_player_stack = Label(player_frame, bg="#dad7cd", text="$", font="Helvetica 10 bold")
    self.lb_player_action = Label(player_frame, bg="#dad7cd", text="Action", font="Helvetica 10 bold")

    self.lb_player_name.grid(row=1, column=0, columnspan=2)
    self.lb_player_stack.grid(row=2, column=1)
    self.lb_player_action.grid(row=3, column=1)

    self.lb_img_card_one.pack()
    self.lb_img_card_two.pack()
    # else:
    #   #player is not seated, allow buy-in
    #   bttn_buy_in = Button(player_frame, image=img_buy_in, borderwidth=0, bg="#505b62", activebackground="#505b62")
    #   entry_buy_in = Entry(player_frame, width=6, bg="#505b62")
    #   buy_in_min = 10
    #   entry_buy_in.insert(0, str(buy_in_min))
    #   #ADD validation and dynamic value if player bank < max buyin, buy_in_max = bank 
    #   buy_in_max = 200
    #   buy_in_range = "$" + str(buy_in_min) + "-" + "$" + str(buy_in_max)
    #   lb_buy_in_range = Label(player_frame, bg="#505b62", text=buy_in_range, font="Helvetica 10 bold")
      
    #   bttn_buy_in.grid(row=1, column=0, columnspan=2)
    #   entry_buy_in.grid(row=2, column=1)
    #   lb_buy_in_range.grid(row=3, column=1)
    lb_player_seat = Label(player_frame, bg="#dad7cd", text="Seat {}".format(seat_num))
    lb_player_seat.grid(row=3, column=0)

  def update_player_name(self, new_name):
    self.player_name = new_name
    self.lb_player_name.config(text = new_name)

  def update_player_stack(self, new_stack):
    self.player_stack = new_stack
    self.lb_player_stack.config(text = "${}".format(new_stack))

  def update_img_card(self, img_card1, img_card2):
    self.lb_img_card_one.config(image = img_card1)
    self.lb_img_card_two.config(image = img_card2)