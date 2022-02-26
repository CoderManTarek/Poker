from tkinter import *

gui = Tk()
gui.title("Poker App")
gui.config(bg="#D3D3D3")
gui.geometry("1200x800")
gui.resizable(False, False)
#widgets
#room frame
room_frame = Frame(gui, bg="#505b62", width=1200, height=600)
room_frame.pack(padx=5, pady=5)
#table frame
table_frame = Frame(room_frame, bg="#35654d", width=800, height=300)
table_frame.place(x=200,y=150)
# #35654d poker green


gui.mainloop()