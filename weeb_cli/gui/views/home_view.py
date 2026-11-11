"""Desktop discovery dashboard and personalized continue-watching section."""

from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThreadPool
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QScrollArea, QGridLayout, QFrame, QSizePolicy,
)

from weeb_cli.gui.views.search_view import AnimeCard
from weeb_cli.gui.workers import RecommendationsWorker, start_background_worker
from weeb_cli.services.progress import progress_tracker
from weeb_cli.services.recommendations import SORT_OPTIONS


SORT_LABELS = {
    "TRENDING_DESC": "Şu an trend",
    "POPULARITY_DESC": "Popüler",
    "SCORE_DESC": "En yüksek puanlı",
}


class HomeView(QWidget):
    search_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool.globalInstance()
        self.recommendations_worker = None
        self._queued_refresh = None
        self._results = []
        self._columns = 0
        self._build_ui()
        QTimer.singleShot(0, self.refresh_recommendations)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        heading = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        title = QLabel("Ana Sayfa")
        title.setObjectName("HomeTitle")
        subtitle = QLabel("İzlemeye devam et veya yeni bir anime keşfet.")
        subtitle.setObjectName("HomeSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        heading.addLayout(title_box)
        heading.addStretch()
        root.addLayout(heading)

        quick_search = QHBoxLayout()
        quick_search.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Anime adını yazıp hızlıca ara…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.returnPressed.connect(self._submit_search)
        quick_search.addWidget(self.search_input, stretch=1)
        self.search_button = QPushButton("⌕  Anime Ara")
        self.search_button.setProperty("class", "PrimaryButton")
        self.search_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.search_button.clicked.connect(self._submit_search)
        quick_search.addWidget(self.search_button)
        root.addLayout(quick_search)

        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_scroll.setFrameShape(QFrame.NoFrame)
        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 2, 0, 8)
        self.content_layout.setSpacing(14)
        self.content_scroll.setWidget(self.content)
        root.addWidget(self.content_scroll, stretch=1)

        self.continue_section = QWidget()
        continue_layout = QVBoxLayout(self.continue_section)
        continue_layout.setContentsMargins(0, 0, 0, 0)
        continue_layout.setSpacing(8)
        continue_header = QHBoxLayout()
        continue_title = QLabel("İzlemeye Devam Et")
        continue_title.setObjectName("SectionTitle")
        continue_header.addWidget(continue_title)
        continue_header.addStretch()
        continue_layout.addLayout(continue_header)
        self.continue_row = QHBoxLayout()
        self.continue_row.setSpacing(8)
        continue_layout.addLayout(self.continue_row)
        self.content_layout.addWidget(self.continue_section)

        rec_header = QHBoxLayout()
        rec_title_box = QVBoxLayout()
        rec_title_box.setSpacing(2)
        rec_title = QLabel("Sana Göre")
        rec_title.setObjectName("SectionTitle")
        self.rec_status = QLabel("Öneriler yükleniyor…")
        self.rec_status.setObjectName("HomeSubtitle")
        rec_title_box.addWidget(rec_title)
        rec_title_box.addWidget(self.rec_status)
        rec_header.addLayout(rec_title_box)
        rec_header.addStretch()

        self.sort_combo = QComboBox()
        for sort in SORT_OPTIONS:
            self.sort_combo.addItem(SORT_LABELS[sort], sort)
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        rec_header.addWidget(self.sort_combo)

        self.refresh_button = QPushButton("⟳ Yenile")
        self.refresh_button.setProperty("class", "SecondaryButton")
        self.refresh_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.refresh_button.clicked.connect(self.refresh_recommendations)
        rec_header.addWidget(self.refresh_button)
        self.content_layout.addLayout(rec_header)

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.content_layout.addWidget(self.grid_container)
        self.content_layout.addStretch(1)

        self._refresh_continue_watching()

    def refresh_recommendations(self, force_refresh=True):
        if self.recommendations_worker and self.recommendations_worker.isRunning():
            self._queued_refresh = (self.sort_combo.currentData(), force_refresh)
            return
        sort = self.sort_combo.currentData()
        self.rec_status.setText("Trend animeler getiriliyor…")
        self.refresh_button.setEnabled(False)
        self.recommendations_worker = RecommendationsWorker(sort, force_refresh)
        self.recommendations_worker.recommendations_ready.connect(self._on_recommendations_ready, Qt.QueuedConnection)
        start_background_worker(self, self.recommendations_worker)

    def _on_recommendations_ready(self, items):
        if self.sender() is not self.recommendations_worker:
            return
        self.refresh_button.setEnabled(True)
        self._results = items or []
        offline = bool(self._results) and all(item.get("source") == "offline" for item in self._results)
        if offline:
            self.rec_status.setText("Bağlantı yok; öneriler çevrimdışı listeyle gösteriliyor.")
        else:
            self.rec_status.setText(f"{len(self._results)} güncel öneri · Bir anime seçince seçili kaynakta arama açılır.")
        self._render_cards()
        if self._queued_refresh:
            sort, force_refresh = self._queued_refresh
            self._queued_refresh = None
            if sort != self.sort_combo.currentData():
                self.sort_combo.blockSignals(True)
                self.sort_combo.setCurrentIndex(max(0, self.sort_combo.findData(sort)))
                self.sort_combo.blockSignals(False)
            QTimer.singleShot(0, lambda: self.refresh_recommendations(force_refresh))

    def _on_sort_changed(self, _index):
        self.refresh_recommendations(force_refresh=True)

    def _refresh_continue_watching(self):
        while self.continue_row.count():
            item = self.continue_row.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        entries = progress_tracker.get_in_progress_anime()[:5]
        self.continue_section.setVisible(bool(entries))
        for entry in entries:
            title = entry.get("title") or entry.get("slug") or "Anime"
            last = entry.get("last_watched", 0)
            total = entry.get("total_episodes", 0)
            detail = f"Bölüm {last}" + (f" / {total}" if total else "")
            button = QPushButton(f"▶  {title}\n     {detail}")
            button.setObjectName("ContinueButton")
            button.setCursor(QCursor(Qt.PointingHandCursor))
            button.setMinimumHeight(56)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button.clicked.connect(lambda checked=False, name=title: self.search_requested.emit(name))
            self.continue_row.addWidget(button)

    def _submit_search(self):
        query = self.search_input.text().strip()
        if query:
            self.search_requested.emit(query)

    def _column_count(self):
        available = max(1, self.content_scroll.viewport().width())
        return max(1, (available + 12) // 190)

    def _render_cards(self):
        self._columns = self._column_count()
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for i, anime in enumerate(self._results):
            card = AnimeCard(anime, self.thread_pool)
            card.clicked.connect(self._on_card_clicked)
            self.grid_layout.addWidget(card, i // self._columns, i % self._columns)

        if not self._results:
            empty = QLabel("Öneri bulunamadı. Üstteki arama kutusunu kullanabilirsin.")
            empty.setObjectName("HomeSubtitle")
            self.grid_layout.addWidget(empty, 0, 0)

    def _on_card_clicked(self, anime):
        title = anime.get("title") or anime.get("name") or ""
        if title:
            self.search_requested.emit(title)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._results:
            QTimer.singleShot(0, self._reflow_if_needed)

    def _reflow_if_needed(self):
        if self._results and self._column_count() != self._columns:
            self._render_cards()
