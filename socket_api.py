import socket
import threading
import sys

#class object
class Server:
  
  # server program data
  usernamesAndPasswords = []
  activeUsernamesAndAddresses = []
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  connections = []

  def __init__(self):

    #load user file data into server program data upon initialization
    file = open("users.txt", "r")
    fileData = file.readlines()
    file.close()
    check = 0
    tempUser = ''
    tempPassword = ''

    #parsing and formatting logic to store file data
    for string in fileData:
      for character in string:
        if(character == ')'):
          check = 0
          break
        if(character == ' '):
          check = 2
          continue
        if(character == ','):
          continue
        if(check == 1):
          tempUser += character
        if(check == 2):
          tempPassword += character
        if(character == '('):
          check = 1
      self.usernamesAndPasswords.append((tempUser, tempPassword))
      tempUser = ''
      tempPassword = ''

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
        for j in self.activeUsernamesAndAddresses:
          if(j[1]==str(a[0])):
            if(j[2]==a[1]):
              userlogincheck=True
              print(j[0]+" logout.")

              #respond to all clients with logout message
              for connection in self.connections:
                connection.send(bytes((j[0]+" left"), 'utf-8'))
              self.activeUsernamesAndAddresses.remove(j)
        if(userlogincheck == False):
          print("You are not logged in")



      #############if we are creating a new User#############
      checkuserlogin = False
      lengthCheck = False
      tokencheck = False
      if(tokens[0] == "newuser"):
        checker = 0

        #check if sender is logged in
        for connectioniterator in self.activeUsernamesAndAddresses:
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
          for userAndPass in self.usernamesAndPasswords:
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
            self.usernamesAndPasswords.append((newUsername, newPassword))
            file = open("users.txt", "a")
            file.write('\n'+'('+newUsername+','+' ' + newPassword + ')')
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
          for connectioniterator in self.activeUsernamesAndAddresses:
            #print(connectioniterator[1],str(a[0]),connectioniterator[2],a[1])
            if(connectioniterator[0]==tokens[1]):
              checklogin = True
              break
            if(connectioniterator[1] == str(a[0])):
              if(connectioniterator[2] == a[1]):
                checklogin=True
                break

        #login
        for users in self.usernamesAndPasswords:
          if(checklogin==True or tokenschecker==False):
            break
          if(tokens[1] == users[0]):
            if(tokens[2] == users[1]):
              self.activeUsernamesAndAddresses.append((tokens[1], str(a[0]), a[1]))
              
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
        for connectioniterator in self.activeUsernamesAndAddresses:
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
                    for x in self.activeUsernamesAndAddresses:
                      if(x[1]==connection.getpeername()[0]):
                        if(x[2]==connection.getpeername()[1]):              
                          connection.send(bytes((senderName + ": " + formattedMessage), 'utf-8'))
                else:
                  #check to see if user is online
                  for tmp in self.activeUsernamesAndAddresses:
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
        for connectioniterator in self.activeUsernamesAndAddresses:
          if(connectioniterator[1] == str(a[0])):
            if(connectioniterator[2] == a[1]):
              loggedIn=True
              for temp in self.activeUsernamesAndAddresses:
                serverList+=temp[0] + ", "
              # find client that sent this packet and respond 
              for connection in self.connections:
                if(connection.getpeername()[0] == str(a[0])):
                  if(connection.getpeername()[1] == a[1]):
                      connection.send(bytes(serverList[:-2], 'utf-8'))

  #infinitely looping run scope that utilizes threads and our handeler function to accept new connections
  def run(self):
    while True:
      c, a = self.sock.accept()
      cThread = threading.Thread(target = self.handler, args = (c, a))
      cThread.daemon = True
      cThread.start()
      self.connections.append(c)
      print(str(a[0])+ ':' + str(a[1]) +  " connected")

#client object
class Client:

  # instantiate socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  def sendMsg(self):
    while True:
      self.sock.send(bytes(input(""), 'utf-8'))

  #instantiate thread
  def __init__(self, address):
    addressAndPort = address.split(':')
    try:
      self.sock.connect((addressAndPort[0], int(addressAndPort[1])))
      iThread = threading.Thread(target=self.sendMsg)
      iThread.daemon = True
      iThread.start()
    except:
      print("attempt to connect to server was unsuccessful")
      exit(0)

    while True:
      try:
        data = self.sock.recv(1024)
      except:
        print("connection to server was lost")
        break
      if not data:
        break
      print(str(data, 'utf-8'))

# driver function 
def main():

  #instantiate server
  if (len(sys.argv)>1):
    client = Client(sys.argv[1])
    
  #instantiate client
  else:
    server = Server()
    server.run()

main()