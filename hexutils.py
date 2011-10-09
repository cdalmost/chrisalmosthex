# Copyright (c) Christopher Almost, 2011.

class HexGame:
  """Representation of a game of hex."""

  swap = { 'r': 'b', 'b': 'r' }

  def __init__(self, game_size=11, onus='r', state_str=None):
    self.size = game_size
    self.onus = onus
    self.board = (self.size * self.size) * ['w']
    self.groups = dict({'r': [], 'b': []})
    self.moves = []
    if state_str and (len(state_str) == self.size * self.size):
      for x in range(self.size * self.size):
        m = state_str[x]
        if m == 'r' or m == 'b':
          i = x // self.size
          j = x - self.size * i
          self.add_move(i, j, m)
        else:
          continue

  def add_move(self, i, j, p):
    self.board[self.size * i + j] = p
    self.groups[p].append(set([(i, j)]))
    self.groups[p] = HexGame.combine(self.groups[p])

  def make_move(self, i, j):
    self.add_move(i, j, self.onus)
    self.onus = HexGame.swap[self.onus]

  def get_move(self, i, j):
    return self.board[self.size * i + j]

  def is_valid(self, i, j):
    return (0 <= i < self.size and 0 <= j < self.size \
        and 'w' == self.board[self.size * i + j])

  def check_win(self):
    for g in self.groups['r']:
      for m in g:
        if m[0] == 0:
          for m in g:
            if m[0] == self.size-1:
              return 'r'
    for g in self.groups['b']:
      for m in g:
        if m[1] == 0:
          for m in g:
            if m[1] == self.size-1:
              return 'b'
    return ''

  @staticmethod
  def combine(grps):
    """Reduce a list of groups by amalgamating all groups with adjacent elements."""
    combd = []
    while grps:
      g = grps.pop()
      combd.append(g)
      for gg in grps:
        if HexGame.adjacent_groups(g, gg):
          combd.remove(g)
          grps.remove(gg)
          grps.append(g.union(gg))
          break
    return combd

  @staticmethod
  def adjacent_groups(g, gg):
    """Returns True if the groups are adjacent."""
    for m in g:
      for mm in gg:
        if HexGame.adjacent_moves(m, mm):
          return True
    return False

  @staticmethod
  def adjacent_moves(m, mm):
    """Returns True if the hexs are adjacent."""
    a, b = m[0] - mm[0], m[1] - mm[1]
    return abs(a) <= 1 and abs(b) <= 1 and (a*b == 0 or a*b == -1)

if __name__=='__main__':
  a = [u'brbbrbrbrbrbrbrbrbbrbrbrb',
      u'bbbbwwwwwwwwwwwwwwwwwrrrb',
      u'rrrrrrrrrrrrrrrrrrrrrrrrr',
      u'bbbbbbbbbbbbbbbbbbbbbbbbb',
      u'rrrrrrrrrrrbbbbbbrbrbbrrb',
      u'rbbbbbbbbbbbrrbbrbrbrbrrr',
      u'rrrrbrrrrrbrbrbrbrrbrrrbb']
  for s in a:
    hg = HexGame(5, state_str=s)
    print hg.check_win()

