"""
EchoScribe Application Stylesheet

Defines the main visual styling for the EchoScribe application interface.
Includes styles for windows, buttons, sliders, and other UI components.
"""

MAIN_STYLE_SHEET = """
/* Root window */
QMainWindow { background-color: transparent; }
#RootWidget {
    background-color: #F0F2F5;
    border-radius: 12px;
    border: 1px solid #D9D9D9;
}

/* Title bar */
#TitleBar {
    background-color: #F0F2F5;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}
#TitleLabel {
    color: #004C99;
    font-weight: bold;
    font-size: 16px;
    padding-left: 10px;
}
/* Close button styling */
QWidget#TitleBar QPushButton#CloseButton {
    background-color: #0078D4;
    color: #FFFFFF;
    font-size: 16px;
    font-weight: bold;
    border: none;
    border-radius: 6px;
    padding: 0px;
}
QWidget#TitleBar QPushButton#CloseButton:hover {
    background-color: #1086E4;
}
QWidget#TitleBar QPushButton#CloseButton:pressed {
    background-color: #006AC4;
}

/* Left sidebar tabs */
#TabBar {
    background-color: #E4E9F2;
    border-right: 1px solid #D9D9D9;
    border-bottom-left-radius: 12px;
}
#TabBar QPushButton {
    border: none;
    background-color: transparent;
    color: #595959;
    font-weight: bold;
    border-radius: 8px;
    margin: 5px;
}
#TabBar QPushButton:hover { background-color: #D0D8E8; }
#TabBar QPushButton:checked { background-color: #FFFFFF; color: #0078D4; }

/* Other controls */
QStackedWidget > QWidget { background-color: #FFFFFF; }
QPushButton {
    background-color: #0078D4; color: white; font-weight: bold;
    padding: 10px 15px; border-radius: 5px; border: none; font-size: 14px;
}
QPushButton:hover { background-color: #1086E4; }
QPushButton:pressed { background-color: #006AC4; }
#TranscriptArea { background-color: #F8F9FA; border: 1px solid #D9D9D9; border-radius: 5px; }
#TranscriptArea QWidget { background-color: #F8F9FA; }
#TranscriptArea QLabel { font-size: 16px; color: #333333; }
QLabel { background-color: transparent; color: #595959; font-size: 14px; }
#PlayPauseButton { padding: 5px; }
QSlider::groove:horizontal { border: 1px solid #bbb; background: #f0f0f0; height: 6px; border-radius: 3px; }
QSlider::handle:horizontal { background: #0078D4; border: 1px solid #0078D4; width: 14px; height: 14px; margin: -4px 0; border-radius: 7px; }
QSlider::sub-page:horizontal { background: #0078D4; border: 1px solid #bbb; height: 6px; border-radius: 3px; }
QProgressBar { border: 1px solid #D9D9D9; border-radius: 5px; background-color: #FFFFFF; text-align: center; }
QProgressBar::chunk { background-color: #0078D4; border-radius: 4px; }
QCheckBox { spacing: 5px; color: #333333; }
QCheckBox::indicator { width: 15px; height: 15px; border: 1px solid #D9D9D9; border-radius: 3px; }
QCheckBox::indicator:unchecked { background-color: white; }
QCheckBox::indicator:checked { background-color: #0078D4; }
QComboBox { border: 1px solid #D9D9D9; border-radius: 4px; padding: 5px; background-color: white; }
QComboBox:hover { border: 1px solid #0078D4; }
QComboBox::drop-down { border: none; width: 20px; }
"""