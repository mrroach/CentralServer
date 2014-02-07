# Read an OCTGN deck
from xml.etree import ElementTree

def read_file(filename):
  filedata = open(filename).read()
  return read(filedata)

def read(filedata):
  root = ElementTree.fromstring(filedata)
  identity = []
  cards = []
  for section in root.getchildren():
    if len(section) == 1:
      dest = identity
    else:
      dest = cards
    for card in section.getchildren():
      for i in range(int(card.get('qty'))):
        # Read the last 5 digits of card#id
        dest.append("Card{}".format(card.get('id')[-5:]))
  return (identity[0], cards)
