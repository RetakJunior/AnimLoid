"""Search View for AnimLoid GUI."""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QComboBox, QLabel, QScrollArea, QGridLayout, QFrame, 
    QGraphicsDropShadowEffect, QSizePolicy, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QThreadPool
from PyQt5.QtGui import QPixmap, QColor, QFont, QCursor

from weeb_cli.config import config
from weeb_cli.services.scraper import scraper
from weeb_cli.services.progress import progress_tracker
from weeb_cli.gui.workers import SearchWorker, ImageLoaderWorker


class AnimeCard(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, anime_data: dict, thread_pool: QThreadPool):
        super().__init__()
        self.anime_data = anime_data
        self.thread_pool = thread_pool
        self.setProperty("class", "AnimeCard")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedSize(170, 275)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Poster Image
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(154, 210)
        self.poster_label.setAlignment(Qt.AlignCenter)
        self.poster_label.setStyleSheet("background-color: #1A1D2B; border-radius: 8px; color: #64748B;")
        self.poster_label.setText("Yükleniyor...")
        self.poster_label.setScaledContents(True)
        layout.addWidget(self.poster_label)

        # Title Label
        title = anime_data.get("title") or anime_data.get("name") or "Anime"
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #F8FAFC; font-weight: bold; font-size: 12px;")
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumHeight(34)
        self.title_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.title_label)

        # Year & Type Badges
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(4)
        meta_layout.setContentsMargins(0, 0, 0, 0)

        year = anime_data.get("year")
        if year:
            year_badge = QLabel(str(year))
            year_badge.setStyleSheet("background-color: #232738; color: #94A3B8; border-radius: 4px; padding: 1px 5px; font-size: 10px;")
            meta_layout.addWidget(year_badge)

        anime_type = anime_data.get("type") or "Series"
        type_badge = QLabel(str(anime_type).capitalize())
        type_badge.setStyleSheet("background-color: rgba(124, 92, 255, 0.2); color: #B5A2FF; border-radius: 4px; padding: 1px 5px; font-size: 10px; font-weight: bold;")
        meta_layout.addWidget(type_badge)
        meta_layout.addStretch()

        layout.addLayout(meta_layout)

        # Load cover asynchronously
        cover_url = anime_data.get("cover")
        if cover_url:
            self._image_worker = ImageLoaderWorker(cover_url, parent=self)
            self._image_worker.image_loaded.connect(self._on_image_loaded)
            self._image_worker.image_failed.connect(self._on_image_failed)
            self._image_worker.start()
        else:
            self.poster_label.setText("Afiş Yok")

    def _on_image_loaded(self, url, pixmap):
        if not pixmap.isNull():
            self.poster_label.setPixmap(pixmap.scaled(
                self.poster_label.size(), 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            ))

    def _on_image_failed(self, url):
        self.poster_label.setText("Afiş Yok")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.anime_data)


class SearchView(QWidget):
    anime_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool.globalInstance()
        self.search_worker = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Search Bar Row
        search_row = QHBoxLayout()
        search_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Anime adı arayın... (Örn: Solo Leveling, Bleach, Attack on Titan)")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.returnPressed.connect(self.start_search)
        search_row.addWidget(self.search_input, stretch=4)

        # Source Provider Dropdown
        self.source_combo = QComboBox()
        providers = scraper.get_available_sources()
        current_source = config.get("scraping_source", "animecix")
        
        current_index = 0
        for i, p in enumerate(providers):
            flag = "🇹🇷" if p.get("lang") == "tr" else "🌐"
            display_name = f"{flag} {p['name'].capitalize()}"
            self.source_combo.addItem(display_name, p["name"])
            if p["name"] == current_source:
                current_index = i

        self.source_combo.setCurrentIndex(current_index)
        self.source_combo.currentIndexChanged.connect(self._on_source_changed)
        search_row.addWidget(self.source_combo, stretch=1)

        # Search Button
        self.search_btn = QPushButton("🔍 Ara")
        self.search_btn.setProperty("class", "PrimaryButton")
        self.search_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.search_btn.clicked.connect(self.start_search)
        search_row.addWidget(self.search_btn)

        main_layout.addLayout(search_row)

        # Recent Searches Row
        self.recent_layout = QHBoxLayout()
        self.recent_layout.setSpacing(8)
        self.recent_label = QLabel("Son Aramalar:")
        self.recent_label.setStyleSheet("color: #64748B; font-size: 11px;")
        self.recent_layout.addWidget(self.recent_label)
        self.recent_container = QWidget()
        self.recent_container_layout = QHBoxLayout(self.recent_container)
        self.recent_container_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_container_layout.setSpacing(6)
        self.recent_layout.addWidget(self.recent_container)
        self.recent_layout.addStretch()
        main_layout.addLayout(self.recent_layout)

        # Status & Loading Bar
        self.status_label = QLabel("Keşfetmek istediğiniz animeyi arayın.")
        self.status_label.setStyleSheet("color: #94A3B8; font-size: 12px; margin-top: 4px;")
        main_layout.addWidget(self.status_label)

        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)  # Infinite indeterminate
        self.loading_bar.setFixedHeight(3)
        self.loading_bar.hide()
        main_layout.addWidget(self.loading_bar)

        # Scroll Area for Results Grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 8, 0, 8)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(self.scroll_area, stretch=1)

        self.refresh_recent_searches()

    def refresh_recent_searches(self):
        # Clear existing
        while self.recent_container_layout.count():
            item = self.recent_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        history = progress_tracker.get_search_history()
        if not history:
            self.recent_label.hide()
            return
        
        self.recent_label.show()
        for query in history[:5]:
            btn = QPushButton(query)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1E2235;
                    color: #94A3B8;
                    border: 1px solid #2A2F45;
                    border-radius: 6px;
                    padding: 2px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #282E47;
                    color: #FFFFFF;
                    border-color: #7C5CFF;
                }
            """)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.clicked.connect(lambda checked, q=query: self._search_recent(q))
            self.recent_container_layout.addWidget(btn)

    def _search_recent(self, query):
        self.search_input.setText(query)
        self.start_search()

    def _on_source_changed(self):
        source = self.source_combo.currentData()
        if source:
            config.set("scraping_source", source)

    def start_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        progress_tracker.add_search_history(query)
        self.refresh_recent_searches()

        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        source = self.source_combo.currentData()
        self.status_label.setText(f"'{query}' aranıyor ({source.capitalize()})...")
        self.loading_bar.show()
        self.search_btn.setEnabled(False)

        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()

        self.search_worker = SearchWorker(query, source)
        self.search_worker.results_ready.connect(self._on_results_ready)
        self.search_worker.error_occurred.connect(self._on_search_error)
        self.search_worker.start()

    def _on_results_ready(self, results):
        self.loading_bar.hide()
        self.search_btn.setEnabled(True)

        if not results:
            self.status_label.setText("Sonuç bulunamadı. Başka bir anime adı veya farklı bir kaynak deneyebilirsiniz.")
            return

        self.status_label.setText(f"{len(results)} sonuç bulundu:")

        columns = 5
        for i, anime in enumerate(results):
            row = i // columns
            col = i % columns
            card = AnimeCard(anime, self.thread_pool)
            card.clicked.connect(self._on_card_clicked)
            self.grid_layout.addWidget(card, row, col)

    def _on_search_error(self, err_msg):
        self.loading_bar.hide()
        self.search_btn.setEnabled(True)
        self.status_label.setText(f"Hata oluştu: {err_msg}")

    def _on_card_clicked(self, anime_data):
        self.anime_selected.emit(anime_data)

