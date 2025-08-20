import sys
from pathlib import Path
from threading import Thread
import time
import json
import pyttsx3

from PySide6.QtCore import (Qt, QPoint, Signal, Slot, QObject, QPropertyAnimation,
                            QEasingCurve, QRect, QSize, Property, QUrl, QTimer)
from PySide6.QtGui import QColor, QFontMetrics
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                               QLabel, QFileDialog, QHBoxLayout, QApplication,
                               QSlider, QStyle, QComboBox, QFormLayout,
                               QProgressBar, QCheckBox, QScrollArea, QLayout,
                               QStackedWidget, QGraphicsOpacityEffect, QSizePolicy, QTextBrowser,
                               QMenu, QInputDialog, QListWidget, QListWidgetItem)

from Echoscribe.ui.style import MAIN_STYLE_SHEET
from Echoscribe.Core.transcriber import Transcriber
from Echoscribe.Core.dictionary import Dictionary


# Custom widgets: FlowLayout, ClickableWordLabel, HoverTabButton
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None: self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing);
        self._item_list = []

    def __del__(self):
        item = self.takeAt(0);

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list): return self._item_list[index]

    def takeAt(self, index):
        if 0 <= index < len(self._item_list): return self._item_list.pop(index)

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect); self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize();
        for item in self._item_list: size = size.expandedTo(item.minimumSize())
        margin, _, _, _ = self.getContentsMargins();
        size += QSize(2 * margin, 2 * margin);
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x();
        y = rect.y();
        line_height = 0
        for item in self._item_list:
            wid = item.widget();
            space_x = self.spacing();
            space_y = self.spacing()
            if wid.isVisible():
                # Force line break when encountering LineBreak placeholder widget
                if wid.objectName() == "LineBreak":
                    x = rect.x();
                    y = y + line_height + space_y;
                    line_height = 0
                    continue
                next_x = x + item.sizeHint().width() + space_x
                if next_x - space_x > rect.right() and line_height > 0:
                    x = rect.x();
                    y = y + line_height + space_y;
                    line_height = 0
                if not test_only: item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
                x = x + item.sizeHint().width() + space_x;
                line_height = max(line_height, item.sizeHint().height())
        return y + line_height - rect.y()


class ClickableWordLabel(QLabel):
    wordClicked = Signal(int)

    def __init__(self, text, start_time_ms, parent=None):
        super().__init__(text, parent)
        self.start_time_ms = start_time_ms;
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("background-color: transparent; padding: 2px 1px; border-radius: 4px;")
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self._color = QColor(0, 0, 0, 0);
        self.animation = QPropertyAnimation(self, b'backgroundColor')
        self.animation.setDuration(150);
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    def mouseReleaseEvent(self, event):
        self.wordClicked.emit(self.start_time_ms)
        super().mouseReleaseEvent(event)

    def enterEvent(self, event): self.animation.setEndValue(QColor(0, 120, 212, 50)); self.animation.start()

    def leaveEvent(self, event): self.animation.setEndValue(QColor(0, 0, 0, 0)); self.animation.start()

    @Property(QColor)
    def backgroundColor(self): return self._color

    @backgroundColor.setter
    def backgroundColor(self, color):
        self._color = color;
        self.setStyleSheet(f"background-color: {color.name(QColor.HexArgb)}; padding: 2px 1px; border-radius: 4px;")


class HoverTabButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.base_size = QSize(50, 40);
        self.hover_size = QSize(55, 45)
        self.setMinimumSize(self.base_size);
        self.setCheckable(True)
        self.animation = QPropertyAnimation(self, b"minimumSize")
        self.animation.setDuration(150);
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    def enterEvent(self, event): self.animation.setEndValue(
        self.hover_size); self.animation.start(); super().enterEvent(event)

    def leaveEvent(self, event): self.animation.setEndValue(self.base_size); self.animation.start(); super().leaveEvent(
        event)

    def mousePressEvent(self, event): self.animation.setEndValue(
        self.base_size); self.animation.start(); super().mousePressEvent(event)


