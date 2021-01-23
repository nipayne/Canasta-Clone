import pygame
import pygame_gui
import numpy
import random
import json
from PyInquirer import prompt, Separator

pygame.init()

w = 1400
h = 800
scaled_w = w/800
scaled_h = h/600
window_surface = pygame.display.set_mode((w,h))

background = pygame.Surface((w,h))
background.fill(pygame.Color('#000000'))
font = pygame.font.SysFont(None, 24)
card_font = pygame.font.SysFont(None, 36)

manager = pygame_gui.UIManager((w,h))

next_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((700*scaled_w, 550*scaled_h),
                                                                     (100*scaled_w, 50*scaled_h)), text='NEXT (N)',
                                           manager=manager)
draw_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0*scaled_w, 550*scaled_h),
                                                                     (100*scaled_w, 50*scaled_h)), text='DRAW (D)',
                                           manager=manager)
play_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((150*scaled_w, 550*scaled_h),
                                                                     (100*scaled_w, 50*scaled_h)), text='PLAY (P)',
                                           manager=manager)
clock = pygame.time.Clock()



class Discard:
    def __init__(self):
        self.discards = []

    def addToDiscard(self, card):
        self.discards.append(card)

    def clearDiscard(self, botCard):
        self.discards.clear()
        self.addToDiscard(botCard)


class Player:
    def __init__(self, player_num):
        self.player_num = player_num
        self.hand = []
        self.kitty = []
        self.canastas = {'reds': [], 'blacks': [], 'wilds': [], 'sevens': []}
        self.can_win = False
        self.board = {}
        self.red3score = 0

    # Return all cards in hand as a string
    def getHand(self):
        s = str(self.player_num) + ": "
        for c in self.hand:
            s = s + c.value + " " + c.color[0] + "; "

        return s

    # Return all cards on board as a string
    def getBoard(self):
        s = str(self.player_num) + ": "
        for c in self.board:
            s = s + c + "; "
        return s

    # Return hand size
    def getHandSize(self):
        return len(self.hand)

    # only should get called at beginning of game
    # sets hand size to 15
    def setHand(self, decks):

        hand = []
        for i in range(0, 15):
            hand.append(decks.pop())
        self.hand = hand

    # only should get called at beginning of game
    # sets kitty size to 10
    def setKitty(self, decks):
        kitty = []
        for i in range(0, 10):
            kitty.append(decks.pop())
        self.kitty = kitty

    # draw 2.  If a red 3 is drawn, it immediately gets counted and discarded from the hand.  Another card is then drawn
    def draw(self, decks):
        for i in range(0, 2):
            pick = decks.pop()
            while pick.value == '3' and pick.color == 'red':
                if len(decks) < 1: break
                print(self.red3score)
                self.red3score += 1
                pick = decks.pop()
            print((pick.value, pick.color))
            self.hand.append(pick)

    # Discard card and add it to the discard pile.
    def discard(self, card, d):
        self.hand.remove(card)
        d.addToDiscard(card)


    ####################################################################################################################
    ##  playToBoard() and makeCanasta() both need substantial modification, and probably is the last major item to    ##
    ##  address, excluding the GUI.                                                                                   ##
    ####################################################################################################################

    # cards will all contain the same number
    # if more than one number is to be played, will be looped in run()
    def playToBoard(self, cards):
        for card in cards:
            self.hand.remove(card)

            # Board is a dictionary, with keys being the value of the card and values being a list of Cards
            # Either find a key that matches the card from hand and append Card to list
            # or create new key with value of Card
            # If card value is wild, then make a temp switch to inputted card number
            #   Search for inputted card, but append original
            # For wilds, must put jokers (14) as 2
            tempCard = card

            # if card.value in ('2', 'joker'):
            #     # temp = input("Where do you want " + str(card.value) + ":  ")
            #     # tempq = [{'type':'list','name':'wildtype', 'message':"Where do you want " + str(card.value) + ":  ",'choices':match}]
            #     # temp = prompt(tempq)
            #     # print(temp)
            #     try:
            #         temp = random.choice(list(self.board.keys()))
            #     except:
            #         temp = 2
            #     # print(list(None))
            #     tempCard = Card(temp, card.color)

            # Card Num not already on board
            if self.board.get(tempCard.value) is None:
                self.board.update({tempCard.value: [card]})
            # Card Num already on board
            else:
                self.board[tempCard.value].append(card)

            print(self.board.get(tempCard.value))
            # If this makes a canasta (>6), make canasta and remove cards from board
            if len(self.board.get(tempCard.value)) > 6:
                if tempCard.value == 2:
                    # print([(c.value,c.color) for c in self.board.get(tempCard.value)])
                    exit()
                self.makeCanasta(self.board.pop(tempCard.value), tempCard.value)

    # Helper function for playToBoard(), which places canasta in appropriate bin.
    def makeCanasta(self, can, num):
        values = [c.value for c in can]
        if num == '2':
            self.canastas.get('wilds').append([(c.value, c.color) for c in can])
        elif values.sort() == values.sort(reverse=True):
            if num not in ('2', '7', 'joker'):
                self.canastas.get('reds').append([(c.value, c.color) for c in can])
            elif num == '7':
                self.canastas.get('sevens').append([(c.value, c.color) for c in can])
        else:
            self.canastas.get('blacks').append([(c.value, c.color) for c in can])

    ####################################################################################################################


    # Internally checks whether a player can win and sets a true flag if so.  Should be called during each turn.
    def setWinConditions(self):
        if len(self.canastas.get('reds')) > 0 and len(self.canastas.get('blacks')) > 0 and len(
                self.canastas.get('wilds')) > 0:
            self.can_win = True


