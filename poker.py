import sys
from PokerTools.server import Server
from PokerTools.client import Client

def main():
  #instantiate server
  if (len(sys.argv)>1):
    client = Client(sys.argv[1])
    
  #instantiate client
  else:
    server = Server()
    server.run()

main()