# Favorites list item widget
class FavoriteItemWidget(QWidget):
    def __init__(self, word_text: str, brief: str = "", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        self.word_label = QLabel(word_text)
        self.word_label.setObjectName("FavoriteWord")
        self.brief_label = QLabel(brief)
        self.brief_label.setObjectName("FavoriteBrief")
        self.brief_label.setWordWrap(True)
        layout.addWidget(self.word_label, 0, Qt.AlignLeft)
        layout.addWidget(self.brief_label, 1)
        self.setObjectName("FavoriteItem")

        self.setStyleSheet(
            "#FavoriteItem { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; }"
            "#FavoriteWord { font-weight: 600; color: #333333; }"
            "#FavoriteBrief { color: #4B5563; }"
        )


# Custom tooltip window
class WordTooltip(QWidget):
    def __init__(self, parent=None, font_size=14, main_window=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(380, 220)
        self.font_size = font_size
        self.main_window = main_window
        self.current_word = ""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        

        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setAlignment(Qt.AlignTop)
        self.content_label.setOpenExternalLinks(False)
        self.content_label.linkActivated.connect(self._on_link_clicked)
        self.content_label.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 rgba(255, 255, 255, 0.98), 
                    stop:1 rgba(248, 250, 252, 0.98));
                border: 2px solid rgba(59, 130, 246, 0.3);
                border-radius: 12px;
                padding: 12px;
                font-size: {self.font_size}px;
                color: #1f2937;
                font-weight: 500;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            }}
        """)
        
        layout.addWidget(self.content_label)
    
    def _on_link_clicked(self, url):
        if (url == "speak_word" or url == "#speak_word") and self.main_window and self.current_word:
            self.main_window._speak_word(self.current_word)
    
    def setContent(self, word, entry):
        self.current_word = word
        
        if not entry:
            content = f"""
            <div style='text-align: center; margin: 10px 0;'>
                <span style='font-size: {self.font_size + 2}px; font-weight: 600; color: #1f2937;'>{word}</span><br/>
                <a href="#speak_word" style='color: #059669; text-decoration: none; cursor: pointer; font-size: {self.font_size}px;'>🔊 Click to play pronunciation</a><br/>
                <span style='color: #9ca3af; font-size: {self.font_size - 1}px; margin-top: 8px;'>📚 No dictionary record</span>
            </div>
            """
        else:
            def esc(t: str) -> str:
                return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            phonetic = entry.get('phonetic', '')
            pos = entry.get('pos', '')
            translation = entry.get('translation', '')
            definition = entry.get('definition', '')
            
            content = f"""
            <div style='margin-bottom: 8px;'>
                <span style='font-size: {self.font_size + 2}px; font-weight: 600; color: #1f2937;'>{esc(word)}</span>
            </div>
            """
            
            if phonetic:
                content += f"""
                <div style='margin-bottom: 6px;'>
                    <a href="#speak_word" style='color: #059669; text-decoration: none; cursor: pointer; font-size: {self.font_size}px; font-weight: 500;'>🔊 /{esc(phonetic)}/</a>
                </div>
                """
            else:
                content += f"""
                <div style='margin-bottom: 6px;'>
                    <a href="#speak_word" style='color: #059669; text-decoration: none; cursor: pointer; font-size: {self.font_size}px; font-weight: 500;'>🔊 Click to play pronunciation</a>
                </div>
                """
            
            if pos:
                content += f"""
                <div style='margin-bottom: 8px;'>
                    <span style='color: #4338ca; font-size: {self.font_size - 1}px; background: rgba(67, 56, 202, 0.1); padding: 2px 6px; border-radius: 4px;'>{esc(pos)}</span>
                </div>
                """
            
            if definition:
                if len(definition) > 100:
                    definition = definition[:100] + "..."
                content += f"""
                <div style='margin-top: 6px; margin-bottom: 6px; line-height: 1.3;'>
                    <div style='color: #dc2626; font-size: {self.font_size - 2}px; font-weight: 600; margin-bottom: 3px;'>🇺🇸 English</div>
                    <span style='color: #1f2937; font-size: {self.font_size - 1}px; font-style: italic;'>{esc(definition)}</span>
                </div>
                """
            
            if translation:
                if len(translation) > 100:
                    translation = translation[:100] + "..."
                content += f"""
                <div style='margin-top: 6px; line-height: 1.3;'>
                    <div style='color: #dc2626; font-size: {self.font_size - 2}px; font-weight: 600; margin-bottom: 3px;'>🇨🇳 Chinese</div>
                    <span style='color: #374151; font-size: {self.font_size - 1}px;'>{esc(translation)}</span>
                </div>
                """
        
        self.content_label.setText(content)

# Main window class
class TranscriptBrowser(QTextBrowser):
    wordEditRequested = Signal(int)
    wordToggleFavoriteRequested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._favorite_resolver = None
        self._hovered_anchor = None
        self._original_html = ""
        self._tooltip_timer = QTimer()
        self._tooltip_timer.setSingleShot(True)
        self._tooltip_timer.timeout.connect(self._show_word_tooltip)
        self._current_tooltip = None
        self._dictionary = None
        self._was_playing_before_tooltip = False
        self.setMouseTracking(True)

    def setFavoriteResolver(self, resolver_callable):
        self._favorite_resolver = resolver_callable
    
    def setDictionary(self, dictionary):
        self._dictionary = dictionary

    def _is_favorite(self, idx: int) -> bool:
        try:
            return bool(self._favorite_resolver(idx)) if callable(self._favorite_resolver) else False
        except Exception:
            return False

    def setHtml(self, html):
        # Save current scroll position before updating HTML
        scrollbar = self.verticalScrollBar()
        current_scroll_position = scrollbar.value()
        
        self._original_html = html
        super().setHtml(html)
        
        # Restore scroll position after HTML update (if not the initial load)
        if hasattr(self, '_has_content') and self._has_content:
            scrollbar.setValue(current_scroll_position)
        else:
            self._has_content = True

    def mouseMoveEvent(self, event):

        anchor = self.anchorAt(event.pos())
        
        if anchor and anchor.startswith('word:') and anchor != self._hovered_anchor:

            self._hovered_anchor = anchor
            self._current_mouse_pos = event.globalPos()
            self._apply_hover_effect(anchor)

            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'hover_delay_ms'):
                parent_window = parent_window.parent()
            
            delay = parent_window.hover_delay_ms if parent_window else 1000
            if delay > 0:
                self._tooltip_timer.start(delay)
        elif not anchor and self._hovered_anchor:

            self._hovered_anchor = None
            self._tooltip_timer.stop()
            self._hide_tooltip()
            self._remove_hover_effect()
        elif anchor == self._hovered_anchor:

            self._current_mouse_pos = event.globalPos()
        
        super().mouseMoveEvent(event)

    def _apply_hover_effect(self, anchor):

        is_fav = 'class="fav"' in self._original_html and f'<a href="{anchor}" class="fav"' in self._original_html
        

        hover_style = "background: #87ceeb !important; color: #1f2937 !important;"
        

        # Save current scroll position before modifying HTML
        scrollbar = self.verticalScrollBar()
        current_scroll_position = scrollbar.value()
        
        if is_fav:
            modified_html = self._original_html.replace(
                f'<a href="{anchor}" class="fav"',
                f'<a href="{anchor}" style="{hover_style}"'
            )
        else:
            modified_html = self._original_html.replace(
                f'<a href="{anchor}"',
                f'<a href="{anchor}" style="{hover_style}"'
            )
        super().setHtml(modified_html)
        
        # Restore scroll position after HTML update
        scrollbar.setValue(current_scroll_position)

    def _remove_hover_effect(self):

        # Save current scroll position before modifying HTML
        scrollbar = self.verticalScrollBar()
        current_scroll_position = scrollbar.value()
        
        super().setHtml(self._original_html)
        
        # Restore scroll position after HTML update
        scrollbar.setValue(current_scroll_position)
    
    def _show_word_tooltip(self):
        if not self._hovered_anchor or not self._dictionary:
            return
        
        try:

            parts = self._hovered_anchor.split(':', 2)
            idx = int(parts[1])
            

            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'words_data'):
                parent_window = parent_window.parent()
            
            if not parent_window or not hasattr(parent_window, 'words_data'):
                return
                
            if idx >= len(parent_window.words_data):
                return
                
            word = parent_window.words_data[idx].get('word', '').strip()

            clean_word = word.strip('.,!?;:，。！？；：').lower()
            

            entry = self._dictionary.lookup(clean_word)
            

            if hasattr(parent_window, 'pause_on_tooltip') and parent_window.pause_on_tooltip:
                if hasattr(parent_window, 'player') and parent_window.player.playbackState() == QMediaPlayer.PlayingState:
                    self._was_playing_before_tooltip = True
                    parent_window.player.pause()
                else:
                    self._was_playing_before_tooltip = False
            

            if self._current_tooltip:
                self._current_tooltip.hide()
                self._current_tooltip.deleteLater()
            

            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'tooltip_font_size'):
                parent_window = parent_window.parent()
            
            font_size = parent_window.tooltip_font_size if parent_window else 14
            self._current_tooltip = WordTooltip(font_size=font_size, main_window=parent_window)
            self._current_tooltip.setContent(clean_word, entry)
            
            pos = self._current_mouse_pos
            tooltip_pos = QPoint(pos.x() - 190, pos.y() - 180)
            
            self._current_tooltip.move(tooltip_pos)
            self._current_tooltip.show()
            
        except Exception as e:
            print(f"Tooltip display error: {e}")
    
    def _hide_tooltip(self):
        if self._current_tooltip:
            self._current_tooltip.hide()
            self._current_tooltip.deleteLater()
            self._current_tooltip = None
        

        if self._was_playing_before_tooltip:
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'player'):
                parent_window = parent_window.parent()
            
            if parent_window and hasattr(parent_window, 'player'):
                if parent_window.player.playbackState() == QMediaPlayer.PausedState:
                    parent_window.player.play()
            
            self._was_playing_before_tooltip = False

    def contextMenuEvent(self, event):
        href = self.anchorAt(event.pos())
        if href and href.startswith('word:'):
            try:
                parts = href.split(':', 2)
                idx = int(parts[1])
            except Exception:
                idx = None
            menu = QMenu(self)
            

            
            action_edit = menu.addAction("Edit")
            label_fav = "Unfavorite" if (idx is not None and self._is_favorite(idx)) else "Favorite"
            action_fav = menu.addAction(label_fav)
            
            if label_fav == "Unfavorite":
                action_fav.setProperty("action_type", "unfavorite")
            else:
                action_fav.setProperty("action_type", "favorite")
            
            action_edit.setProperty("action_type", "edit")
            

            menu.setStyleSheet("""
                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 8px 16px;
                    border-radius: 4px;
                    margin: 2px;
                    color: #333333;
                }
                QMenu::item[action_type="edit"]:selected {
                    color: #3b82f6;
                    background-color: #f0f9ff;
                }
                QMenu::item[action_type="favorite"]:selected {
                    color: #f59e0b;
                    background-color: #fffbeb;
                }
                QMenu::item[action_type="unfavorite"]:selected {
                    color: #ef4444;
                    background-color: #fef2f2;
                }
            """)
            chosen = menu.exec(event.globalPos())
            if idx is not None:
                if chosen == action_edit:
                    self.wordEditRequested.emit(idx)
                elif chosen == action_fav:
                    self.wordToggleFavoriteRequested.emit(idx)
        else:
            super().contextMenuEvent(event)

class MainWindow(QMainWindow):
    class WorkerSignals(QObject):
        finished = Signal(list);
        error = Signal(str);
        progress = Signal(int)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint);
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("MainWindow");
        self.setWindowTitle("EchoScribe");
        self.resize(850, 600)
        self.setAcceptDrops(True);
        self.transcriber = Transcriber();
        self.dictionary = Dictionary()
        self._drag_pos = QPoint();
        self.duration = 0
        self.player = QMediaPlayer();
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self._pending_seek_ms = None
        self.favorites = set()
        self.text_font_size_px = 18
        self.text_line_height = 2.0
        
        self.auto_play_after_transcription = True
        self.hover_delay_ms = 1000
        self.tooltip_font_size = 14
        self.speech_rate = 200
        self.pause_on_tooltip = False
        
        self.tts_engine = None


        self._load_settings()
        self._load_favorites()

        self._setup_ui()
        self._connect_signals()
        

        self._refresh_favorites_page()
        
        self._switch_tab(0, initial=True)

    def _get_application_path(self) -> Path:
        """Get application root directory path for reading resource files."""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        return Path(__file__).resolve().parent.parent.parent
    
    def _get_user_data_path(self) -> Path:
        """Get user data directory path for saving configurations and favorites."""
        import os
        if os.name == 'nt':  # Windows
            user_data_dir = Path(os.environ.get('APPDATA', '')) / 'EchoScribe'
        else:  # Linux/Mac
            user_data_dir = Path.home() / '.echoscribe'
        
        user_data_dir.mkdir(parents=True, exist_ok=True)
        return user_data_dir

    def _load_settings(self):
        user_settings_path = self._get_user_data_path() / "settings.json"
        default_settings_path = self._get_application_path() / "Assets" / "config" / "settings.json"
        
        try:
            if user_settings_path.exists():
                with user_settings_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            elif default_settings_path.exists():
                with default_settings_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                self._save_settings_data(data)
            else:
                data = {}
            
            self.text_font_size_px = data.get("font_size_px", 18)
            self.text_line_height = data.get("line_height", 2.0)
            self.auto_play_after_transcription = data.get("auto_play_after_transcription", True)
            self.hover_delay_ms = data.get("hover_delay_ms", 1000)
            self.tooltip_font_size = data.get("tooltip_font_size", 14)
            self.speech_rate = data.get("speech_rate", 200)
            self.pause_on_tooltip = data.get("pause_on_tooltip", False)
        except Exception as e:
            print(f"[DEBUG] Failed to load settings: {e}")
            pass

    def _save_settings(self):
        data = {
            "font_size_px": self.text_font_size_px,
            "line_height": self.text_line_height,
            "volume": self.volume_slider.value(),
            "playback_rate": self.rate_combo.currentText(),
            "show_progress": self.show_progress_checkbox.isChecked(),
            "auto_play_after_transcription": self.auto_play_after_transcription,
            "hover_delay_ms": self.hover_delay_ms,
            "tooltip_font_size": self.tooltip_font_size,
            "speech_rate": self.speech_rate,
            "pause_on_tooltip": self.pause_on_tooltip
        }
        self._save_settings_data(data)
    
    def _save_settings_data(self, data):
        """Save settings data to user directory."""
        settings_path = self._get_user_data_path() / "settings.json"
        try:
            with settings_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[DEBUG] Settings saved to: {settings_path}")
        except Exception as e:
            print(f"[DEBUG] Failed to save settings: {e}")
            pass

    def _load_favorites(self):

        user_favorites_path = self._get_user_data_path() / "favorites.json"
        default_favorites_path = self._get_application_path() / "Assets" / "config" / "favorites.json"
        
        try:
            if user_favorites_path.exists():

                with user_favorites_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            elif default_favorites_path.exists():

                with default_favorites_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)

                self._save_favorites()
            else:

                data = []
            
            self.favorites = set(data) if isinstance(data, list) else set()
            print(f"[DEBUG] Favorites loaded: {len(self.favorites)} words")
        except Exception as e:
            print(f"[DEBUG] Failed to load favorites: {e}")
            self.favorites = set()

    def _save_favorites(self):
        favorites_path = self._get_user_data_path() / "favorites.json"
        try:
            with favorites_path.open("w", encoding="utf-8") as f:
                json.dump(sorted(list(self.favorites)), f, indent=2, ensure_ascii=False)
            print(f"[DEBUG] Favorites saved to: {favorites_path}")
        except Exception as e:
            print(f"[DEBUG] Failed to save favorites: {e}")
            pass

    def _setup_ui(self):
        root_widget = QWidget();
        root_widget.setObjectName("RootWidget")
        root_layout = QVBoxLayout(root_widget);
        root_layout.setContentsMargins(0, 0, 0, 0);
        root_layout.setSpacing(0)
        self.setCentralWidget(root_widget)

        title_bar = QWidget();
        title_bar.setObjectName("TitleBar")
        title_bar_layout = QHBoxLayout(title_bar);
        title_bar_layout.setContentsMargins(10, 0, 0, 0)
        self.title_label = QLabel("EchoScribe");
        self.title_label.setObjectName("TitleLabel")
        self.close_button = QPushButton("✕");
        self.close_button.setObjectName("CloseButton");
        self.close_button.setFixedSize(30, 30)
        title_bar_layout.addWidget(self.title_label);
        title_bar_layout.addStretch();
        title_bar_layout.addWidget(self.close_button)

        main_content_layout = QHBoxLayout();
        main_content_layout.setSpacing(0);
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        tab_bar = QWidget();
        tab_bar.setObjectName("TabBar");
        tab_bar_layout = QVBoxLayout(tab_bar)
        tab_bar.setFixedWidth(120)
        self.main_tab_button = HoverTabButton("Home");
        self.settings_tab_button = HoverTabButton("Settings")
        self.favorites_tab_button = HoverTabButton("Favorites")
        self.search_tab_button = HoverTabButton("Search")
        tab_bar_layout.addWidget(self.main_tab_button, alignment=Qt.AlignTop)
        tab_bar_layout.addWidget(self.settings_tab_button, alignment=Qt.AlignTop);
        tab_bar_layout.addWidget(self.favorites_tab_button, alignment=Qt.AlignTop);
        tab_bar_layout.addWidget(self.search_tab_button, alignment=Qt.AlignTop);
        tab_bar_layout.addStretch()

        self.pages_stack = QStackedWidget()
        self.main_page = self._create_main_page();
        self.settings_page = self._create_settings_page()
        self.favorites_page = self._create_favorites_page()
        self.search_page = self._create_search_page()
        self.pages_stack.addWidget(self.main_page);
        self.pages_stack.addWidget(self.settings_page)
        self.pages_stack.addWidget(self.favorites_page)
        self.pages_stack.addWidget(self.search_page)
        main_content_layout.addWidget(tab_bar);
        main_content_layout.addWidget(self.pages_stack, 1)

        root_layout.addWidget(title_bar);
        root_layout.addLayout(main_content_layout)
        self.setStyleSheet(MAIN_STYLE_SHEET)

    def _create_main_page(self):
        page = QWidget();
        layout = QVBoxLayout(page);
        layout.setContentsMargins(20, 20, 20, 20)
        self.load_button = QPushButton("Import audio file or drag and drop here");
        self.status_label = QLabel("Welcome to EchoScribe")

        self.transcription_progress = QProgressBar()
        self.transcription_progress.setRange(0, 100)
        self.transcription_progress.setTextVisible(True)

        self.transcription_progress.setVisible(False)
        self.transcription_progress.setFixedHeight(16)
        self.transcription_progress.setMinimumWidth(0)
        self.transcription_progress.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)


        self.transcript_browser = TranscriptBrowser()
        self.transcript_browser.setObjectName("TranscriptArea")
        self.transcript_browser.setOpenExternalLinks(False)
        self.transcript_browser.setOpenLinks(False)
        self.transcript_browser.setReadOnly(True)

        self.transcript_browser.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.transcript_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.transcript_browser.setLineWrapMode(QTextBrowser.WidgetWidth)

        self.transcript_browser.setStyleSheet("QTextBrowser#TranscriptArea { padding: 8px; }")
        self.playback_controls = self._create_playback_controls()
        layout.addWidget(self.load_button);
        layout.addWidget(self.status_label);
        layout.addWidget(self.transcription_progress)
        layout.addWidget(self.transcript_browser, 1);
        layout.addWidget(self.playback_controls)
        return page

    def _create_settings_page(self):
        page = QWidget();
        layout = QFormLayout(page);
        layout.setContentsMargins(20, 20, 20, 20);
        layout.setSpacing(10)
        self.volume_slider = QSlider(Qt.Horizontal);
        self.volume_slider.setRange(0, 100);
        self.volume_slider.setValue(100)
        self.rate_combo = QComboBox();
        self.rate_combo.addItems(["0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x", "2.5x", "3.0x"])
        self.rate_combo.setCurrentText("1.0x");
        self.show_progress_checkbox = QCheckBox("Show transcription progress")

        self.font_size_combo = QComboBox(); self.font_size_combo.addItems(["14", "16", "18 (default)", "20", "22"]); self.font_size_combo.setCurrentText(str(self.text_font_size_px) + (" (default)" if self.text_font_size_px == 18 else ""))
        self.line_height_combo = QComboBox(); self.line_height_combo.addItems(["Compact (1.6)", "Standard (2.0) (default)", "Loose (2.4)"])

        if self.text_line_height <= 1.6:
            self.line_height_combo.setCurrentText("Compact (1.6)")
        elif self.text_line_height >= 2.4:
            self.line_height_combo.setCurrentText("Loose (2.4)")
        else:
            self.line_height_combo.setCurrentText("Standard (2.0) (default)")
        
        self.auto_play_checkbox = QCheckBox("Play immediately after transcription (default)")
        self.auto_play_checkbox.setChecked(self.auto_play_after_transcription)
        
        self.pause_on_tooltip_checkbox = QCheckBox("Pause when tooltip appears")
        self.pause_on_tooltip_checkbox.setChecked(self.pause_on_tooltip)
        
        self.hover_delay_combo = QComboBox()
        self.hover_delay_combo.addItems(["Off", "0s", "0.5s", "1s (default)", "2s", "3s"])
        delay_map = {-1: "Off", 0: "0s", 500: "0.5s", 1000: "1s (default)", 2000: "2s", 3000: "3s"}
        if self.hover_delay_ms == -1:
            self.hover_delay_combo.setCurrentText("Off")
        else:
            self.hover_delay_combo.setCurrentText(delay_map.get(self.hover_delay_ms, "1s (default)"))
        
        self.tooltip_font_combo = QComboBox()
        self.tooltip_font_combo.addItems(["12", "14 (default)", "16", "18", "20"])
        self.tooltip_font_combo.setCurrentText(str(self.tooltip_font_size) + (" (default)" if self.tooltip_font_size == 14 else ""))
        
        self.speech_rate_combo = QComboBox()
        self.speech_rate_combo.addItems(["Slow (150)", "Normal (200) (default)", "Fast (250)", "Very Fast (300)"])
        rate_map = {150: "Slow (150)", 200: "Normal (200) (default)", 250: "Fast (250)", 300: "Very Fast (300)"}
        self.speech_rate_combo.setCurrentText(rate_map.get(self.speech_rate, "Normal (200) (default)"))
        
        self.show_progress_checkbox.setChecked(True)
        self.btn_reset_settings = QPushButton("Reset to defaults")
        self.btn_reset_settings.clicked.connect(self._reset_settings)
        layout.addRow("Volume", self.volume_slider);
        layout.addRow("Speed", self.rate_combo);
        layout.addRow("", self.show_progress_checkbox)
        layout.addRow("", self.auto_play_checkbox)
        layout.addRow("", self.pause_on_tooltip_checkbox)
        layout.addRow("Font Size(px)", self.font_size_combo)
        layout.addRow("Line Height", self.line_height_combo)
        layout.addRow("Hover Delay", self.hover_delay_combo)
        layout.addRow("Tooltip Font", self.tooltip_font_combo)
        layout.addRow("Speech Rate", self.speech_rate_combo)
        layout.addRow("", self.btn_reset_settings)
        return page

    def _create_favorites_page(self):
        page = QWidget();
        layout = QVBoxLayout(page);
        layout.setContentsMargins(20, 20, 20, 20)
        self.favorites_list = QListWidget()
        self.favorites_list.setSpacing(8)
        self.favorites_list.setAlternatingRowColors(False)
        self.favorites_list.setStyleSheet("QListWidget { background: transparent; border: none; }")
        self.favorites_list.itemClicked.connect(self._open_favorite_detail)
        btns = QHBoxLayout()
        self.btn_remove_favorite = QPushButton("Remove Selected")
        self.btn_remove_favorite.clicked.connect(self._remove_selected_favorite)
        btns.addStretch(); btns.addWidget(self.btn_remove_favorite)
        layout.addWidget(self.favorites_list, 1)
        layout.addLayout(btns)
        return page

    def _create_search_page(self):
        page = QWidget();
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        from PySide6.QtWidgets import QLineEdit
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter English word to search dictionary...")
        self.search_result = QTextBrowser()
        self.search_result.setReadOnly(True)
        self.search_result.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.search_result.setOpenExternalLinks(False)
        self.search_result.setOpenLinks(False)
        self.search_result.anchorClicked.connect(self._on_search_anchor_clicked)
        self.btn_add_to_fav = QPushButton("Add to Favorites")
        self.btn_add_to_fav.clicked.connect(self._add_search_to_favorites)
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_result, 1)
        layout.addWidget(self.btn_add_to_fav)
        self.search_input.returnPressed.connect(self._perform_search)
        return page

    def _create_playback_controls(self):
        self.play_pause_button = QPushButton();
        self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay));
        self.play_pause_button.setObjectName("PlayPauseButton")
        self.progress_slider = QSlider(Qt.Horizontal);
        self.time_label = QLabel("00:00 / 00:00");
        layout = QHBoxLayout();
        layout.addWidget(self.play_pause_button);
        layout.addWidget(self.progress_slider);
        layout.addWidget(self.time_label)
        widget = QWidget();
        widget.setLayout(layout);
        return widget

    def _connect_signals(self):
        self.close_button.clicked.connect(self.close)
        self.main_tab_button.clicked.connect(lambda: self._switch_tab(0));
        self.settings_tab_button.clicked.connect(lambda: self._switch_tab(1))
        self.favorites_tab_button.clicked.connect(lambda: self._switch_tab(2))
        self.search_tab_button.clicked.connect(lambda: self._switch_tab(3))
        self.load_button.clicked.connect(self._handle_load_file_dialog)
        self.play_pause_button.clicked.connect(self._toggle_playback)
        self.player.playbackStateChanged.connect(self._update_play_pause_button_icon)
        self.volume_slider.valueChanged.connect(self._set_volume);
        self.rate_combo.currentTextChanged.connect(self._on_rate_changed)
        self.font_size_combo.currentTextChanged.connect(self._on_font_size_changed)
        self.line_height_combo.currentTextChanged.connect(self._on_line_height_changed)
        self.auto_play_checkbox.stateChanged.connect(self._on_auto_play_changed)
        self.pause_on_tooltip_checkbox.stateChanged.connect(self._on_pause_on_tooltip_changed)
        self.hover_delay_combo.currentTextChanged.connect(self._on_hover_delay_changed)
        self.tooltip_font_combo.currentTextChanged.connect(self._on_tooltip_font_changed)
        self.speech_rate_combo.currentTextChanged.connect(self._on_speech_rate_changed)
        self.progress_slider.sliderReleased.connect(lambda: self.player.setPosition(self.progress_slider.value()))
        self.player.positionChanged.connect(self._update_progress);
        self.player.durationChanged.connect(self._set_progress_range)
        self.transcript_browser.anchorClicked.connect(self._on_anchor_clicked)
        self.transcript_browser.wordEditRequested.connect(self._on_word_edit_requested)
        self.transcript_browser.wordToggleFavoriteRequested.connect(self._on_word_toggle_favorite_requested)
        self.favorites_tab_button.clicked.connect(lambda: self._switch_tab(2))

    def _switch_tab(self, index, initial=False):
        if self.pages_stack.currentIndex() == index and not initial: return

        if not initial and index != 3:
            self._showing_detail = False
        self.main_tab_button.setChecked(index == 0);
        self.settings_tab_button.setChecked(index == 1)
        if hasattr(self, 'favorites_tab_button'):
            self.favorites_tab_button.setChecked(index == 2)
        if hasattr(self, 'search_tab_button'):
            self.search_tab_button.setChecked(index == 3)
        if initial: self.pages_stack.setCurrentIndex(index); return
        current_widget = self.pages_stack.currentWidget();
        effect = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(effect);
        self.anim_fade_out = QPropertyAnimation(effect, b"opacity")
        self.anim_fade_out.setDuration(280);
        self.anim_fade_out.setEasingCurve(QEasingCurve.InOutCubic)
        self.anim_fade_out.setStartValue(1.0);
        self.anim_fade_out.setEndValue(0.0)
        self.anim_fade_out.finished.connect(lambda: self._fade_in_new_page(index));
        self.anim_fade_out.start()

    def _fade_in_new_page(self, index):
        self.pages_stack.setCurrentIndex(index);
        new_widget = self.pages_stack.currentWidget()
        effect = QGraphicsOpacityEffect(new_widget);
        new_widget.setGraphicsEffect(effect)
        self.anim_fade_in = QPropertyAnimation(effect, b"opacity");
        self.anim_fade_in.setDuration(280)
        self.anim_fade_in.setEasingCurve(QEasingCurve.InOutCubic)
        self.anim_fade_in.setStartValue(0.0);
        self.anim_fade_in.setEndValue(1.0);
        self.anim_fade_in.start()

    def _process_file(self, file_path_str):
        self.player.stop();
        self.progress_slider.setValue(0);
        self.time_label.setText("00:00 / 00:00")
        self._pending_seek_ms = None


        self.transcription_progress.setVisible(self.show_progress_checkbox.isChecked())
        self.transcription_progress.setValue(0)

        self.transcript_browser.clear()
        self.status_label.setText(f"Processing audio: {Path(file_path_str).name} ...")
        self.player.setSource(QUrl.fromLocalFile(file_path_str));
        self.load_button.setEnabled(False)
        self.signals = self.WorkerSignals();
        self.signals.finished.connect(self._on_transcription_finished)
        self.signals.error.connect(self._on_transcription_error);
        self.signals.progress.connect(self.transcription_progress.setValue)
        thread = Thread(target=self._run_transcription_in_worker, args=(file_path_str,));
        thread.daemon = True;
        thread.start()

    @Slot(list)
    def _on_transcription_finished(self, words_data):
        self.status_label.setText("Processing completed!");
        self.load_button.setEnabled(True)
        self.transcription_progress.setVisible(False)
        self.words_data = words_data
        self.transcript_browser.setFavoriteResolver(self._is_word_index_favorite)
        self.transcript_browser.setDictionary(self.dictionary)
        self._render_transcript()
        if self.auto_play_after_transcription and self.player.source().isValid(): 
            self.player.play()
        self._refresh_favorites_page()

    def _run_transcription_in_worker(self, file_path):
        try:
            segments, info = self.transcriber.model.transcribe(file_path, beam_size=5, word_timestamps=True)
            total_duration = getattr(info, 'duration', None)
            all_words = []
            last_progress = -1

            # Accumulate words and update progress based on processed duration
            for segment in segments:
                for word in segment.words:
                    start_sec = getattr(word, 'start', None)
                    if start_sec is None:
                        start_sec = getattr(segment, 'start', 0.0)
                    try:
                        start_ms = int(max(0.0, float(start_sec)) * 1000)
                    except Exception:
                        start_ms = 0
                    all_words.append({'word': word.word, 'start_ms': start_ms})

                if total_duration and getattr(segment, 'end', None) is not None:
                    ratio = min(max(segment.end / total_duration, 0.0), 0.999)
                    pct = int(ratio * 100)
                    if pct > last_progress:
                        last_progress = pct
                        self.signals.progress.emit(pct)

            self.signals.progress.emit(100);
            self.signals.finished.emit(all_words)
        except Exception as e:
            self.signals.error.emit(str(e))

    @Slot(int)
    def _on_word_clicked(self, position_ms):
        try:
            target = int(max(0, position_ms))
        except Exception:
            target = 0
        # Simple reliable version: pause → seek → play
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        self.player.setPosition(target)
        self.player.play()

    @Slot(QUrl)
    def _on_anchor_clicked(self, url):
        s = url.toString()
        if s.startswith('word:'):
            try:
                _, idx_str, ms_str = s.split(':', 2)
                ms = int(ms_str)
            except Exception:
                ms = 0
            self._on_word_clicked(ms)

    def _render_transcript(self):
        # Check if transcription data exists, skip rendering if none
        if not hasattr(self, 'words_data') or not self.words_data:
            return
        
        sentence_break_punctuations = set(['。', '.', '！', '!', '？', '?'])
        def esc(t: str) -> str:
            return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        def normalize_for_key(t: str) -> str:
            return t.strip().strip('.,!?;:，。！？；：').lower()
        html_words = []
        for i, w in enumerate(self.words_data):
            word_text = esc(w['word'])
            start_ms = int(max(0, w['start_ms']))
            cls = ' class="fav"' if normalize_for_key(w['word']) in self.favorites else ''
            html_words.append(f'<a href="word:{i}:{start_ms}"{cls}>{word_text}</a>')
            if any(p in w['word'] for p in sentence_break_punctuations):
                html_words.append('<br/>')
            else:
                html_words.append('&nbsp;')
        styled_html = (
            "<html><head><style>"
            f"body {{ background: transparent; color: #333333; font-size: {self.text_font_size_px}px; line-height: {self.text_line_height}; }}"
            "a { "
            "text-decoration: none; color: #333333; padding: 3px 6px; border-radius: 8px; background: transparent; "
            "transition: all 0.2s ease-out; "
            "display: inline-block; "
            "}"
            "a.fav { background: rgba(255,193,7,0.35); border-radius: 8px; }"
            "</style></head><body>" + ''.join(html_words) + "</body></html>"
        )
        self.transcript_browser.setHtml(styled_html)

    @Slot(int)
    def _on_word_edit_requested(self, idx):
        if not (0 <= idx < len(self.words_data)):
            return
        current_text = self.words_data[idx].get('word', '')
        new_text, ok = QInputDialog.getText(self, "Edit Word", "Enter new text:", text=current_text)
        if ok:
            self.words_data[idx]['word'] = new_text
            self._render_transcript()
            self._refresh_favorites_page()

    def _is_word_index_favorite(self, idx: int) -> bool:
        if not (0 <= idx < len(self.words_data)):
            return False
        key = self.words_data[idx].get('word', '')
        key = key.strip().strip('.,!?;:，。！？；：').lower()
        return key in self.favorites

    @Slot(int)
    def _on_toggle_favorite_idx(self, idx: int):
        if not (0 <= idx < len(self.words_data)):
            return
        raw = self.words_data[idx].get('word', '')
        word = raw.strip().strip('.,!?;:，。！？；：').lower()
        if not word:
            return
        if word in self.favorites:
            self.favorites.remove(word)
        else:
            self.favorites.add(word)
        self._render_transcript()
        self._refresh_favorites_page()

    # Compatible with old connection name
    @Slot(int)
    def _on_word_toggle_favorite_requested(self, idx: int):
        self._on_toggle_favorite_idx(idx)

    def _refresh_favorites_page(self):
        self.favorites_list.clear()
        for w in sorted(self.favorites):
            brief = self._format_brief_for_word(w)
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 48))
            item.setData(Qt.UserRole, w)
            self.favorites_list.addItem(item)
            widget = FavoriteItemWidget(w, brief)
            self.favorites_list.setItemWidget(item, widget)

    def _remove_selected_favorite(self):
        items = self.favorites_list.selectedItems()
        if not items:
            return
        for it in items:
            text = it.data(Qt.UserRole)
            if text and text in self.favorites:
                self.favorites.remove(text)
        self._refresh_favorites_page()
        self._render_transcript()

    def _format_brief_for_word(self, w: str) -> str:
        entry = self.dictionary.lookup(w.strip().strip('.,!?;:，。！？；：'))
        if not entry:
            return ""
        phon = entry.get('phonetic') or ""
        pos = entry.get('pos') or ""
        trans = entry.get('translation') or ""
        if len(trans) > 80:
            trans = trans[:80] + "…"
        parts = []
        if phon:
            parts.append(f"/{phon}/")
        if pos:
            parts.append(pos)
        if trans:
            parts.append(trans)
        return "  |  ".join(parts)





    def _add_search_to_favorites(self):
        q = self.search_input.text().strip().strip('.,!?;:，。！？；：').lower()
        if not q:
            return
        self.favorites.add(q)
        self._refresh_favorites_page()
        self._render_transcript()

    def _update_progress(self, position):
        if not self.progress_slider.isSliderDown(): self.progress_slider.setValue(position)
        self._update_time_label(position)

    def _set_progress_range(self, duration):
        self.progress_slider.setRange(0, duration);
        self.duration = duration;
        self._update_time_label(0)

    def _toggle_playback(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _set_volume(self, value):
        self.audio_output.setVolume(float(value) / 100.0)

    def _update_play_pause_button_icon(self, state):
        icon = QStyle.SP_MediaPause if state == QMediaPlayer.PlayingState else QStyle.SP_MediaPlay
        self.play_pause_button.setIcon(self.style().standardIcon(icon))

    @Slot(str)
    def _on_transcription_error(self, error_message):
        self.transcript_browser.setPlainText(f"Error occurred:\n{error_message}")
        self.status_label.setText("Processing failed!");
        self.load_button.setEnabled(True)
        self.transcription_progress.setVisible(False)

    def _update_time_label(self, position):
        self.time_label.setText(f"{self._format_time(position)} / {self._format_time(self.duration)}")

    def _format_time(self, ms):
        if not isinstance(ms, (int, float)) or ms < 0: return "00:00"
        s = round(ms / 1000);
        m, s = divmod(s, 60);
        h, m = divmod(m, 60)
        return f"{h:d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls(): self._process_file(event.mimeData().urls()[0].toLocalFile())

    def _handle_load_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "",
                                                   "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a)");
        if file_path: self._process_file(file_path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            try:
                pos_in_central = self.centralWidget().mapFrom(self, event.position().toPoint())
            except AttributeError:
                # Fallback for compatibility if position() not available
                pos_in_central = self.centralWidget().mapFrom(self, event.pos())
            target = self.centralWidget().childAt(pos_in_central)
            if target and target.objectName() == "TitleBar":
                self._drag_pos = event.globalPosition().toPoint() - self.pos()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos);
            event.accept();
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = QPoint();
        super().mouseReleaseEvent(event)

    def _reset_settings(self):
        # Reset to default values
        self.text_font_size_px = 18
        self.text_line_height = 2.0
        self.auto_play_after_transcription = True
        self.hover_delay_ms = 1000
        self.tooltip_font_size = 14
        self.speech_rate = 200
        self.pause_on_tooltip = False
        self.volume_slider.setValue(100)
        self.rate_combo.setCurrentText("1.0x")
        self.show_progress_checkbox.setChecked(True)
        self.auto_play_checkbox.setChecked(True)
        self.pause_on_tooltip_checkbox.setChecked(False)
        self.font_size_combo.setCurrentText("18 (默认)")
        self.line_height_combo.setCurrentText("标准 (2.0) (默认)")
        self.hover_delay_combo.setCurrentText("1s (default)")
        self.tooltip_font_combo.setCurrentText("14 (默认)")
        self.speech_rate_combo.setCurrentText("标准 (200) (默认)")
        # 立即保存并应用
        self._save_settings()
        self._render_transcript()
        self._set_volume(100)
        self.player.setPlaybackRate(1.0)

    @Slot(str)
    def _on_rate_changed(self, text):
        try:
            value = float(text.replace('x', '').strip())
        except Exception:
            value = 1.0
        self.player.setPlaybackRate(value)
        self._save_settings()

    @Slot(str)
    def _on_font_size_changed(self, text):
        try:
            self.text_font_size_px = int(text)
        except Exception:
            self.text_font_size_px = 18
        self._render_transcript()
        self._save_settings()

    @Slot(str)
    def _on_line_height_changed(self, text):
        if "1.6" in text:
            self.text_line_height = 1.6
        elif "2.4" in text:
            self.text_line_height = 2.4
        else:
            self.text_line_height = 2.0
        self._render_transcript()
        self._save_settings()

    def _speak_word(self, word):
        """使用TTS引擎播放单词发音"""
        if not word:
            return
        
        try:
            # 在新线程中播放，避免阻塞UI
            def speak_in_thread():
                try:
                    # 每次都重新初始化TTS引擎，避免状态冲突
                    tts = pyttsx3.init()
                    tts.setProperty('rate', self.speech_rate)
                    
                    # 设置为英语语音
                    voices = tts.getProperty('voices')
                    for voice in voices:
                        if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                            tts.setProperty('voice', voice.id)
                            break
                    
                    tts.say(word)
                    tts.runAndWait()
                    
                    # 播放完成后停止引擎
                    tts.stop()
                    del tts
                except Exception as e:
                    print(f"TTS线程播放失败: {e}")
            
            thread = Thread(target=speak_in_thread, daemon=True)
            thread.start()
        except Exception as e:
            print(f"语音播放失败: {e}")

    @Slot(int)
    def _on_auto_play_changed(self, state):
        self.auto_play_after_transcription = state == 2  # Qt.Checked
        self._save_settings()

    @Slot(int)
    def _on_pause_on_tooltip_changed(self, state):
        self.pause_on_tooltip = state == 2  # Qt.Checked
        self._save_settings()

    @Slot(str)
    def _on_hover_delay_changed(self, text):
        delay_map = {"Off": -1, "0s": 0, "0.5s": 500, "1s (default)": 1000, "2s": 2000, "3s": 3000}
        self.hover_delay_ms = delay_map.get(text, 1000)
        self._save_settings()

    @Slot(str)
    def _on_tooltip_font_changed(self, text):
        try:
            # 提取数字部分
            font_size = int(text.split()[0])
            self.tooltip_font_size = font_size
        except Exception:
            self.tooltip_font_size = 14
        self._save_settings()

    @Slot(str)
    def _on_speech_rate_changed(self, text):
        rate_map = {"慢速 (150)": 150, "标准 (200) (默认)": 200, "快速 (250)": 250, "极快 (300)": 300}
        self.speech_rate = rate_map.get(text, 200)
        # 语速设置会在下次播放时生效
        self._save_settings()

    def _is_word_index_favorite(self, idx: int) -> bool:
        if not hasattr(self, 'words_data') or not (0 <= idx < len(self.words_data)):
            return False
        key = self.words_data[idx].get('word', '')
        key = key.strip().strip('.,!?;:，。！？；：').lower()
        return key in self.favorites

    @Slot(int)
    def _on_toggle_favorite_idx(self, idx: int):
        if not hasattr(self, 'words_data') or not (0 <= idx < len(self.words_data)):
            return
        raw = self.words_data[idx].get('word', '')
        word = raw.strip().strip('.,!?;:，。！？；：').lower()
        if not word:
            return
        if word in self.favorites:
            self.favorites.remove(word)
        else:
            self.favorites.add(word)
        self._render_transcript()
        self._refresh_favorites_page()
        self._save_favorites()

    # Compatible with old connection name
    @Slot(int)
    def _on_word_toggle_favorite_requested(self, idx: int):
        self._on_toggle_favorite_idx(idx)

    def _refresh_favorites_page(self):
        if not hasattr(self, 'favorites_list'):
            return
        self.favorites_list.clear()
        for w in sorted(self.favorites):
            brief = self._format_brief_for_word(w)
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 48))
            item.setData(Qt.UserRole, w)
            self.favorites_list.addItem(item)
            widget = FavoriteItemWidget(w, brief)
            self.favorites_list.setItemWidget(item, widget)

    def _remove_selected_favorite(self):
        if not hasattr(self, 'favorites_list'):
            return
        items = self.favorites_list.selectedItems()
        if not items:
            return
        for it in items:
            text = it.data(Qt.UserRole)
            if text and text in self.favorites:
                self.favorites.remove(text)
        self._refresh_favorites_page()
        self._render_transcript()
        self._save_favorites()

    def _format_brief_for_word(self, w: str) -> str:
        entry = self.dictionary.lookup(w.strip().strip('.,!?;:，。！？；：'))
        if not entry:
            return ""
        phon = entry.get('phonetic') or ""
        pos = entry.get('pos') or ""
        trans = entry.get('translation') or ""
        if len(trans) > 80:
            trans = trans[:80] + "…"
        parts = []
        if phon:
            parts.append(f"/{phon}/")
        if pos:
            parts.append(pos)
        if trans:
            parts.append(trans)
        return "  |  ".join(parts)

    def _open_favorite_detail(self, item):
        word = item.data(Qt.UserRole) if item else None
        if not word:
            return
        entry = self.dictionary.lookup(word)
        if not entry:
            detail_html = f"<b>{word}</b><br/><span style='color:#999'>无词典记录</span>"
        else:
            def esc(t: str) -> str:
                return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # 构建详细的收藏详情显示（与搜索页面一致）
            detail_html = f"<h2 style='margin:0; color:#1f2937; font-size:20px;'>{esc(entry.get('word',''))}</h2>"
            
            # 音标（可点击播放）
            if entry.get('phonetic'):
                detail_html += f"<div style='margin:8px 0;'><a href='#speak_word' style='color:#059669; text-decoration:none; font-size:16px; font-weight:500; cursor:pointer;'>🔊 /{esc(entry.get('phonetic',''))}/</a></div>"
            else:
                detail_html += f"<div style='margin:8px 0;'><a href='#speak_word' style='color:#059669; text-decoration:none; font-size:16px; font-weight:500; cursor:pointer;'>🔊 点击播放发音</a></div>"
            
            # 词性
            if entry.get('pos'):
                detail_html += f"<div style='margin:8px 0;'><span style='color:#4338ca; font-size:13px; background:rgba(67,56,202,0.1); padding:2px 6px; border-radius:4px;'>{esc(entry.get('pos',''))}</span></div>"
            
            # 英译英
            if entry.get('definition'):
                detail_html += f"""
                <div style='margin:12px 0; padding:10px; background:rgba(239,246,255,0.8); border-left:3px solid #3b82f6; border-radius:4px;'>
                    <div style='color:#dc2626; font-size:14px; font-weight:600; margin-bottom:6px;'>🇺🇸 English Definition</div>
                    <div style='color:#1f2937; font-size:15px; line-height:1.4; font-style:italic;'>{esc(entry.get('definition',''))}</div>
                </div>
                """
            
            # 中文翻译
            if entry.get('translation'):
                detail_html += f"""
                <div style='margin:12px 0; padding:10px; background:rgba(254,249,195,0.8); border-left:3px solid #f59e0b; border-radius:4px;'>
                    <div style='color:#dc2626; font-size:14px; font-weight:600; margin-bottom:6px;'>🇨🇳 中文释义</div>
                    <div style='color:#374151; font-size:15px; line-height:1.4;'>{esc(entry.get('translation',''))}</div>
                </div>
                """
        # 临时用搜索页显示详情
        if hasattr(self, 'search_result') and hasattr(self, 'search_input'):
            # 设置详情显示模式
            self._showing_detail = True
            # 直接显示详情内容和设置搜索框
            self.search_result.setHtml(detail_html)
            self.search_input.setText(word)
            self._switch_tab(3)

    def _perform_search(self):
        if not hasattr(self, 'search_input') or not hasattr(self, 'search_result'):
            return
        q = self.search_input.text().strip()
        print(f"[DEBUG] _perform_search 被调用，搜索内容: '{q}'")
        print(f"[DEBUG] 详情模式状态: {getattr(self, '_showing_detail', False)}")
        
        # 如果搜索框为空，不做任何操作，保持当前内容
        if not q:
            print("[DEBUG] 搜索框为空，保持当前内容不变")
            return
            
        # 只有当用户输入新内容并回车时，才进行搜索和更新页面
        print(f"[DEBUG] 开始搜索新内容: '{q}'")
        # 清除详情显示模式，进入正常搜索模式
        self._showing_detail = False
            
        entry = self.dictionary.lookup(q.strip().strip('.,!?;:，。！？；：'))
        if not entry:
            self.search_result.setHtml(f"<b>{q}</b><br/><span style='color:#999'>无词典记录</span>")
            return
        def esc(t: str) -> str:
            return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # 构建详细的搜索结果显示
        html_content = f"<h2 style='margin:0; color:#1f2937; font-size:20px;'>{esc(entry.get('word',''))}</h2>"
        
        # 音标（可点击播放）
        if entry.get('phonetic'):
            html_content += f"<div style='margin:8px 0;'><a href='#speak_word' style='color:#059669; text-decoration:none; font-size:16px; font-weight:500; cursor:pointer;'>🔊 /{esc(entry.get('phonetic',''))}/</a></div>"
        else:
            html_content += f"<div style='margin:8px 0;'><a href='#speak_word' style='color:#059669; text-decoration:none; font-size:16px; font-weight:500; cursor:pointer;'>🔊 点击播放发音</a></div>"
        
        # 词性
        if entry.get('pos'):
            html_content += f"<div style='margin:8px 0;'><span style='color:#4338ca; font-size:13px; background:rgba(67,56,202,0.1); padding:2px 6px; border-radius:4px;'>{esc(entry.get('pos',''))}</span></div>"
        
        # 英译英
        if entry.get('definition'):
            html_content += f"""
            <div style='margin:12px 0; padding:10px; background:rgba(239,246,255,0.8); border-left:3px solid #3b82f6; border-radius:4px;'>
                <div style='color:#dc2626; font-size:14px; font-weight:600; margin-bottom:6px;'>🇺🇸 English Definition</div>
                <div style='color:#1f2937; font-size:15px; line-height:1.4; font-style:italic;'>{esc(entry.get('definition',''))}</div>
            </div>
            """
        
        # 中文翻译
        if entry.get('translation'):
            html_content += f"""
            <div style='margin:12px 0; padding:10px; background:rgba(254,249,195,0.8); border-left:3px solid #f59e0b; border-radius:4px;'>
                <div style='color:#dc2626; font-size:14px; font-weight:600; margin-bottom:6px;'>🇨🇳 中文释义</div>
                <div style='color:#374151; font-size:15px; line-height:1.4;'>{esc(entry.get('translation',''))}</div>
            </div>
            """
        
        self.search_result.setHtml(html_content)

    def _on_search_anchor_clicked(self, url):
        """处理搜索页面的链接点击事件"""
        print(f"[DEBUG] 点击链接: {url.toString()}")
        url_str = url.toString()
        if url_str == "speak_word" or url_str == "#speak_word":
            # 获取当前搜索的单词并播放
            word = self.search_input.text().strip()
            print(f"[DEBUG] 搜索框内容: '{word}'，准备播放语音")
            
            if word:
                # 直接播放语音，不刷新页面
                clean_word = word.strip('.,!?;:，。！？；：').lower()
                self._speak_word(clean_word)

    def _add_search_to_favorites(self):
        if not hasattr(self, 'search_input'):
            return
        q = self.search_input.text().strip().strip('.,!?;:，。！？；：').lower()
        if not q:
            return
        self.favorites.add(q)
        self._refresh_favorites_page()
        self._render_transcript()
        self._save_favorites()