# Card class - stores number, suit, and image (to be used later)
class Card:
    def __init__(self, value, color, suit, suitIm):
        self.value = value
        self.color = color
        self.suit = suit
        self.suitIm = suitIm
    def getValue(self):
        return self.value

    def getSuit(self):
        return self.suit

    def getColor(self):
        return self.color


# Shuffles all of the cards in the draw pile.  While any number of decks can be used, the default is 10.
def createDecks():
    suiteSheet = pygame.image.load('path_to_file').convert()
    suiteWidth = suiteSheet.get_width() / 4
    suitsImg = []
    for s in range(4):
        x = (s) * suiteWidth
        cardIm = suiteSheet.subsurface(x, 0, suiteWidth, suiteSheet.get_height()).convert()
        suitsImg.append(pygame.transform.scale(cardIm,(30,30)))

    num_decks = 10
    suits = ['spades', 'diamonds', 'clubs', 'hearts']
    colors = ['black','red','black','red']
    numbers = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']

    deck = []
    for i in range(4):
        for j in range(13):
            deck.append(Card(numbers[j],colors[i],suits[i], suitsImg[i]))

    #deck = [Card(value, color, "") for value in numbers for color in colors]
    deck.append(Card('joker', 'joker','joker',pygame.Surface((0,0))))
    deck.append(Card('joker', 'joker','joker',pygame.Surface((0,0))))
    print(len(deck))
    # duplicate decks by num_decks
    decks = []
    for i in range(0, num_decks + 1):
        decks.extend(deck)
    # shuffle everything
    random.shuffle(decks)

    return decks


