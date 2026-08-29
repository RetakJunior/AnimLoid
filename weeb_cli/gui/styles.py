"""Modern dark theme stylesheets for AnimLoid GUI."""

DARK_THEME_QSS = """
/* Global Application Styles */
QWidget {
    background-color: #0F1017;
    color: #E2E8F0;
    font-family: 'Segoe UI', 'SF Pro Display', 'Ubuntu', 'Roboto', 'Noto Sans', sans-serif;
    font-size: 13px;
    selection-background-color: #7C5CFF;
    selection-color: #FFFFFF;
}

/* Main Window */
QMainWindow {
    background-color: #0F1017;
}

/* Sidebar */
QFrame#Sidebar {
    background-color: #151722;
    border-right: 1px solid #232738;
    min-width: 210px;
    max-width: 210px;
}

QLabel#LogoTitle {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: bold;
    padding-left: 5px;
}

QLabel#LogoSubtitle {
    color: #7C5CFF;
    font-size: 11px;
    font-weight: 600;
    padding-left: 5px;
}

/* Nav Buttons */
QPushButton.NavButton {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
}

QPushButton.NavButton:hover {
    background-color: #1E2235;
    color: #FFFFFF;
}

QPushButton.NavButton:checked, QPushButton.NavButton[active="true"] {
    background-color: #7C5CFF;
    color: #FFFFFF;
    font-weight: bold;
}

/* Header & Top Bar */
QFrame#TopBar {
    background-color: #151722;
    border-bottom: 1px solid #232738;
    padding: 8px 16px;
}

/* Input Fields */
QLineEdit {
    background-color: #1A1D2B;
    border: 1px solid #2D3247;
    border-radius: 8px;
    color: #F8FAFC;
    padding: 8px 12px;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1px solid #7C5CFF;
    background-color: #202436;
}

QLineEdit::placeholder {
    color: #64748B;
}

/* Buttons */
QPushButton.PrimaryButton {
    background-color: #7C5CFF;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton.PrimaryButton:hover {
    background-color: #9074FF;
}

QPushButton.PrimaryButton:pressed {
    background-color: #6842FF;
}

QPushButton.SecondaryButton {
    background-color: #1E2235;
    color: #CBD5E1;
    border: 1px solid #2E344E;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton.SecondaryButton:hover {
    background-color: #282E47;
    color: #FFFFFF;
    border-color: #3E4668;
}

QPushButton.SecondaryButton:pressed {
    background-color: #181B2A;
}

QPushButton.DangerButton {
    background-color: #EF4444;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton.DangerButton:hover {
    background-color: #F87171;
}

QPushButton.SuccessButton {
    background-color: #10B981;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton.SuccessButton:hover {
    background-color: #34D399;
}

/* ComboBox */
QComboBox {
    background-color: #1A1D2B;
    border: 1px solid #2D3247;
    border-radius: 8px;
    color: #F8FAFC;
    padding: 6px 12px;
    min-width: 130px;
}

QComboBox:hover {
    border-color: #3E4668;
}

QComboBox:focus {
    border-color: #7C5CFF;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #94A3B8;
    margin-right: 8px;
}

QComboBox QAbstractItemView,
QComboBox QListView,
QListView {
    background-color: #1A1D2B;
    border: 1px solid #2D3247;
    selection-background-color: #7C5CFF;
    selection-color: #FFFFFF;
    color: #F8FAFC;
    padding: 4px;
    outline: none;
}

QComboBox QAbstractItemView::item {
    background-color: #1A1D2B;
    color: #F8FAFC;
    padding: 6px 10px;
    min-height: 24px;
    border-radius: 4px;
}

QComboBox QAbstractItemView::item:selected,
QComboBox QAbstractItemView::item:hover {
    background-color: #7C5CFF;
    color: #FFFFFF;
}

/* Cards & Frames */
QFrame.Card {
    background-color: #151824;
    border: 1px solid #232738;
    border-radius: 12px;
}

QFrame.Card:hover {
    border: 1px solid #3E4668;
}

QFrame.AnimeCard {
    background-color: #151824;
    border: 1px solid #222638;
    border-radius: 10px;
}

QFrame.AnimeCard:hover {
    border: 1px solid #7C5CFF;
    background-color: #1C2030;
}

/* ScrollBars */
QScrollBar:vertical {
    background-color: #0F1017;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #282D42;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #7C5CFF;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    background: none;
}

QScrollBar:horizontal {
    background-color: #0F1017;
    height: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background-color: #282D42;
    min-width: 25px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #7C5CFF;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
    background: none;
}

/* ScrollArea */
QScrollArea {
    background-color: transparent;
    border: none;
}

/* Table Widget */
QTableWidget {
    background-color: #151824;
    border: 1px solid #232738;
    border-radius: 8px;
    gridline-color: #232738;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #1E2234;
}

QTableWidget::item:selected {
    background-color: #24293D;
    color: #FFFFFF;
}

QHeaderView::section {
    background-color: #1A1D2B;
    color: #94A3B8;
    padding: 8px;
    font-weight: bold;
    border: none;
    border-bottom: 1px solid #2D3247;
}

/* Progress Bar */
QProgressBar {
    background-color: #1A1D2B;
    border: 1px solid #2A2F45;
    border-radius: 6px;
    text-align: center;
    color: #F8FAFC;
    font-size: 11px;
    font-weight: bold;
    height: 14px;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7C5CFF, stop:1 #00E5FF);
    border-radius: 5px;
}

/* Badges / Tags */
QLabel.Badge {
    background-color: #222638;
    color: #94A3B8;
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 600;
}

QLabel.BadgeAccent {
    background-color: rgba(124, 92, 255, 0.2);
    color: #B5A2FF;
    border: 1px solid rgba(124, 92, 255, 0.4);
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: bold;
}

QLabel.BadgeSuccess {
    background-color: rgba(16, 185, 129, 0.2);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.4);
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: bold;
}

/* CheckBox */
QCheckBox {
    color: #E2E8F0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #3E4668;
    border-radius: 4px;
    background-color: #1A1D2B;
}

QCheckBox::indicator:checked {
    background-color: #7C5CFF;
    border-color: #7C5CFF;
}

/* List Widget */
QListWidget {
    background-color: #151824;
    border: 1px solid #232738;
    border-radius: 8px;
    padding: 4px;
}

QListWidget::item {
    border-radius: 6px;
    padding: 8px 12px;
    margin: 2px 0px;
}

QListWidget::item:hover {
    background-color: #1E2337;
}

QListWidget::item:selected {
    background-color: #7C5CFF;
    color: #FFFFFF;
}

/* Status Bar */
QStatusBar {
    background-color: #151722;
    border-top: 1px solid #232738;
    color: #64748B;
    font-size: 12px;
}
"""

