"""Main application window for AnimLoid GUI."""

import os
import sys
from pathlib import Path

# This module can also be launched directly with ``python -m``.  Configure
# the Qt platform before importing any PyQt module; an explicit environment
# value is always left untouched.
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QStackedWidget, QPushButton, QLabel, QFrame, QStatusBar, QButtonGroup
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor

from weeb_cli.config import config
from weeb_cli.gui.styles import DARK_THEME_QSS
from weeb_cli.gui.views.home_view import HomeView
from weeb_cli.gui.views.search_view import SearchView
from weeb_cli.gui.views.detail_view import DetailView
from weeb_cli.gui.views.history_view import HistoryView
from weeb_cli.gui.views.downloads_view import DownloadsView
from weeb_cli.gui.views.settings_view import SettingsView


class AnimLoidApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AnimLoid - Anime İzle & İndir")
        self.resize(1080, 700)
        self.setMinimumSize(900, 560)

        # Set App Icon
        self._load_app_icon()

        # Central widget and layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create Sidebar and Content Stack
        self.nav_buttons = {}
        self._last_page_index = 0
        self._create_sidebar()
        self._create_content_stack()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("AnimLoid hazır. Keyifli seyirler!")

    def _load_app_icon(self):
        # Look for logo file in weeb_landing/logo or resources
        base_dir = Path(__file__).resolve().parent.parent.parent
        possible_icons = [
            base_dir / "weeb_landing" / "logo" / "favicon-32x32.png",
            base_dir / "weeb_landing" / "logo" / "512x512.webp",
            base_dir / "weeb_landing" / "logo" / "favicon.ico",
        ]
        for icon_path in possible_icons:
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
                break

    def _create_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(6)

        # Brand / Logo Header
        brand_layout = QHBoxLayout()
        brand_layout.setContentsMargins(4, 0, 4, 16)
        brand_layout.setSpacing(10)

        logo_label = QLabel("A")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFixedSize(28, 28)
        logo_label.setStyleSheet("background: #2563eb; color: white; border-radius: 6px; font-size: 15px; font-weight: bold;")
        brand_layout.addWidget(logo_label)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)

        app_title = QLabel("AnimLoid")
        app_title.setObjectName("LogoTitle")
        title_box.addWidget(app_title)

        app_sub = QLabel("v2.7.4 • Anime izle")
        app_sub.setObjectName("LogoSubtitle")
        title_box.addWidget(app_sub)

        brand_layout.addLayout(title_box)
        sidebar_layout.addLayout(brand_layout)

        # Navigation Button Group
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_home = self._create_nav_btn("⌂  Ana Sayfa", 0)
        self.btn_search = self._create_nav_btn("⌕  Anime Ara", 1)
        self.btn_history = self._create_nav_btn("◷  İzlediklerim", 3)
        self.btn_downloads = self._create_nav_btn("⇩  İndirmeler", 4)
        self.btn_settings = self._create_nav_btn("⚙  Ayarlar", 5)

        sidebar_layout.addWidget(self.btn_home)
        sidebar_layout.addWidget(self.btn_search)
        sidebar_layout.addWidget(self.btn_history)
        sidebar_layout.addWidget(self.btn_downloads)
        sidebar_layout.addWidget(self.btn_settings)

        sidebar_layout.addStretch()

        # Bottom info card in sidebar
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: #17191d;
                border: 1px solid #303238;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(8, 8, 8, 8)
        info_layout.setSpacing(4)

        info_t = QLabel("📺 MPV & Aria2")
        info_t.setStyleSheet("color: #FFFFFF; font-size: 11px; font-weight: bold;")
        info_layout.addWidget(info_t)

        info_d = QLabel("Yayın ve indirme")
        info_d.setStyleSheet("color: #64748B; font-size: 10px;")
        info_layout.addWidget(info_d)

        sidebar_layout.addWidget(info_card)

        self.main_layout.addWidget(self.sidebar)

    def _create_nav_btn(self, text: str, page_idx: int) -> QPushButton:
        btn = QPushButton(text)
        btn.setProperty("class", "NavButton")
        btn.setCheckable(True)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.clicked.connect(lambda: self._switch_page(page_idx))
        self.nav_group.addButton(btn)
        self.nav_buttons[page_idx] = btn
        if page_idx == 0:
            btn.setChecked(True)
        return btn

    def _create_content_stack(self):
        self.stack = QStackedWidget()

        # 0: Home / discovery
        self.home_view = HomeView()
        self.home_view.search_requested.connect(self._on_home_search)
        self.stack.addWidget(self.home_view)

        # 1: Search View
        self.search_view = SearchView()
        self.search_view.anime_selected.connect(self._open_anime_detail)
        self.stack.addWidget(self.search_view)

        # 2: Detail View
        self.detail_view = DetailView()
        self.detail_view.back_clicked.connect(self._on_detail_back)
        self.detail_view.episode_watched.connect(self._on_episode_watched)
        self.stack.addWidget(self.detail_view)

        # 3: History View
        self.history_view = HistoryView()
        self.history_view.anime_selected.connect(self._open_anime_detail)
        self.stack.addWidget(self.history_view)

        # 4: Downloads View
        self.downloads_view = DownloadsView()
        self.stack.addWidget(self.downloads_view)

        # 5: Settings View
        self.settings_view = SettingsView()
        self.stack.addWidget(self.settings_view)

        self.main_layout.addWidget(self.stack, stretch=1)

    def _switch_page(self, page_idx: int):
        self.stack.setCurrentIndex(page_idx)
        if page_idx == 0:
            self.home_view._refresh_continue_watching()
            self.home_view.refresh_recommendations(force_refresh=False)
        elif page_idx == 3:
            self.history_view.refresh_history()
        elif page_idx == 4:
            self.downloads_view.refresh_queue()

    def _open_anime_detail(self, anime_data: dict):
        current_index = self.stack.currentIndex()
        if current_index != 2:
            self._last_page_index = current_index
        source = anime_data.get("source") or config.get("scraping_source", "animecix")
        self.detail_view.load_anime(anime_data, source)
        self.stack.setCurrentIndex(2)

    def _on_home_search(self, title: str):
        self._sync_search_source()
        self.btn_search.setChecked(True)
        self.stack.setCurrentIndex(1)
        self.search_view.search_title(title)

    def _sync_search_source(self):
        source = config.get("scraping_source", "animecix")
        source_index = self.search_view.source_combo.findData(source)
        if source_index >= 0:
            self.search_view.source_combo.setCurrentIndex(source_index)

    def _on_detail_back(self):
        # Return to the screen that opened the selected anime.
        self._sync_search_source()
        self.stack.setCurrentIndex(self._last_page_index)
        button = self.nav_buttons.get(self._last_page_index)
        if button:
            button.setChecked(True)

    def _on_episode_watched(self, slug: str, ep_num: int):
        self.status_bar.showMessage(f"Bölüm {ep_num} izleme listesine kaydedildi.", 4000)


def run_gui():
    try:
        # Enable High DPI scaling
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        app = QApplication(sys.argv)
        app.setStyleSheet(DARK_THEME_QSS)

        window = AnimLoidApp()
        window.show()

        sys.exit(app.exec_())
    except Exception as e:
        print(f"\n⚠️  Grafik arayüz (GUI) başlatılamadı ({e}).")
        print("➡️  Komut satırı (CLI) moduna geçiliyor...\n")
        from weeb_cli.main import app as cli_app
        cli_app()


if __name__ == "__main__":
    run_gui()