def playGame():
    meld = 50

    p1 = Player(1)
    p2 = Player(2)


    # house rules scoring for each card
    card_score = {'ace': 20, '2': 20, '3': 5, '4': 5, '5': 5, '6': 5, '7': 5, '8': 5, '9': 5, '10': 10,
                  'jack': 10, 'queen': 10, 'king': 10, 'joker': 50}
    # Sets position of cursor to play card
    pos = 0
    has_drawn = False
    discard = Discard()
    time_delta = clock.tick(60) / 1000.0

    is_running = True

    # Setup for game
    gameDeck = createDecks()
    p1.setHand(gameDeck)
    p1.setKitty(gameDeck)
    p2.setHand(gameDeck)
    p2.setKitty(gameDeck)
    currentPlayer = p1

    # Win Conditions, as well as quit condition (breaks loop if closed, will later be used for in-game exit/reset)
    while not currentPlayer.can_win and currentPlayer.getHandSize() > 0 and is_running:
        print(currentPlayer.getBoard())
        # Is the game waiting for user Input?
        waitForPlayer = True

        # pygame boilerplate/literally no idea
        manager.update(time_delta)

        # random.shuffle(currentPlayer.hand)

        # currentPlayer.discard(random.choice(currentPlayer.hand),discard)

        # For display/testing purposes, won't be needed in final version
        # Just keeps player 1 first
        if p1.player_num == 1:
            hand1 = card_font.render(p1.getHand(), True, (255, 255, 255))
            hand2 = card_font.render(p2.getHand(), True, (255, 255, 255))
        else:
            hand2 = card_font.render(p1.getHand(), True, (255, 255, 255))
            hand1 = card_font.render(p2.getHand(), True, (255, 255, 255))

        # Player Number
        player = card_font.render("Current Player: " + str(currentPlayer.player_num) + "  Number of Red 3s: "
                           + str(currentPlayer.red3score), True, (255, 255, 255))
        # Card selected
        card = card_font.render(str(currentPlayer.hand[pos].value) + " "
                           + str(currentPlayer.hand[pos].color) + " "
                           + str(card_score.get(currentPlayer.hand[pos].value)), True,
                           (255, 255, 255))

        # Put everything on screen
        window_surface.blit(background, (0*scaled_w, 0*scaled_h))
        window_surface.blit(hand1, (100*scaled_w, 100*scaled_h))
        window_surface.blit(hand2, (100*scaled_w, 200*scaled_h))
        window_surface.blit(card, (100*scaled_w, 300*scaled_h))
        x = 150*scaled_w
        for k in currentPlayer.board.keys():
            y = 400*scaled_h
            for v in currentPlayer.board.get(k):
                window_surface.blit(v.suitIm, (x, y))
                c = card_font.render(str(v.value) + " ", True,(255, 255, 255))
                window_surface.blit(c,(x + 35,y))

                y += 40
            x += 125
        window_surface.blit(player, (0*scaled_w, 0*scaled_h))
        manager.draw_ui(window_surface)

        pygame.display.update()

        # User Input Loop
        # waitForPlayer is needed(?) in every case to quit loop and update display - probably a better way of doing this
        while waitForPlayer:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                    waitForPlayer = False

                # Change cursor to another card
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if pos > 0:
                            pos -= 1
                    if event.key == pygame.K_RIGHT:
                        if pos < currentPlayer.getHandSize() - 1:
                            pos += 1
                    if event.key == pygame.K_p:
                        currentPlayer.playToBoard([currentPlayer.hand[pos]])
                        pos = 0
                    if event.key == pygame.K_n:
                        print('Next')
                        p1, p2 = p2, p1
                        currentPlayer = p1
                        pos = 0
                        has_drawn = False
                    if event.key == pygame.K_d:
                        if not has_drawn:
                            currentPlayer.draw(gameDeck)
                            has_drawn = True
                    waitForPlayer = False

                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        # Go to next player
                        if event.ui_element == next_button:
                            print('Next')
                            p1, p2 = p2, p1
                            currentPlayer = p1
                            pos = 0
                            has_drawn = False
                        # Draw a card only if not drawn already in turn
                        if event.ui_element == draw_button:
                            if not has_drawn:
                                currentPlayer.draw(gameDeck)
                                has_drawn = True

                        # Play whatever card cursor is on
                        if event.ui_element == play_button:
                            currentPlayer.playToBoard([currentPlayer.hand[pos]])
                            pos = 0
                    waitForPlayer = False

                manager.process_events(event)

        # For testing purposes
        if len(gameDeck) < 2:
            print(json.dumps(p1.canastas.get('reds'), indent=4))
            print("=========================================================")
            print(json.dumps(p2.canastas.get('reds'), indent=4))
            break



if __name__ == '__main__':
    playGame()
