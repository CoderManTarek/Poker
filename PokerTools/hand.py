class Hand:
  def __init__(self, card1, card2):
    self.card1 = card1
    self.card2 = card2

  def __str__(self):
    return "{} {} {} {}".format(self.card1.value, self.card1.suit, self.card2.value, self.card2.suit)