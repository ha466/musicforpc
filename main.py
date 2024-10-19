import sys
import argparse
import logging
import asyncio
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer
from ui.main_window import MainWindow
from utils.config import Config
from qasync import QEventLoop, asyncSlot, asyncClose

def setup_logging(debug_mode: bool) -> None:
    level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='pymusicplayer.log',
        filemode='a'
    )
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def create_system_tray(app: QApplication, window: MainWindow) -> QSystemTrayIcon:
    tray_icon = QSystemTrayIcon(QIcon("assets/app_icon.png"), app)
    tray_menu = QMenu()
    
    show_action = tray_menu.addAction("Show")
    show_action.triggered.connect(window.show)
    
    hide_action = tray_menu.addAction("Hide")
    hide_action.triggered.connect(window.hide)
    
    quit_action = tray_menu.addAction("Quit")
    quit_action.triggered.connect(app.quit)
    
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()
    
    return tray_icon

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PyMusicPlayer - A Python-based music player")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--offline", action="store_true", help="Start in offline mode")
    return parser.parse_args()

@asyncClose
async def cleanup(window: MainWindow, config: Config) -> None:
    logging.info("Shutting down PyMusicPlayer...")
    await window.music_player.stop()
    await window.music_player.save_offline_cache()
    await config.save()

async def main() -> None:
    args = parse_arguments()
    
    setup_logging(args.debug)
    
    try:
        app = QApplication(sys.argv)
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)

        config = Config()
        await config.load()
        
        window = MainWindow(config)
        
        if args.offline:
            await window.toggle_offline_mode()
        
        window.show()
        
        tray_icon = create_system_tray(app, window)
        
        # Graceful shutdown
        app.aboutToQuit.connect(lambda: asyncio.create_task(cleanup(window, config)))
        
        with loop:
            loop.run_forever()
    
    except Exception as e:
        logging.error(f"An error occurred during startup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())