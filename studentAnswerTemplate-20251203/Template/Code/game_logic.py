import random


# Core game logic for 21 (Blackjack) without any UI components.
# This class manages the deck, hands, and game rules.
# It provides methods for dealing cards, calculating totals,
# and determining the winner.
# UI components should call these methods to drive the game.
# No input/output or UI code should be present here.
# This separation allows for easy testing and reuse of the game logic.
class Game21:
    def __init__(self):
        # Start immediately with a fresh round
        self.new_round()

    # ROUND MANAGEMENT

    def new_round(self):
        """
        Prepares for a new round
        Suggested process:
        - Create and shuffle a new deck
        - Reset card pointer
        - Empty both hands
        - Reset whether the dealer's hidden card has been revealed
        """
        self.deck = self.create_deck()
        random.shuffle(self.deck)

        # Instead of removing cards from the deck,
        # we keep an index of the "next card" to deal.
        self.deck_position = 0

        # Hands start empty; cards will be dealt after UI calls deal_initial_cards()
        self.player_hand = []
        self.dealer_hand = []

        # The first dealer card starts hidden until Stand is pressed
        self.dealer_hidden_revealed = False

    def deal_initial_cards(self):
        """
        Deal two cards each to player and dealer.
        Called at the start of a round after new_round().
        """
        self.player_hand = [self.draw_card(), self.draw_card()]
        self.dealer_hand = [self.draw_card(), self.draw_card()]

    # DECK AND CARD DRAWING

    def create_deck(self):
        """
        Create a standard 52-card deck represented as text strings, e.g.:
        'A♠', '10♥', 'K♦'

        Ranks: A, 2–10, J, Q, K
        Suits: spades, hearts, diamonds, clubs (with Unicode symbols)
        """
        ranks = ["A"] + [str(n) for n in range(2, 11)] + ["J", "Q", "K"]
        suits = ["♠", "♥", "♦", "♣"]

        return [f"{rank}{suit}" for rank in ranks for suit in suits]
        # This creates a list comprehension that combines each rank with each suit.
        # Resulting list has 52 unique card strings.

    def draw_card(self):
        """
    Return the next card in the shuffled deck. If the deck is exhausted,
    recreate and reshuffle the deck to avoid IndexError, then return the
    first card of the new deck.

    Returns:
        card: A single card object (type depends on how you represent cards,
              e.g., tuple, string, or custom Card class).
    """
        # If deck exhausted (should be rare), recreate and shuffle to avoid errors
        # - `self.deck_position` tracks the index of the next card to draw.
        # - When it reaches or exceeds len(self.deck) there are no more cards to draw.
        if self.deck_position >= len(self.deck):
            # Recreate the deck (assumes self.create_deck() returns a full deck list)
            self.deck = self.create_deck()
            # Shuffle the new deck in-place to randomize order for the new round
            random.shuffle(self.deck)
            # Reset position to start drawing from the top of the shuffled deck
            self.deck_position = 0

        # Fetch the next card at the current position
        card = self.deck[self.deck_position]
        # Advance the pointer so the next call returns the subsequent card
        self.deck_position += 1
        # Return the drawn card
        return card

    def card_value(self, card):
        """
        Convert a card string into its numeric value.

        Rules:
        - Number cards = their number (2–10)
        - J, Q, K = 10
        - A is normally 11, may later count as 1 if needed

        Parameters:
            card (str): Card string like 'A♠', '10♥', 'K♦' where the last character is the suit.

        Returns:
            int: numeric value used for scoring (Ace is returned as 11 here; the hand_total
                 method will reduce Aces to 1 when needed to avoid busting).
        """
        rank = card[:-1]  # everything except the suit symbol

        # Face cards (Jack, Queen, King) are always worth 10 points.
        if rank in ["J", "Q", "K"]:
            return 10

        # Aces are treated as 11 initially; hand_total will adjust them to 1 if needed.
        if rank == "A":
            return 11  # Initially treat Ace as 11

        # Otherwise it's a number from 2 to 10
        return int(rank)

    def hand_total(self, hand):
        """
        Calculates the best possible total for a hand.
        Aces are counted as 11 unless this would bust the hand,
        in which case they are reduced to 1.

        Suggested Process:
        1. Count all Aces as 11 initially.
        2. If total > 21, subtract 10 for each Ace, so it effectively makes them = 1
        """
        # Sum initial values (Aces counted as 11 by card_value)
        total = sum(self.card_value(c) for c in hand)
        # Count how many aces are present
        ace_count = sum(1 for c in hand if c[:-1] == "A")

        # Convert Aces from 11 to 1 (subtract 10) until total <= 21 or no more aces
        while total > 21 and ace_count > 0:
            total -= 10
            ace_count -= 1

        return total

    # PLAYER ACTIONS

    def player_hit(self):
        # Add one card to the player's hand and return it, so the UI can display the card.
        card = self.draw_card()

        # Add the drawn card to the player's hand in-place. The hand's order
        # preserves the sequence of draws (useful for UI layout or logging).
        self.player_hand.append(card)

        # Return the card so the caller can display it immediately or perform
        # additional checks (e.g. update totals). The player's total is not
        # computed here — call `player_total()` when you need the updated score.
        return card

    def player_total(self):
        """
        Return the player's current hand total.

        This is a thin wrapper around `hand_total` that uses `self.player_hand`.
        Returns an integer representing the best possible total (Aces adjusted
        from 11 to 1 as needed to avoid busting).

        Returns:
            int: player's hand total (0 if the hand is empty).
        """
        # Delegate the actual calculation to hand_total (which handles Aces).
        return self.hand_total(self.player_hand)

    # DEALER ACTIONS

    def reveal_dealer_card(self):
        """
        Reveal the dealer's hidden card.

        Side effects:
        - Sets `self.dealer_hidden_revealed = True` so UIs know to show both
          of the dealer's cards. This does not change the dealer's hand or totals.

        When to call:
        - Typically called when the player stands and the dealer begins their turn.
        """
        # Called when the player presses Stand. After this, the UI should show both dealer cards.
        self.dealer_hidden_revealed = True

    def dealer_total(self):
        """
        Return the dealer's current hand total.

        Like `player_total`, this delegates to `hand_total` and returns the best
        total for the dealer's hand (Aces adjusted to avoid busting).

        Returns:
            int: dealer's hand total.
        """
        # Delegate to hand_total which handles Ace adjustments
        return self.hand_total(self.dealer_hand)

    def play_dealer_turn(self):
        """
        Play out the dealer's actions after the player stands.

        Rules implemented:
        - Reveal the dealer's hidden card first (set `dealer_hidden_revealed`).
        - Dealer will hit (draw cards) while their total is less than 17.
        - Dealer stands when total is 17 or higher.

        Returns:
            list: cards drawn by the dealer during this turn (may be empty).

        Notes / Edge cases:
        - Current behavior: dealer stands on all 17s (including "soft 17").
          If you want the dealer to hit on a soft 17 (A+6), change the logic
          to treat soft 17 explicitly.
        - This method mutates `self.dealer_hand` in place and returns the list
          of newly drawn cards so the UI can animate them.
        - If deck is exhausted while dealer is drawing, `draw_card()` will
          recreate and reshuffle the deck automatically.
        - Concurrency: protect shared state with a lock if multiple threads may
          call game methods concurrently.
        """
        # Reveal dealer card before playing out the rest of the turn
        self.dealer_hidden_revealed = True
        drawn_cards = []

        # Dealer hits on totals less than 17, then stops. Use dealer_total()
        # which already handles Ace values correctly.
        while self.dealer_total() < 17:
            card = self.draw_card()
            self.dealer_hand.append(card)
            drawn_cards.append(card)
        return drawn_cards

    # WINNER DETERMINATION

    def decide_winner(self):
        """
        Determine the round outcome after both player and dealer have finished.

        Flow and return values:
        - Ensure dealer's hidden card is revealed for final comparison.
        - If the player busts (total > 21) the player loses.
        - Else if the dealer busts the player wins.
        - Else compare totals: higher total wins; equal totals are a push (tie).

        Returns:
            str: human-readable result message describing the winner.

        Notes:
        - If both player and dealer are over 21, this implementation returns
          "Player busts. Dealer wins!" because the player check comes first.
          Adjust ordering if you prefer a different rule.
        - This method returns a simple string for use by UIs; if you need a
          programmatic result consider returning an enum or structured object.
        """
        # Decide the outcome of the round.
        # Ensure dealer card is revealed for final comparison
        self.dealer_hidden_revealed = True

        p_total = self.player_total()
        d_total = self.dealer_total()

        # Check busts first; player busts immediately result in dealer win.
        if p_total > 21:
            return "Player busts. Dealer wins!"
        if d_total > 21:
            return "Dealer busts. Player wins!"

        # Neither busted: higher total wins, equality is a push (tie).
        if p_total > d_total:
            return "Player wins!"
        if d_total > p_total:
            return "Dealer wins!"
        return "Push (tie)."
