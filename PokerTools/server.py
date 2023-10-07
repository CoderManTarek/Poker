import socket
from PokerTools.deck import Deck
from PokerTools.servertable import ServerTable
import random
import threading
from PokerTools.player import Player

class Server:
  
  # server program data
  usernames_passwords_bankrolls = []
  activePlayersAndAddresses = []
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  connections = []
  table_players = [] # list of tuples (ip, port)

  def __init__(self):

    #load user file data into server program data upon initialization
    file = open("users.txt", "r")
    fileData = file.readlines()
    file.close()
    check = 0
    tempUser = ''
    tempPassword = ''
    tempBankroll = ''

    #parsing and formatting logic to store file data
    for string in fileData:
      for character in string:
        if(character == ')'):
          check = 0
          break
        if(character == ' ' and check == 2):
          check = 3
          continue
        if(character == ' '):
          check = 2
          continue
        if(character == ','):
          continue
        if(check == 1):
          tempUser += character
        if(check == 2):
          tempPassword += character
        if(check == 3):
          tempBankroll += character
        if(character == '('):
          check = 1
      self.usernames_passwords_bankrolls.append((tempUser, tempPassword, int(tempBankroll)))
      tempUser = ''
      tempPassword = ''
      tempBankroll = ''

    # build table
    self.players = []
    self.deck = Deck()
    self.table = ServerTable(self.deck, self.connections, 9, self.players)
    self.started = False

    # table.deal()

    # bind server to host and port for listening
    self.sock.bind(('localhost', 19447))
    self.sock.listen(1)

  # how connections will be handeled based on data recieved by server from connection
  # user command function implementations will be marked with #############<function>#############
  def handler(self, c,a):
    while True:
      try:
        # recieve data
        data = c.recv(1024)
      except:
        # close connection
        print(str(a[0])+ ':' + str(a[1]) +  " disconnected")
        self.connections.remove(c)
        c.close()
        break
      if not data:
        # close connection
        print(str(a[0])+ ':' + str(a[1]) +  " disconnected")
        self.connections.remove(c)
        c.close()
        break
 
      #tokenize message recieved by server
      message = str(data, 'utf-8')
      print(message)
      tokens = message.split(' ')

      # format message
      formattedMessage = ""
      x = 0
      for i in tokens:
        if(x!=0 and x!=1):
          formattedMessage+=i+' '
        x+=1




      #############if we are logging out#############
      userlogincheck = False
      if(tokens[0]=="logout"):

        #is this account logged in
        for j in self.activePlayersAndAddresses:
          if(j[1]==str(a[0])):
            if(j[2]==a[1]):
              userlogincheck=True
              print(j[0]+" logout.")

              #respond to all clients with logout message
              for connection in self.connections:
                connection.send(bytes((j[0]+" left"), 'utf-8'))
              self.activePlayersAndAddresses.remove(j)
        if(userlogincheck == False):
          print("You are not logged in")



      #############if we are creating a new User#############
      checkuserlogin = False
      lengthCheck = False
      tokencheck = False
      if(tokens[0] == "newuser"):
        checker = 0

        #check if sender is logged in
        for connectioniterator in self.activePlayersAndAddresses:
          if(connectioniterator[1] == str(a[0])):
            if(connectioniterator[2] == a[1]):
              checkuserlogin=True
              break

        #check if tokens include all parameters
        if(len(tokens)>=3):
          tokencheck = True


        #check to see if all necessary tokens have been inputted    
        if(tokencheck == True):

          # if this username is not already in use in the usernames and passwords list of tuples
          for userAndPass in self.usernames_passwords_bankrolls:
            if(userAndPass[0] == tokens[1]):
              checker = 1

          #check username and password length
          if(len(tokens[1])>=3 and len(tokens[1])<=32 and len(tokens[2])>=4 and len(tokens[2])<=8):
            lengthCheck = True

        if(checker == 0 and checkuserlogin==False and lengthCheck == True):

          # add user to usernames and passwords list of tuples
          if(len(tokens) > 2):
            newUsername = tokens[1]
            newPassword = tokens[2]
            self.usernames_passwords_bankrolls.append((newUsername, newPassword, 10000))
            file = open("users.txt", "a")
            file.write('\n'+'('+newUsername+','+' ' + newPassword + ','+' '+ '10000'+')')
            file.close()

            # find client that sent this packet and respond 
            for connection in self.connections:
              if(connection.getpeername()[0] == str(a[0])):
                if(connection.getpeername()[1] == a[1]):
                    connection.send(bytes("New user account created. Please login.", 'utf-8'))
                    print("New user account created.")

          else:
            print("must enter username and password to create a new user account")
        if(checkuserlogin == True):
          print("you must logout before creating a new account")
        if(checker == 1):
          # find client that sent this packet and respond 
          for connection in self.connections:
            if(connection.getpeername()[0] == str(a[0])):
              if(connection.getpeername()[1] == a[1]):
                  connection.send(bytes("Denied. User account already exists.", 'utf-8'))
        if(lengthCheck== False):
          # find client that sent this packet and respond 
          for connection in self.connections:
            if(connection.getpeername()[0] == str(a[0])):
              if(connection.getpeername()[1] == a[1]):
                  connection.send(bytes("Denied. Username must be 3-32 characters. Password must be 4-8 characters.", 'utf-8'))
        

      #############if we are logging in#############
      checklogin = False
      loginchecker = False
      tokenschecker = False
      if(tokens[0] == "login"):

        #check if user inputted a password
        if(len(tokens)>= 3):
          tokenschecker=True

        if(tokenschecker==True):
          #check if sender is logged in
          for connectioniterator in self.activePlayersAndAddresses:
            #print(connectioniterator[1],str(a[0]),connectioniterator[2],a[1])
            if(connectioniterator[0]==tokens[1]):
              checklogin = True
              break
            if(connectioniterator[1] == str(a[0])):
              if(connectioniterator[2] == a[1]):
                checklogin=True
                break

        #login
        for users in self.usernames_passwords_bankrolls:
          if(checklogin==True or tokenschecker==False):
            break
          if(tokens[1] == users[0]):
            if(tokens[2] == users[1]):
              self.activePlayersAndAddresses.append((tokens[1], str(a[0]), a[1]))
              
              # find client that sent this packet and respond 
              for connection in self.connections:
                if(connection.getpeername()[0] == str(a[0])):
                  if(connection.getpeername()[1] == a[1]):
                      connection.send(bytes("login confirmed", 'utf-8'))
                      print(tokens[1]+" login")
                      loginchecker = True
                      break
              break
        if(checklogin==True):
          pass
          #print("you are already logged in")
        if(checklogin==False and loginchecker == False):
          # find client that sent this packet and respond 
          for connection in self.connections:
            if(connection.getpeername()[0] == str(a[0])):
              if(connection.getpeername()[1] == a[1]):
                  connection.send(bytes("Denied. User name or password incorrect.", 'utf-8'))


      #############if we are sending to all users#############
      loggedIn=False
      lengthchecker= False
      if(tokens[0] == "send"):

        #check if sender is logged in
        for connectioniterator in self.activePlayersAndAddresses:
          if(connectioniterator[1] == str(a[0])):
            if(connectioniterator[2] == a[1]):
              senderName = connectioniterator[0]
              loggedIn=True

              # check to see if message length is 1-256 characters
              if((len(formattedMessage)-1)>=1 and (len(formattedMessage)-1)<=256):
                lengthchecker = True
                
                if(tokens[1] == "all"):
                  # send to all users that are logged in
                  print(senderName + ": " + formattedMessage)
                  for connection in self.connections:
                    for x in self.activePlayersAndAddresses:
                      if(x[1]==connection.getpeername()[0]):
                        if(x[2]==connection.getpeername()[1]):              
                          connection.send(bytes((senderName + ": " + formattedMessage), 'utf-8'))
                else:
                  #check to see if user is online
                  for tmp in self.activePlayersAndAddresses:
                    if(tokens[1]==tmp[0]):

                      #send direct message to specified user
                      for connection in self.connections:

                        #find user's address and port
                        if(tmp[1] == connection.getpeername()[0] and tmp[2] == connection.getpeername()[1]):

                          #send message
                          connection.send(bytes((senderName + ": " + formattedMessage), 'utf-8'))
                          print(senderName+" (to " + tokens[1] + "):" + formattedMessage)



        #if user is not logged in
        if(loggedIn==False):

          # find client that sent this packet and respond 
          for connection in self.connections:
            if(connection.getpeername()[0] == str(a[0])):
              if(connection.getpeername()[1] == a[1]):
                  connection.send(bytes("Denied. Please login first.", 'utf-8'))
        
        # if the message is too short or to long
        elif(lengthchecker == False):

           # find client that sent this packet and respond 
          for connection in self.connections:
            if(connection.getpeername()[0] == str(a[0])):
              if(connection.getpeername()[1] == a[1]):
                  connection.send(bytes("Denied. Message must be between 1-256 characters.", 'utf-8'))



      #############if we are viewing the list of active users#############
      loggedIn=False
      serverList = ""
      if(tokens[0] == "who"):

        #check if sender is logged in
        for connectioniterator in self.activePlayersAndAddresses:
          if(connectioniterator[1] == str(a[0])):
            if(connectioniterator[2] == a[1]):
              loggedIn=True
              for temp in self.activePlayersAndAddresses:
                serverList+=temp[0] + ", "
              # find client that sent this packet and respond 
              for connection in self.connections:
                if(connection.getpeername()[0] == str(a[0])):
                  if(connection.getpeername()[1] == a[1]):
                      connection.send(bytes(serverList[:-2], 'utf-8'))
      
      #############if a player makes a decision#############
      if(tokens[0]=='decision'):
        pass
        loggedIn=False
        #check if sender is logged in
        for connectioniterator in self.activePlayersAndAddresses:
          if(connectioniterator[1] == str(a[0])):
            if(connectioniterator[2] == a[1]):
              loggedIn=True
        if(loggedIn == True):
          # check if sender belongs to table
          onTable = False
          for player in self.table_players:
            if(player[0] == str(a[0]) and player[1] == str(a[1])):
              onTable = True
              id = player[2]

        if(loggedIn == True and onTable == True):
          # check if sender has action
          for player in self.table.players:
            if(player.player_id == id):
              if(player.action == True):
                choice = tokens[1]
                if choice == 'bet':
                  amount = int(tokens[2])
                  self.table.process_decision(id, choice, amount)
                  self.table.print_table()
                  self.table.iterate_action()
                if choice == 'call':
                  amount = player.owed - player.money_out
                  self.table.process_decision(id, choice, amount)
                  self.table.print_table()
                  self.table.iterate_action()
                  
                if choice == 'check':
                  self.table.iterate_action()
                  self.table.process_decision(id, choice)
                  self.table.print_table()
                
                if choice == 'fold':
                  # end hand if only one playuer remains
                  active_player_count = 0
                  for plyr in self.table.players:
                    if plyr.status != 'out':
                      active_player_count +=1
                  
                  if active_player_count != 2:
                    self.table.iterate_action()
                  self.table.process_decision(id, choice)
                  self.table.print_table()

      #############if we are starting a game#############
      if(tokens[0] == "start"):
        self.started = True
        initial_action = random.randint(1,len(self.table.players))
        for player in self.table.players:
          if(player.seat_number == initial_action):
            player.action = True
        self.table.deal()


      #############if we are joining a table#############
      loggedIn=False
      if(tokens[0] == "join"):
        buy_in = int(tokens[1])
        #check if sender is logged in
        for connectioniterator in self.activePlayersAndAddresses:
          if(connectioniterator[1] == str(a[0])):
            if(connectioniterator[2] == a[1]):
              loggedIn=True

              #if the table is not full
              if(len(self.table.players)<9):

                #create a new player and append to table list
                plyr_id = connectioniterator[0]
                seat_num = len(self.table.players)+1
                player = Player(plyr_id, seat_num, buy_in, None)
                self.table.players.append(player)
                self.table_players.append((str(a[0]), str(a[1]), plyr_id))
                # send table.players [] data to connections that are on the table



                # send to all users that are logged in and on table
                for connection in self.connections:
                  for x in self.activePlayersAndAddresses:
                    if(x[1]==connection.getpeername()[0]):
                      if(x[2]==connection.getpeername()[1]):
                        for p in self.table.players:
                          if(p.player_id == x[0]):
                            player_list = ""
                            for k in self.table.players:
                              player_list += Player.__str__(k)
                            connection.send(bytes("joined {}{}".format(player.player_id, player_list), 'utf-8'))

              else:
                print("table is full")
        for j in self.table.players:
          print("{} [Stack: {}] (Seat: {})".format(j.player_id, j.stack, j.seat_number))

  #infinitely looping run scope that utilizes threads and our handeler function to accept new connections
  def run(self):
    while True:
      c, a = self.sock.accept()
      cThread = threading.Thread(target = self.handler, args = (c, a))
      cThread.daemon = True
      cThread.start()
      self.connections.append(c)
      print(str(a[0])+ ':' + str(a[1]) +  " connected")
      #self.table.players.append(Player(1, 1, 200, None))
      #for player in self.table.players:
      #  print("Player {}[Stack {}]: {}".format(player.player_id, player.stack, player.hand))