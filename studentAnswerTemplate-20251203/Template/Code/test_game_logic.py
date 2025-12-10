from game_logic import Game21

print('=== Game21 quick tests ===')

# Initial deal test
g = Game21()
g.deal_initial_cards()
print('Initial player hand:', g.player_hand, 'total:', g.player_total())
print('Initial dealer hand:', g.dealer_hand, 'total (hidden until reveal):', g.dealer_total())

# Ace handling tests
print('\n-- Ace handling --')
print("['A\u2660','A\u2665','9\u2663'] -> expected 21 ->", g.hand_total(['A\u2660','A\u2665','9\u2663']))
print("['A\u2660','K\u2665'] -> expected 21 ->", g.hand_total(['A\u2660','K\u2665']))
print("['A\u2660','9\u2665'] -> expected 20 ->", g.hand_total(['A\u2660','9\u2665']))

# Deck exhaustion test: draw 53 cards to trigger IndexError on the last draw
print('\n-- Deck exhaustion test --')
g = Game21()
exception = None
try:
    for i in range(53):
        c = g.draw_card()
    print('Drew 53 cards without exception (unexpected).')
except Exception as e:
    exception = e
    print('Exception type on overdraw:', type(e).__name__, '-', e)

print('\n=== End tests ===')

