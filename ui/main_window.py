from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QLineEdit, QWidget, QLabel, QSlider, 
                             QSplitter, QTreeWidget, QTreeWidgetItem, QMessageBox,
                             QInputDialog, QProgressBar)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon
from player.music_player import MusicPlayer
from player.recommendation_engine import RecommendationEngine
from api.sample_api import sample_api
from utils.config import Config
import asyncio

class MainWindow(QMainWindow):
    update_progress = pyqtSignal(int)

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.setWindowTitle("PyMusicPlayer")
        self.setGeometry(100, 100, 1200, 800)
        self.load_stylesheet()

        self.music_player = MusicPlayer(self.config)
        self.recommendation_engine = RecommendationEngine()

        self.setup_ui()
        self.setup_connections()

        # Sleep timer
        self.sleep_timer = QTimer()
        self.sleep_timer.timeout.connect(self.music_player.stop)

        # Update progress bar
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress_bar)
        self.progress_timer.start(1000)  # Update every second

    def load_stylesheet(self) -> None:
        with open("assets/style.qss", "r") as f:
            self.setStyleSheet(f.read())

    def setup_ui(self) -> None:
        main_layout = QHBoxLayout()

        # Left sidebar
        left_sidebar = self.create_left_sidebar()

        # Main content area
        main_content = self.create_main_content()

        # Player controls
        player_controls = self.create_player_controls()

        # Combine layouts
        main_layout.addLayout(left_sidebar, 1)
        main_layout.addLayout(main_content, 4)

        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(self.progress_bar)
        bottom_layout.addLayout(player_controls)
        bottom_layout.addWidget(self.volume_slider)
        bottom_layout.addWidget(self.now_playing)

        overall_layout = QVBoxLayout()
        overall_layout.addLayout(main_layout)
        overall_layout.addLayout(bottom_layout)

        central_widget = QWidget()
        central_widget.setLayout(overall_layout)
        self.setCentralWidget(central_widget)

    def create_left_sidebar(self) -> QVBoxLayout:
        left_sidebar = QVBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for music...")
        left_sidebar.addWidget(self.search_bar)

        self.library_tree = QTreeWidget()
        self.library_tree.setHeaderHidden(True)
        home = QTreeWidgetItem(self.library_tree, ["Home"])
        browse = QTreeWidgetItem(self.library_tree, ["Browse"])
        radio = QTreeWidgetItem(self.library_tree, ["Radio"])
        playlists = QTreeWidgetItem(self.library_tree, ["Playlists"])
        self.library_tree.addTopLevelItems([home, browse, radio, playlists])
        left_sidebar.addWidget(self.library_tree)

        return left_sidebar

    def create_main_content(self) -> QVBoxLayout:
        main_content = QVBoxLayout()
        self.content_label = QLabel("Your Library")
        main_content.addWidget(self.content_label)

        self.playlist = QListWidget()
        main_content.addWidget(self.playlist)

        # Recommendations
        self.recommendations = QListWidget()
        main_content.addWidget(QLabel("Recommendations:"))
        main_content.addWidget(self.recommendations)

        return main_content

    def create_player_controls(self) -> QHBoxLayout:
        player_controls = QHBoxLayout()
        self.play_button = QPushButton(QIcon("assets/play_icon.png"), "")
        self.play_button.setIconSize(QSize(32, 32))
        self.next_button = QPushButton(QIcon("assets/next_icon.png"), "")
        self.next_button.setIconSize(QSize(32, 32))
        self.prev_button = QPushButton(QIcon("assets/prev_icon.png"), "")
        self.prev_button.setIconSize(QSize(32, 32))
        self.sleep_timer_button = QPushButton(QIcon("assets/sleep_icon.png"), "")
        self.sleep_timer_button.setIconSize(QSize(32, 32))
        self.offline_mode_button = QPushButton(QIcon("assets/offline_icon.png"), "")
        self.offline_mode_button.setIconSize(QSize(32, 32))

        player_controls.addWidget(self.prev_button)
        player_controls.addWidget(self.play_button)
        player_controls.addWidget(self.next_button)
        player_controls.addWidget(self.sleep_timer_button)
        player_controls.addWidget(self.offline_mode_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # Volume control
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)

        # Now playing
        self.now_playing = QLabel("Now Playing: ")

        return player_controls

    def setup_connections(self) -> None:
        self.search_bar.returnPressed.connect(self.search_music)
        self.library_tree.itemClicked.connect(self.handle_tree_item_click)
        self.playlist.itemDoubleClicked.connect(self.play_selected)
        self.recommendations.itemDoubleClicked.connect(self.play_recommended)
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.next_button.clicked.connect(self.music_player.next_track)
        self.prev_button.clicked.connect(self.music_player.previous_track)
        self.sleep_timer_button.clicked.connect(self.set_sleep_timer)
        self.offline_mode_button.clicked.connect(self.toggle_offline_mode)
        self.volume_slider.valueChanged.connect(self.music_player.set_volume)
        self.update_progress.connect(self.progress_bar.setValue)

    async def search_music(self) -> None:
        query = self.search_bar.text()
        try:
            results = await self.music_player.search(query)
            self.playlist.clear()
            for result in results:
                self.playlist.addItem(result['title'])
            await self.update_recommendations()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while searching: {str(e)}")

    async def play_selected(self, item) -> None:
        title = item.text()
        try:
            await self.music_player.play_title(title)
            self.now_playing.setText(f"Now Playing: {title}")
            await self.update_recommendations()
            self.play_button.setIcon(QIcon("assets/pause_icon.png"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while playing the selected track: {str(e)}")

    async def play_recommended(self, item) -> None:
        title = item.text()
        try:
            await self.music_player.play_title(title)
            self.now_playing.setText(f"Now Playing: {title}")
            self.play_button.setIcon(QIcon("assets/pause_icon.png"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while playing the recommended track: {str(e)}")

    def set_sleep_timer(self) -> None:
        minutes, ok = QInputDialog.getInt(self, "Set Sleep Timer", "Enter minutes:", 30, 1, 180)
        if ok:
            self.sleep_timer.start(minutes * 60 * 1000)  # Convert minutes to milliseconds
            QMessageBox.information(self, "Sleep Timer", f"Sleep timer set for {minutes} minutes.")

    async def toggle_offline_mode(self) -> None:
        await self.music_player.toggle_offline_mode()
        mode = "Offline" if self.music_player.offline_mode else "Online"
        self.offline_mode_button.setIcon(QIcon(f"assets/offline_{'on' if self.music_player.offline_mode else 'off'}_icon.png"))
        QMessageBox.information(self, "Mode Changed", f"Switched to {mode} mode.")

    async def update_recommendations(self) -> None:
        try:
            recommendations = await self.recommendation_engine.get_recommendations(self.music_player.get_play_history())
            self.recommendations.clear()
            for recommendation in recommendations:
                self.recommendations.addItem(recommendation['title'])
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not update recommendations: {str(e)}")

    async def toggle_play_pause(self) -> None:
        if await self.music_player.is_playing():
            await self.music_player.pause()
            self.play_button.setIcon(QIcon("assets/play_icon.png"))
        else:
            await self.music_player.play()
            self.play_button.setIcon(QIcon("assets/pause_icon.png"))

    async def update_progress_bar(self) -> None:
        if await self.music_player.is_playing():
            progress = int(await self.music_player.get_position() * 100)
            self.update_progress.emit(progress)

    async def handle_tree_item_click(self, item, column) -> None:
        self.content_label.setText(item.text(column))
        self.playlist.clear()
        if item.text(column) == "Home":
            tracks = await sample_api.get_top_tracks()
            for track in tracks:
                self.playlist.addItem(track['title'])
        elif item.text(column) == "Browse":
            genres = await sample_api.get_genres()
            for genre in genres:
                self.playlist.addItem(genre)
        elif item.text(column) == "Radio":
            stations = await sample_api.get_radio_stations()
            for station in stations:
                self.playlist.addItem(station['name'])
        elif item.text(column) == "Playlists":
            playlists = await sample_api.get_user_playlists()
            for playlist in playlists:
                self.playlist.addItem(playlist['name'])