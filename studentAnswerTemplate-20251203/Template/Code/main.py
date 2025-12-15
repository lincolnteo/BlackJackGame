from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, \
    QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
import sys
import os
import traceback
# this project should use a modular approach - try to keep UI logic and game logic separate
from game_logic import Game21


# get asset paths
def asset_path(*parts):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', *parts))


#  create styled QLabel
def make_label(text='', bold=False, color='white'):
    lbl = QLabel(text)
    style = f"color: {color};"
    if bold:
        style += " font-weight: bold;"
    lbl.setStyleSheet(style)
    return lbl


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Game of Blackjack 21')  # Set window title
        self.move(200, 200)  # Set initial position
        self.setFixedSize(600, 600)  # Set fixed window size
        self.game = Game21()  # Initialize game logic
        self.stats = {'wins': 0, 'losses': 0, 'pushes': 0}  # Player statistics
        self._font_bold = True  # Font style for labels
        self.initUI()  # Initialize UI

    def initUI(self):
        central = QWidget()
        self.setCentralWidget(central)
        # BACKGROUND WALLPAPER
        self.wallpaper_path = asset_path('Assets', 'Backgrounds', 'background_1.png')
        self.bg_label = QLabel(central)
        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.bg_label.lower()
        self.wallpaper_pix = None
        if os.path.exists(self.wallpaper_path):
            wp = QPixmap(self.wallpaper_path)
            if not wp.isNull():
                self.wallpaper_pix = wp
                self.bg_label.setPixmap(wp.scaled(self.width(), self.height(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                                  Qt.TransformationMode.SmoothTransformation))
        # MAIN LAYOUT
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        central.setLayout(self.mainLayout)
        # DEALER AREA
        self.dealerLabel = make_label('Dealer', bold=self._font_bold)
        self.dealerCardsLayout = QHBoxLayout()
        self.dealerTotalLabel = make_label('Dealer: ?')
        self.mainLayout.addWidget(self.dealerLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.mainLayout.addLayout(self.dealerCardsLayout)
        self.mainLayout.addWidget(self.dealerTotalLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        # TABLE AREA
        self.tableContainer = QWidget()
        self.tableContainer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        tableLayout = QVBoxLayout()
        tableLayout.setContentsMargins(0, 0, 0, 0)
        self.tableContainer.setLayout(tableLayout)
        #  FEEDBACK LABEL
        self.feedbackLabel = QLabel('')
        self.feedbackLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedbackLabel.setStyleSheet('color: white; font-weight: bold; background-color: rgba(0,0,0,0);')
        self.feedbackLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        tableLayout.addStretch()
        #  TABLE IMAGE
        table_path = asset_path('Assets', 'Tables', 'table_green.png')
        self.table_pix = None
        self.tableLabel = QLabel()
        self.tableLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if os.path.exists(table_path):
            pix = QPixmap(table_path)
            if not pix.isNull():
                self.table_pix = pix
                self.update_table_size()
                self.feedbackLabel.setParent(self.tableLabel)
        else:
            self.tableLabel.setText('[Table]')
            self.feedbackLabel.setParent(self.tableContainer)
        tableLayout.addWidget(self.tableLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        tableLayout.addStretch()
        #  STATISTICS WIDGET
        self.statsWidget = QWidget()
        statsLayout = QVBoxLayout()
        statsLayout.setContentsMargins(6, 6, 6, 6)
        self.statsWidget.setLayout(statsLayout)
        statsLayout.addWidget(make_label('Player Statistic:', bold=True))
        self.winLabel = make_label('win : 0')
        self.lossLabel = make_label('loss: 0')
        self.pushLabel = make_label('push: 0')
        statsLayout.addWidget(self.winLabel)
        statsLayout.addWidget(self.lossLabel)
        statsLayout.addWidget(self.pushLabel)
        self.statsWidget.setFixedWidth(140)
        # MID ROW WITH STATS AND TABLE
        midRow = QWidget()
        midLayout = QHBoxLayout()
        midLayout.setContentsMargins(0, 0, 0, 0)
        midRow.setLayout(midLayout)
        midLayout.addWidget(self.statsWidget, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # center table area
        centerWrapper = QWidget()
        centerLayout = QHBoxLayout()
        centerLayout.setContentsMargins(0, 0, 0, 0)
        centerWrapper.setLayout(centerLayout)
        centerWrapper.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        centerLayout.addStretch(1)
        centerLayout.addWidget(self.tableContainer, alignment=Qt.AlignmentFlag.AlignCenter)
        centerLayout.addStretch(1)
        # right spacer to balance stats on left
        self.rightSpacer = QWidget()
        self.rightSpacer.setFixedWidth(self.statsWidget.width())

        midLayout.addWidget(centerWrapper, stretch=1)
        midLayout.addWidget(self.rightSpacer)
        self.mainLayout.addWidget(midRow)
        # Adjust spacers and background
        self.update_spacers()
        self.update_background()
        self.update_table_size()
        # PLAYER AREA
        self.playerLabel = make_label('Player', bold=self._font_bold)
        self.playerCardsLayout = QHBoxLayout()
        self.playerTotalLabel = make_label('Player: 0')
        self.mainLayout.addWidget(self.playerLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.mainLayout.addLayout(self.playerCardsLayout)
        self.mainLayout.addWidget(self.playerTotalLabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        # BUTTONS
        self.buttonsLayout = QHBoxLayout()
        self.hitButton = QPushButton('Hit')
        self.standButton = QPushButton('Stand')
        self.newRoundButton = QPushButton('New Round')
        self.hitButton.clicked.connect(self.on_hit)
        self.standButton.clicked.connect(self.on_stand)
        self.newRoundButton.clicked.connect(self.on_new_round)
        self.buttonsLayout.addWidget(self.hitButton)
        self.buttonsLayout.addWidget(self.standButton)
        self.buttonsLayout.addWidget(self.newRoundButton)
        self.mainLayout.addLayout(self.buttonsLayout)

        self.new_round_setup()

    def on_hit(self):
        # Player takes a card
        card = self.game.player_hit()
        self.add_card(self.playerCardsLayout, card)
        self.playerTotalLabel.setText(f'Player: {self.game.player_total()}')
        # Check for bust
        if self.game.player_total() > 21:
            self.update_dealer_cards(full=True)
            result = self.game.decide_winner()
            self.update_stats(result)
            self.feedbackLabel.setText(result)
            self.end_round()

    def on_stand(self):
        self.game.reveal_dealer_card()  # Reveal dealer hidden card
        self.update_dealer_cards(full=True)
        drawn = self.game.play_dealer_turn()
        for card in drawn:
            self.add_card(self.dealerCardsLayout, card)
        self.dealerTotalLabel.setText(f'Dealer: {self.game.dealer_total()}')
        self.playerTotalLabel.setText(f'Player: {self.game.player_total()}')
        result = self.game.decide_winner()
        self.update_stats(result)
        self.feedbackLabel.setText(result)
        self.end_round()

    def on_new_round(self):
        # Start a new round
        self.game.new_round()
        self.new_round_setup()

    # HELPER METHODS

    def clear_layout(self, layout):
        # Remove all widgets from a layout
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # Get the image path for a given card string
    def card_image_path(self, card):
        # Parse rank and suit
        rank = card[:-1]
        suit_symbol = card[-1]
        suit_folder_map = {'♠': 'spade', '♥': 'heart', '♦': 'diamond', '♣': 'club'}
        suit_name_map = {'♠': 'Spades', '♥': 'Hearts', '♦': 'Diamonds', '♣': 'Clubs'}
        # Determine folder and filename
        folder = suit_folder_map.get(suit_symbol, 'spade')
        suitname = suit_name_map.get(suit_symbol, 'Spades')
        filename = f'card{suitname}_{rank}.png'
        path = asset_path('Assets', 'normal_cards', 'individual', folder, filename)
        # Check both possible paths
        if os.path.exists(path):
            return path
        alt_path = asset_path('Assets', 'normal_cards', 'individual', suitname.lower(), filename)
        if os.path.exists(alt_path):
            return alt_path
        return None

    def add_card(self, layout, card_text, face_down=False):
        # Create a QLabel showing the card value and add it to the chosen layout.
        label = QLabel()
        label.setFixedSize(96, 144)
        label.setScaledContents(True)
        # retrieve card image
        if face_down or card_text == '??':
            back_path = asset_path('Assets', 'normal_cards', 'individual', 'card back', 'cardBackRed.png')
            if os.path.exists(back_path):
                pix = QPixmap(back_path)
                label.setPixmap(pix.scaled(label.width(), label.height(), Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation))
            else:
                label.setText('XX')
        else:
            # show face-up card
            img_path = self.card_image_path(card_text)
            if img_path and os.path.exists(img_path):
                pix = QPixmap(img_path)
                label.setPixmap(pix.scaled(label.width(), label.height(), Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation))
            else:
                label.setText(card_text)
        layout.addWidget(label)
        label.setProperty('card', True)

    def update_dealer_cards(self, full=False):
        # Show dealer cards; hide the first card until revealed
        self.clear_layout(self.dealerCardsLayout)
        for i, card in enumerate(self.game.dealer_hand):
            if i == 0 and not full:
                self.add_card(self.dealerCardsLayout, '??', face_down=True)  # face-down
            else:
                self.add_card(self.dealerCardsLayout, card)
        # TODO: update relevant labels in response to dealer actions. Remove pass when complete
        if full:
            self.dealerTotalLabel.setText(f'Dealer: {self.game.dealer_total()}')
        else:
            self.dealerTotalLabel.setText('Dealer: ?')

    def new_round_setup(self):
        # Prepare UI for a new round
        self.clear_layout(self.dealerCardsLayout)
        self.clear_layout(self.playerCardsLayout)
        self.feedbackLabel.setText('')
        self.game.deal_initial_cards()
        # Show initial player cards
        for card in self.game.player_hand:
            self.add_card(self.playerCardsLayout, card)
        self.playerTotalLabel.setText(f'Player: {self.game.player_total()}')
        # Show initial dealer cards
        self.update_dealer_cards(full=False)
        self.hitButton.setEnabled(True)
        self.standButton.setEnabled(True)
        self.update_feedback_position()

    def end_round(self):
        # Disable buttons at round end
        self.hitButton.setEnabled(False)
        self.standButton.setEnabled(False)

    def update_stats(self, result_text: str):
        # Update win/loss/push statistics based on result text
        if 'Player wins' in result_text or 'Dealer busts' in result_text:
            self.stats['wins'] += 1
        elif 'Dealer wins' in result_text or 'Player busts' in result_text:
            self.stats['losses'] += 1
        elif 'Push' in result_text or 'tie' in result_text:
            self.stats['pushes'] += 1
        self.refresh_stats_label()

    def refresh_stats_label(self):
        # Update the statistics labels
        self.winLabel.setText(f"win : {self.stats['wins']}")
        self.lossLabel.setText(f"loss: {self.stats['losses']}")
        self.pushLabel.setText(f"push: {self.stats['pushes']}")

    def update_background(self):
        # Update the background wallpaper to fit the window size
        if os.path.exists(self.wallpaper_path):
            pix = QPixmap(self.wallpaper_path)
            if not pix.isNull():
                scaled = pix.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
                self.bg_label.setPixmap(scaled)
                self.bg_label.setGeometry(0, 0, self.width(), self.height())
        else:
            self.bg_label.clear()

    def update_spacers(self):
        # Adjust the right spacer width to match stats widget width
        try:
            if hasattr(self, 'rightSpacer') and hasattr(self, 'statsWidget'):
                w = self.statsWidget.width()
                if w <= 0:
                    w = 140
                self.rightSpacer.setFixedWidth(w)
        except Exception:
            pass

    def update_table_size(self):
        # Resize the table image to fit within the available space
        try:
            # Ensure table_pix is available
            if not hasattr(self, 'table_pix') or self.table_pix is None:
                return
            # Calculate available width
            left_margin = self.statsWidget.width() if hasattr(self, 'statsWidget') else 0
            right_margin = self.rightSpacer.width() if hasattr(self, 'rightSpacer') else left_margin
            available_center_w = max(200, self.width() - left_margin - right_margin - 40)
            default_target_w = max(200, int(self.width() * 0.6))
            target_w = min(default_target_w, available_center_w)
            max_h = max(120, int(self.height() * 0.35))
            if target_w <= 0:
                return
            scaled = self.table_pix.scaled(target_w, max_h, Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation)
            if not scaled.isNull():
                self.tableLabel.setPixmap(scaled)
                self.tableLabel.setFixedSize(scaled.size())
            self.update_feedback_position()
        except Exception:
            traceback.print_exc()
            return

    def resizeEvent(self, event):
        # Handle window resize events
        super().resizeEvent(event)
        self.update_spacers()
        self.update_background()
        self.update_table_size()

    def update_feedback_position(self):
        # Adjust feedback label position and size based on parent widget
        parent_widget = self.feedbackLabel.parentWidget()
        if parent_widget == self.tableLabel:
            tableSize = self.tableLabel.size()
            # Try to fit within 80% width and 40% height of table
            if tableSize.width() > 0:
                allowed_w = int(tableSize.width() * 0.8)
                allowed_h = int(tableSize.height() * 0.4)
                self.feedbackLabel.setWordWrap(True)
                font_size = 12
                min_font = 8
                fitted = False
                while font_size >= min_font:
                    f = QFont()
                    f.setPointSize(font_size)
                    f.setBold(True)
                    self.feedbackLabel.setFont(f)
                    self.feedbackLabel.setFixedWidth(allowed_w)
                    self.feedbackLabel.adjustSize()
                    sh = self.feedbackLabel.sizeHint()
                    # Check if it fits
                    if sh.height() <= allowed_h and sh.width() <= allowed_w:
                        fitted = True
                        self.feedbackLabel.setFixedHeight(sh.height())
                        break
                    font_size -= 1
                    # try smaller font
                if not fitted:
                    self.feedbackLabel.setFixedHeight(allowed_h)
                x = (tableSize.width() - self.feedbackLabel.width()) // 2
                y = (tableSize.height() - self.feedbackLabel.height()) // 2
                self.feedbackLabel.move(x, y)
        else:
            # Center in table container
            geom = (parent_widget.geometry() if parent_widget is not None else self.tableContainer.geometry())
            x = (geom.width() - self.feedbackLabel.width()) // 2
            y = (geom.height() - self.feedbackLabel.height()) // 2
            self.feedbackLabel.move(x, y)
        self.feedbackLabel.raise_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # macOS only fix for icons appearing
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
