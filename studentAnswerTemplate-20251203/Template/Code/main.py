from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, \
    QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
import sys
import os
import traceback
# this project should use a modular approach - try to keep UI logic and game logic separate
from game_logic import Game21


# Function to get asset paths dynamically
def asset_path(*parts):
    """
        This function returns the absolute path for assets located relative
        to the directory of this script file.
        It's useful for loading files images, sounds and more in a platform independent way.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', *parts))


#  create styled QLabel
def make_label(text='', bold=False, color='white'):
    """
    Create and return a styled QLabel with simple text color and optional bold font.

    Parameters:
        text (str): The text to display in the label. Default is an empty string.
        bold (bool): If True, the label text will use a bold weight via stylesheet.
        color (str): CSS color name or hex string for the text color '#ffffff'.

    """
    # Create the QLabel with the provided text
    lbl = QLabel(text)

    # Build a small CSS string for styling. Keep it minimal so callers can override
    # or extend styles later if needed (e.g. via `lbl.setStyleSheet(lbl.styleSheet() + '...')`).
    style = f"color: {color};"

    # Add bold weight if requested. QFont is more precise.
    if bold:
        style += " font-weight: bold;"

    # Apply the stylesheet to the label. This sets only the properties we added above.
    lbl.setStyleSheet(style)

    # Return the configured label (caller will insert into layouts/parents)
    return lbl


class MainWindow(QMainWindow):
    def __init__(self):
        """
            Constructor to initialize the main window of the application.
            This function is called when an instance of MainWindow is created.
         """
        super().__init__()  # Initialize the parent class (QMainWindow)
        # Set the window title to 'Game of Blackjack 21'
        self.setWindowTitle('Game of Blackjack 21')
        # Move the window to a specific position on the screen (200, 200 pixels)
        self.move(200, 200)
        # Set the window to have a fixed size of 600x600 pixels
        self.setFixedSize(600, 600)
        # Initialize the game logic by creating an instance of Game21
        self.game = Game21()  # Initialize game logic
        # Initialize a dictionary to track player statistics (wins, losses, and pushes)
        self.stats = {'wins': 0, 'losses': 0, 'pushes': 0}  # Player statistics
        # Initialize the font style for labels (currently set to bold)
        self._font_bold = True
        self.initUI()  # Call the initUI function to set up the user interface

    def initUI(self):
        """
             This function will be responsible for initializing and setting up the user interface (UI).
             It will create widgets like buttons, labels, and game status displays, but the actual
             implementation is not shown in this part of the code.
         """

        # Create central widget for the main window
        central = QWidget()
        self.setCentralWidget(central)
        # BACKGROUND WALLPAPER
        # Set the path to the background image for the game
        self.wallpaper_path = asset_path('Assets', 'Backgrounds', 'background_1.png')

        # Create a QLabel to display the background image
        self.bg_label = QLabel(central)
        self.bg_label.setScaledContents(True)  # Make sure the background is scaled to fit the window
        self.bg_label.setGeometry(0, 0, self.width(), self.height())  # Set label size to window size
        self.bg_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents)  # Make the background ignore mouse events
        self.bg_label.lower()  # Send the background label to the bottom, so other widgets can be on top
        self.wallpaper_pix = None  # Placeholder for the wallpaper image
        if os.path.exists(self.wallpaper_path):  # Check if the background image exists
            wp = QPixmap(self.wallpaper_path)  # Load the wallpaper as a QPixmap
            if not wp.isNull():  # Ensure the image loaded correctly
                self.wallpaper_pix = wp
                # Scale and set the wallpaper image to fit the window
                self.bg_label.setPixmap(wp.scaled(self.width(), self.height(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                                  Qt.TransformationMode.SmoothTransformation))
        # MAIN LAYOUT
        # Create the main vertical layout for the window
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)  # Remove margins around the layout
        central.setLayout(self.mainLayout)  # Set the main layout on the central widget

        # DEALER AREA
        # Label for the dealer's area
        self.dealerLabel = make_label('Dealer', bold=self._font_bold)
        # Horizontal layout for the dealer's cards
        self.dealerCardsLayout = QHBoxLayout()
        # Label to show the dealer's total score (initially unknown, represented by '?')
        self.dealerTotalLabel = make_label('Dealer: ?')
        # Add dealer-related widgets to the main layout, centered
        self.mainLayout.addWidget(self.dealerLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.mainLayout.addLayout(self.dealerCardsLayout)
        self.mainLayout.addWidget(self.dealerTotalLabel, alignment=Qt.AlignmentFlag.AlignHCenter)

        # TABLE AREA
        # Create a container widget for the game table
        self.tableContainer = QWidget()
        self.tableContainer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Vertical layout to hold other widgets related to the table (e.g., feedback label, table image)
        tableLayout = QVBoxLayout()
        tableLayout.setContentsMargins(0, 0, 0, 0)  # Remove margins for this layout
        self.tableContainer.setLayout(tableLayout)

        # FEEDBACK LABEL
        # Label to display feedback to the player (e.g., win, loss, etc.)
        self.feedbackLabel = QLabel('')
        self.feedbackLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedbackLabel.setStyleSheet('color: white; font-weight: bold; background-color: rgba(0,0,0,0);')
        self.feedbackLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        tableLayout.addStretch()  # Add stretch so the feedback label stays at the bottom

        # TABLE IMAGE
        # Set the path to the table image
        table_path = asset_path('Assets', 'Tables', 'table_green.png')
        self.table_pix = None  # Placeholder for table image
        self.tableLabel = QLabel()  # QLabel to display the table
        self.tableLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if os.path.exists(table_path):  # Check if the table image exists
            pix = QPixmap(table_path)  # Load the table image
            if not pix.isNull():  # Ensure the image loaded correctly
                self.table_pix = pix
                self.update_table_size()  # Call method to adjust table size if needed
                self.feedbackLabel.setParent(self.tableLabel)  # Set the feedback label as a child of the table label
        else:
            self.tableLabel.setText('[Table]')  # If no table image, show placeholder text
            self.feedbackLabel.setParent(self.tableContainer)  # Place the feedback label directly in the container
        tableLayout.addWidget(self.tableLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        tableLayout.addStretch()  # Add stretch to position the table at the center

        # STATISTICS WIDGET
        # Create a widget to hold player statistics (win/loss/push)
        self.statsWidget = QWidget()
        statsLayout = QVBoxLayout()
        statsLayout.setContentsMargins(6, 6, 6, 6)  # Set margins for the stats layout
        self.statsWidget.setLayout(statsLayout)
        statsLayout.addWidget(make_label('Player Statistic:', bold=True))
        self.winLabel = make_label('win : 0')
        self.lossLabel = make_label('loss: 0')
        self.pushLabel = make_label('push: 0')
        statsLayout.addWidget(self.winLabel)
        statsLayout.addWidget(self.lossLabel)
        statsLayout.addWidget(self.pushLabel)
        self.statsWidget.setFixedWidth(140)  # Set a fixed width for the statistics widget

        # MID ROW WITH STATS AND TABLE
        # Create a mid-row container to align the stats and table in the layout
        midRow = QWidget()
        midLayout = QHBoxLayout()
        midLayout.setContentsMargins(0, 0, 0, 0)  # Remove margins for this layout
        midRow.setLayout(midLayout)
        midLayout.addWidget(self.statsWidget, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Center container for the game table, ensuring it's centered in the layout
        centerWrapper = QWidget()
        centerLayout = QHBoxLayout()
        centerLayout.setContentsMargins(0, 0, 0, 0)  # Remove margins for this layout
        centerWrapper.setLayout(centerLayout)
        centerWrapper.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        centerLayout.addStretch(1)  # Add stretch to keep the table centered
        centerLayout.addWidget(self.tableContainer, alignment=Qt.AlignmentFlag.AlignCenter)
        centerLayout.addStretch(1)

        # Right spacer to balance the statistics widget on the left
        self.rightSpacer = QWidget()
        self.rightSpacer.setFixedWidth(self.statsWidget.width())  # Match the width of the stats widget
        midLayout.addWidget(centerWrapper, stretch=1)
        midLayout.addWidget(self.rightSpacer)

        # Add the mid-row to the main layout
        self.mainLayout.addWidget(midRow)

        # Adjust spacers and background
        self.update_spacers()  # Method to update any spacing between widgets
        self.update_background()  # Method to update background
        self.update_table_size()  # Method to adjust the table size if needed

        # PLAYER AREA
        # Label for the player's area
        self.playerLabel = make_label('Player', bold=self._font_bold)
        # Horizontal layout for the player's cards
        self.playerCardsLayout = QHBoxLayout()
        # Label to show the player's total score (initially 0)
        self.playerTotalLabel = make_label('Player: 0')
        self.mainLayout.addWidget(self.playerLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.mainLayout.addLayout(self.playerCardsLayout)
        self.mainLayout.addWidget(self.playerTotalLabel, alignment=Qt.AlignmentFlag.AlignHCenter)

        # BUTTONS
        # Create layout for buttons (Hit, Stand, New Round)
        self.buttonsLayout = QHBoxLayout()
        self.hitButton = QPushButton('Hit')  # Button to draw a card
        self.standButton = QPushButton('Stand')  # Button to stop drawing cards
        self.newRoundButton = QPushButton('New Round')  # Button to start a new round

        # Connect button clicks to respective methods
        self.hitButton.clicked.connect(self.on_hit)
        self.standButton.clicked.connect(self.on_stand)
        self.newRoundButton.clicked.connect(self.on_new_round)
        # Add buttons to the layout
        self.buttonsLayout.addWidget(self.hitButton)
        self.buttonsLayout.addWidget(self.standButton)
        self.buttonsLayout.addWidget(self.newRoundButton)
        self.mainLayout.addLayout(self.buttonsLayout)

        # Setup for the new round (initializing any required values)
        self.new_round_setup()

    def on_hit(self):
        """
            Triggered when the player clicks the 'Hit' button.
            The player draws one additional card and the game state is updated.
            """

        # Player takes one card from the deck
        card = self.game.player_hit()

        # Visually add the drawn card to the player's card layout
        self.add_card(self.playerCardsLayout, card)

        # Update the player's total score label
        self.playerTotalLabel.setText(f'Player: {self.game.player_total()}')

        # Check if the player has busted (total exceeds 21)
        if self.game.player_total() > 21:
            # Reveal all dealer cards since the round is now over
            self.update_dealer_cards(full=True)

            # Determine the winner of the round
            result = self.game.decide_winner()

            # Update win/loss/push statistics based on the result
            self.update_stats(result)

            # Display the result message to the player
            self.feedbackLabel.setText(result)

            # End the current round and disable further actions
            self.end_round()

    def on_stand(self):
        """
            Triggered when the player clicks the 'Stand' button.
            The player stops drawing cards and the dealer plays their turn.
            """

        # Reveal the dealer's hidden card
        self.game.reveal_dealer_card()
        self.update_dealer_cards(full=True)

        # Dealer draws cards according to Blackjack rules
        drawn = self.game.play_dealer_turn()

        # Add each drawn dealer card to the UI
        for card in drawn:
            self.add_card(self.dealerCardsLayout, card)

        # Update dealer and player total score labels
        self.dealerTotalLabel.setText(f'Dealer: {self.game.dealer_total()}')
        self.playerTotalLabel.setText(f'Player: {self.game.player_total()}')

        # Decide the winner after dealer finishes their turn
        result = self.game.decide_winner()

        # Update player statistics based on the outcome
        self.update_stats(result)

        # Show the round result to the player
        self.feedbackLabel.setText(result)

        # End the current round
        self.end_round()

    def on_new_round(self):
        """
           Triggered when the player clicks the 'New Round' button.
           Resets the game logic and UI for a fresh round.
           """

        # Reset game state and shuffle/redeal cards
        self.game.new_round()

        # Reset the UI elements for a new round
        self.new_round_setup()

    # HELPER METHODS

    def clear_layout(self, layout):
        """
        Remove all widgets from a given layout.

        This is used when starting a new round or updating cards,
        ensuring old card widgets are properly deleted and do not
        remain visible or consume memory.
        """
        while layout.count():  # Continue until the layout is empty
            item = layout.takeAt(0)  # Remove the first item from the layout
            widget = item.widget()  # Get the widget associated with the layout item
            if widget:
                widget.deleteLater()  # Safely delete the widget

    # Get the image path for a given card string
    def card_image_path(self, card):
        """
        Determine and return the file path for a given card image.

        The card is represented as a string
        This method converts that representation into a matching
        filename and folder structure used by the card image assets.
        """

        # Extract the rank (everything except last character)
        # Example: '10♥' -> rank = '10'
        rank = card[:-1]

        # Extract the suit symbol (last character of the string)
        # Example: '10♥' -> suit_symbol = '♥'
        suit_symbol = card[-1]

        # Mapping suit symbols to folder names
        suit_folder_map = {
            '♠': 'spade',
            '♥': 'heart',
            '♦': 'diamond',
            '♣': 'club'
        }

        # Mapping suit symbols to filename naming convention
        suit_name_map = {
            '♠': 'Spades',
            '♥': 'Hearts',
            '♦': 'Diamonds',
            '♣': 'Clubs'
        }

        # Determine folder name (fallback to spade if symbol is unknown)
        folder = suit_folder_map.get(suit_symbol, 'spade')

        # Determine suit name for filename (fallback to Spades)
        suitname = suit_name_map.get(suit_symbol, 'Spades')

        # Construct filename based on asset naming convention
        # Example: cardHearts_10.png
        filename = f'card{suitname}_{rank}.png'

        # Primary expected asset path
        path = asset_path(
            'Assets', 'normal_cards', 'individual', folder, filename
        )

        # Check if the primary path exists
        if os.path.exists(path):
            return path

        # Alternate path check (handles different folder naming styles)
        alt_path = asset_path(
            'Assets', 'normal_cards', 'individual', suitname.lower(), filename
        )

        if os.path.exists(alt_path):
            return alt_path

        # Return None if no valid image path is found
        return None

    def add_card(self, layout, card_text, face_down=False):
        """
           Create a card widget and add it to the specified layout.

           Parameters:
           - layout: The layout (dealer or player) to add the card to
           - card_text: String representation of the card
           - face_down: Whether the card should be displayed face-down
           """

        # Create a QLabel to represent the card visually
        label = QLabel()

        # Set a fixed card size (matches card image proportions)
        label.setFixedSize(96, 144)

        # Allow image to scale inside the label
        label.setScaledContents(True)

        # FACE-DOWN CARD LOGIC (used for dealer's hidden card)
        if face_down or card_text == '??':
            # Path to the card-back image
            back_path = asset_path(
                'Assets', 'normal_cards', 'individual', 'card back', 'cardBackRed.png'
            )

            if os.path.exists(back_path):
                pix = QPixmap(back_path)
                label.setPixmap(
                    pix.scaled(
                        label.width(),
                        label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )
            else:
                # Fallback text if image is missing
                label.setText('XX')

        else:
            # FACE-UP CARD LOGIC
            img_path = self.card_image_path(card_text)

            if img_path and os.path.exists(img_path):
                pix = QPixmap(img_path)
                label.setPixmap(
                    pix.scaled(
                        label.width(),
                        label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )
            else:
                # Fallback: show card text if image cannot be found
                label.setText(card_text)

        # Add the card widget to the specified layout
        layout.addWidget(label)

        # Tag the widget as a card (useful for styling or future logic)
        label.setProperty('card', True)

    def update_dealer_cards(self, full=False):
        """
           Update the dealer's card display.

           Parameters:
           - full: If False, the dealer's first card remains hidden.
                   If True, all dealer cards are revealed.
           """

        # Remove all currently displayed dealer cards
        self.clear_layout(self.dealerCardsLayout)

        # Iterate through the dealer's hand
        for i, card in enumerate(self.game.dealer_hand):
            # Hide the first card unless full reveal is requested
            if i == 0 and not full:
                self.add_card(
                    self.dealerCardsLayout,
                    '??',
                    face_down=True
                )
            else:
                self.add_card(self.dealerCardsLayout, card)

        # Update dealer total label depending on reveal state
        if full:
            self.dealerTotalLabel.setText(
                f'Dealer: {self.game.dealer_total()}'
            )
        else:
            self.dealerTotalLabel.setText('Dealer: ?')

    def new_round_setup(self):
        """
           Reset the UI and game state for a new round.

           This method:
           - Clears all card displays
           - Resets feedback text
           - Deals new cards
           - Updates player and dealer displays
           - Re-enables player controls
           """

        # Clear all previously displayed cards
        self.clear_layout(self.dealerCardsLayout)
        self.clear_layout(self.playerCardsLayout)

        # Clear feedback message from previous round
        self.feedbackLabel.setText('')

        # Deal initial cards via game logic
        self.game.deal_initial_cards()

        # Display player's initial cards
        for card in self.game.player_hand:
            self.add_card(self.playerCardsLayout, card)

        # Update player's total score
        self.playerTotalLabel.setText(
            f'Player: {self.game.player_total()}'
        )

        # Display dealer cards (first card hidden)
        self.update_dealer_cards(full=False)

        # Enable player controls for the new round
        self.hitButton.setEnabled(True)
        self.standButton.setEnabled(True)

        # Reposition feedback label (centered over table)
        self.update_feedback_position()

    def end_round(self):
        """
           Finalize the current round.

           This method is called once a win, loss, or push has been determined.
           It prevents further player interaction until a new round is started.
           """

        # Disable the "Hit" button so the player cannot draw more cards
        self.hitButton.setEnabled(False)

        # Disable the "Stand" button since the round has already concluded
        self.standButton.setEnabled(False)

    def update_stats(self, result_text: str):
        """
            Update player statistics based on the result of the round.

            The result_text is a human-readable string (e.g. "Player wins",
            "Dealer busts", "Push") returned by the game logic. This method
            parses that text and increments the appropriate statistic counter.
            """

        # Check for conditions that count as a player win
        # Player wins if:
        # - The player explicitly wins
        # - The dealer busts
        if 'Player wins' in result_text or 'Dealer busts' in result_text:
            self.stats['wins'] += 1

        # Check for conditions that count as a player loss
        # Player loses if:
        # - Dealer explicitly wins
        # - Player busts
        elif 'Dealer wins' in result_text or 'Player busts' in result_text:
            self.stats['losses'] += 1

        # Check for tie conditions (push)
        # A push occurs when both player and dealer have equal totals
        elif 'Push' in result_text or 'tie' in result_text:
            self.stats['pushes'] += 1

        # Update the statistics labels in the UI
        self.refresh_stats_label()

    def refresh_stats_label(self):
        """
           Refresh the on-screen statistics labels.

           This method ensures that the UI accurately reflects the current
           values stored in the stats dictionary.
           """

        # Update win count label
        self.winLabel.setText(f"win : {self.stats['wins']}")

        # Update loss count label
        self.lossLabel.setText(f"loss: {self.stats['losses']}")

        # Update push (tie) count label
        self.pushLabel.setText(f"push: {self.stats['pushes']}")

    def update_background(self):
        """
           Resize and update the background wallpaper to match the window size.

           This method is typically called after a window resize or during
           initialization to ensure the background image always fills
           the entire application window.
           """

        # Verify that the wallpaper image exists on disk
        if os.path.exists(self.wallpaper_path):
            pix = QPixmap(self.wallpaper_path)

            # Ensure the image loaded correctly
            if not pix.isNull():
                # Scale the image to match the window size
                # Ignore aspect ratio so the entire window is filled
                scaled = pix.scaled(
                    self.size(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                # Apply the scaled background image
                self.bg_label.setPixmap(scaled)

                # Update background geometry to cover the full window
                self.bg_label.setGeometry(0, 0, self.width(), self.height())
        else:
            # Clear the background if the wallpaper image is missing
            self.bg_label.clear()

    def update_spacers(self):
        """
           Adjust layout spacers to maintain visual symmetry.

           This method ensures that the right-side spacer matches the width
           of the statistics widget on the left, keeping the table centered
           in the window.
           """

        try:
            # Confirm both required widgets exist before accessing them
            if hasattr(self, 'rightSpacer') and hasattr(self, 'statsWidget'):

                # Retrieve the current width of the statistics widget
                w = self.statsWidget.width()

                # Fallback width if the widget has not been rendered yet
                if w <= 0:
                    w = 140

                # Set the spacer width to match the stats widget
                self.rightSpacer.setFixedWidth(w)

        except Exception:
            # Silently ignore layout-related errors to prevent UI crashes
            # (Useful during resize events or early initialization)
            pass

    def update_table_size(self):
        """
            Resize the table image so it fits nicely in the center of the window.

            This method dynamically scales the table image based on:
            - Current window size
            - Width of left statistics panel
            - Width of right balancing spacer

            It ensures the table:
            - Never becomes too small
            - Remains centered
            - Preserves aspect ratio
            """

        try:
            # Ensure the table image pixmap exists before attempting to resize
            if not hasattr(self, 'table_pix') or self.table_pix is None:
                return

            # Calculate how much horizontal space is taken by the left stats panel
            left_margin = self.statsWidget.width() if hasattr(self, 'statsWidget') else 0

            # Calculate right-side spacing (mirrors left margin for centering)
            right_margin = self.rightSpacer.width() if hasattr(self, 'rightSpacer') else left_margin

            # Compute the available width for the table in the center area
            # Subtract margins and extra padding (40px)
            available_center_w = max(
                200,
                self.width() - left_margin - right_margin - 40
            )

            # Define a default target width (60% of window width)
            default_target_w = max(200, int(self.width() * 0.6))

            # Choose the smaller of default or available width
            target_w = min(default_target_w, available_center_w)

            # Limit table height to 35% of window height
            max_h = max(120, int(self.height() * 0.35))

            # Abort if calculated width is invalid
            if target_w <= 0:
                return

            # Scale the table image while preserving aspect ratio
            scaled = self.table_pix.scaled(
                target_w,
                max_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # If scaling succeeded, update the QLabel displaying the table
            if not scaled.isNull():
                self.tableLabel.setPixmap(scaled)

                # Fix label size to match the scaled image exactly
                self.tableLabel.setFixedSize(scaled.size())

            # Reposition the feedback label after resizing
            self.update_feedback_position()

        except Exception:
            # Print traceback for debugging resize-related issues
            traceback.print_exc()
            return

    def resizeEvent(self, event):
        """
            Handle window resize events.

            This method is automatically called by Qt whenever
            the window is resized by the user or the system.
            """

        # Call the base class resize handler
        super().resizeEvent(event)

        # Recalculate spacer widths for layout symmetry
        self.update_spacers()

        # Rescale the background wallpaper to fit the new window size
        self.update_background()

        # Resize and reposition the table image
        self.update_table_size()

    def update_feedback_position(self):
        """
           Position and resize the feedback label dynamically.

           The feedback label displays messages like:
           - "Player Wins!"
           - "Dealer Busts"
           - "Push"

           The label is centered over the table image when possible,
           and automatically adjusts its font size to fit within
           a defined area.
           """

        # Determine where the feedback label is currently parented
        parent_widget = self.feedbackLabel.parentWidget()

        # Case 1: Feedback label is placed directly on the table image
        if parent_widget == self.tableLabel:

            # Get the current size of the table image
            tableSize = self.tableLabel.size()

            # Ensure table has valid size before calculations
            if tableSize.width() > 0:

                # Limit feedback text area to 80% width and 40% height of table
                allowed_w = int(tableSize.width() * 0.8)
                allowed_h = int(tableSize.height() * 0.4)

                # Enable automatic word wrapping
                self.feedbackLabel.setWordWrap(True)

                # Start with a reasonably large font
                font_size = 12
                min_font = 8

                fitted = False

                # Reduce font size until the text fits in allowed area
                while font_size >= min_font:
                    f = QFont()
                    f.setPointSize(font_size)
                    f.setBold(True)

                    # Apply font and width constraint
                    self.feedbackLabel.setFont(f)
                    self.feedbackLabel.setFixedWidth(allowed_w)

                    # Resize label based on content
                    self.feedbackLabel.adjustSize()

                    # Get the size the label wants to be
                    sh = self.feedbackLabel.sizeHint()

                    # Check if label fits within allowed bounds
                    if sh.height() <= allowed_h and sh.width() <= allowed_w:
                        fitted = True
                        self.feedbackLabel.setFixedHeight(sh.height())
                        break

                    # Reduce font size and try again
                    font_size -= 1

                # If text never fully fits, cap height at allowed maximum
                if not fitted:
                    self.feedbackLabel.setFixedHeight(allowed_h)

                # Center feedback label over the table image
                x = (tableSize.width() - self.feedbackLabel.width()) // 2
                y = (tableSize.height() - self.feedbackLabel.height()) // 2
                self.feedbackLabel.move(x, y)

        # Case 2: Feedback label is not attached to table image
        else:
            # Center feedback label inside its parent container
            geom = (
                parent_widget.geometry()
                if parent_widget is not None
                else self.tableContainer.geometry()
            )

            x = (geom.width() - self.feedbackLabel.width()) // 2
            y = (geom.height() - self.feedbackLabel.height()) // 2
            self.feedbackLabel.move(x, y)

        # Ensure feedback label appears above other widgets
        self.feedbackLabel.raise_()


if __name__ == '__main__':
    """
       Application entry point.

       This block is executed only when the script is run directly,
       not when it is imported as a module.
    """

    app = QApplication(sys.argv)  # Create the Qt application instance
    # macOS only fix for icons appearing
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
    # Create and display the main application window
    window = MainWindow()
    window.show()
    sys.exit(app.exec())  # Start the Qt event loop and exit cleanly when the app closes
