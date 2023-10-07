from PokerTools.table import Table

class ServerTable(Table):
  def __init__(self, deck, connections,  total_seats,players = None, button_seat_number = 1):
    super().__init__(deck, total_seats, players, button_seat_number)
    self.connections = connections
    self.betting_rounds = ["preflop", "flop", "turn", "river"]
    self.current_betting_round = ""

  def iterate_action(self):
    active_player_list = []
    for player in self.players:
      if player.status != "out":
        active_player_list.append(player)

    for index, player in enumerate(active_player_list):
      # find playter who just made a decision
      if player.action == True:
        # take action away from client who jsut made a decision
        for pl in self.players:
          if pl.player_id == player.player_id:
            pl.action = False

        player.action = False
        # give action to next player that is not out
        if((index+1) <= len(active_player_list)-1):
          for p in self.players:
            if p.player_id == active_player_list[index+1].player_id:
              p.action = True
              self.send_action()
              return
        else:
          for p in self.players:
            if p.player_id == active_player_list[0].player_id:
              p.action = True
              self.send_action()
              return

  def is_round_over(self):
    for player in self.players:
      if(player.status == "in (money owed)" or player.status == "starting round"):
        return False
    return True
  
  def increment_betting_round(self):
    for index, rnd in enumerate(self.betting_rounds):
      if rnd == self.current_betting_round:
        if rnd != 'river':
          self.current_betting_round = self.betting_rounds[index + 1]
          break
        else:
          self.current_betting_round = 'showdown'
    
    if self.current_betting_round == 'flop':
      self.flop()
    
    if self.current_betting_round == 'turn':
      self.turn()
    
    if self.current_betting_round == 'river':
      self.river()
    
    if self.current_betting_round == 'showdown':
      print("Showdown")
      self.showdown()


  def process_decision(self, id, choice, amount = 0):
    for player in self.players:
      if player.player_id == id:
        if choice == 'bet':
          self.pot += amount
          player.stack -= amount
          player.money_out += amount
          player.status = "in (money not owed)"
          # set owed for other players
          for plyr in self.players:
            if(plyr == player):
              continue
            if(plyr.status != "out"):
              plyr.owed = player.money_out
              plyr.status = "in (money owed)"
          server_response = "Decision: Player {} {} {}".format(id, choice, amount)
          for connection in self.connections:
            connection.send(bytes(server_response, 'utf-8'))

        if choice == 'check':
          player.status = "in (money not owed)"
          server_response = "Decision: Player {} {}".format(id, choice)
          for connection in self.connections:
            connection.send(bytes(server_response, 'utf-8'))
          if(self.is_round_over() == True):
            print("{} betting round is over".format(self.current_betting_round))
            self.increment_betting_round()

        if choice == 'fold':
          player.status = "out"
          active_players = []
          # count how many players remain in hand
          for plyr in self.players:
            if plyr.status != 'out':
              active_players.append(plyr)
          # if only one player remains, they win without showdown
          if len(active_players) == 1:
            active_players[0].stack += self.pot
            server_response = "Decision: Player {} {}\nWin: Player {} wins ${}".format(id, choice, active_players[0].player_id, self.pot)
            for connection in self.connections:
              connection.send(bytes(server_response, 'utf-8'))
            self.pot = 0
          else:
            server_response = "Decision: Player {} {}".format(id, choice)
            for connection in self.connections:
              connection.send(bytes(server_response, 'utf-8'))
            if(self.is_round_over() == True):
              print("{} betting round is over".format(self.current_betting_round))
              self.increment_betting_round()

        if choice == 'call':
          for player in self.players:
            if player.player_id == id:
              self.pot += amount
              player.stack -= amount
              player.owed = 0
              player.money_out += amount
              player.status = "in (money not owed)"

          server_response = "Decision: Player {} {} {}".format(id, choice, amount)
          for connection in self.connections:
            connection.send(bytes(server_response, 'utf-8'))
          if(self.is_round_over() == True):
            print("{} betting round is over".format(self.current_betting_round))
            self.increment_betting_round()