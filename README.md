# 🎙️ EchoScribe

<div align="center">
  
  **Professional Audio Transcription & Language Learning Tool**
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![Platform](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/TravelerLby/EchoScribe)
</div>

---

## 📖 Overview

EchoScribe is a powerful desktop application that transforms audio transcription into an interactive learning experience. Built with advanced AI technology, it offers precise word-level timing, comprehensive dictionary integration, and an intuitive interface designed for language learners, researchers, and professionals.

### ✨ Why EchoScribe?

- **🎯 Precision**: Word-level timing accuracy for seamless audio navigation
- **📚 Learning-Focused**: Built-in dictionary with pronunciations and translations
- **🎨 User-Friendly**: Modern, customizable interface with smooth animations
- **🔊 Interactive**: Click any word to jump to that exact moment in audio
- **💾 Offline**: Works completely offline - no internet required
- **🌍 Multi-Language**: English-Chinese dictionary with phonetic transcriptions

---

## 🚀 Key Features

### 🎵 Audio Processing
- **Multi-Format Support**: MP3, WAV, OGG, FLAC, M4A
- **High-Quality Transcription**: Powered by OpenAI's Whisper model
- **Real-Time Progress**: Live transcription progress with smooth animations
- **Drag & Drop**: Simple file import with intuitive interface

### 📝 Interactive Transcription
- **Word-Level Clicking**: Jump to any word's timestamp instantly
- **Smart Text Wrapping**: Automatic sentence breaks and word wrapping
- **Hover Effects**: Beautiful word highlighting with smooth transitions
- **Edit Capability**: Right-click to modify any transcribed word

### 📖 Comprehensive Dictionary
- **Instant Lookup**: Right-click any word for definitions
- **Rich Information**: Phonetics, part of speech, Chinese translations
- **English Definitions**: Complete English-to-English explanations
- **Search Function**: Dedicated dictionary search with full details

### 🔖 Vocabulary Management
- **Smart Favorites**: Save words for later study
- **Visual Highlighting**: Favorited words stand out in transcripts
- **Quick Management**: Easy add/remove with visual feedback
- **Persistent Storage**: Favorites saved locally across sessions

### 🎨 Customization
- **Font Control**: Adjustable text sizes (14px-22px)
- **Line Spacing**: Compact, standard, or loose layouts
- **Tooltip Settings**: Customizable hover delays and font sizes
- **Audio Controls**: Variable playback speeds and volume control

### 🔊 Text-to-Speech
- **Word Pronunciation**: Click to hear any word spoken
- **Speed Control**: Adjustable speech rates for learning
- **Auto-Pause Option**: Pause audio when tooltips appear
- **Threading**: Smooth playback without UI freezing

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.8 or higher
- **RAM**: 4GB (8GB recommended for large audio files)
- **Storage**: 2GB free space (includes models and dependencies)
- **Audio**: Standard audio output device

### Required Dependencies
- **FFmpeg**: Essential for audio format support
  - 🪟 **Windows**: Included in the application (no separate installation needed)

---

## 📦 Installation

### 🎯 Option 1: Ready-to-Use Executable (Recommended)

**Download the latest release**: [📥 Releases Page](https://github.com/TravelerLby/EchoScribe/releases)

#### Windows Users:
- **🔧 Installer**: `EchoScribe-Setup.exe` - Full installation with shortcuts
- **📱 Portable**: `EchoScribe-Portable.exe` - No installation required

### 🛠️ Option 2: From Source (For Developers)

#### Step 1: Clone Repository
```bash
git clone https://github.com/TravelerLby/EchoScribe.git
cd EchoScribe
```

#### Step 2: Download Required Assets
**⚠️ Important**: The repository doesn't include large model files and FFmpeg binaries. You need to download them separately:

1. **Go to [Releases Page](https://github.com/TravelerLby/EchoScribe/releases)**
2. **Download these files from the latest release**:
   - 📦 `Models.zip` (~120MB) - Contains Whisper AI model files
   - 🛠️ `vendor.zip` (~120MB) - Contains FFmpeg executables
3. **Extract to project root**:
   ```bash
   # Extract Models.zip to create Models/ directory
   unzip Models.zip
   
   # Extract vendor.zip to create vendor/ directory  
   unzip vendor.zip
   ```

#### Step 3: Setup Environment
```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 4: Run Application
```bash
python -m Echoscribe.main
```

#### 🔍 Verify Setup
After extraction, your project structure should look like this:
```
EchoScribe/
├── Echoscribe/           # ✅ From repository
├── Assets/               # ✅ From repository  
├── Models/               # 📦 From Models.zip
│   └── faster_whisper_base_en/
│       ├── config.json
│       ├── model.bin     # ~500MB file
│       ├── tokenizer.json
│       └── vocabulary.txt
├── vendor/               # 🛠️ From vendor.zip
│   └── ffmpeg/
│       ├── ffmpeg.exe    # Windows
│       ├── ffprobe.exe   # Windows
│       ├── ffmpeg        # macOS/Linux
│       └── ffprobe       # macOS/Linux
├── requirements.txt      # ✅ From repository
├── build.spec           # ✅ From repository
└── README.md            # ✅ From repository
```

---

## 🎮 Quick Start Guide

### 1️⃣ First Launch
1. **Open EchoScribe** - Double-click the executable or run from source
2. **Check Audio Setup** - Ensure your audio device is working
3. **Verify FFmpeg** - The app will notify you if FFmpeg is missing

### 2️⃣ Basic Workflow
1. **📂 Import Audio**
   - Click "Import audio file" button, or
   - Drag and drop audio file into the window
   
2. **⏳ Wait for Transcription**
   - Watch the progress bar (can be hidden in settings)
   - Transcription time varies by audio length and system performance
   
3. **🎯 Interactive Playback**
   - Click any word to jump to that timestamp
   - Use playback controls for normal play/pause
   - Adjust speed with the speed slider

4. **📚 Dictionary Features**
   - Right-click any word for instant definitions
   - Hover over words to see quick tooltips
   - Search specific words in the Search tab

5. **⭐ Build Your Vocabulary**
   - Right-click words to add to favorites
   - Visit the Favorites tab to review saved words
   - Delete unwanted favorites with one click

### 3️⃣ Advanced Features
- **🎨 Customize Appearance**: Visit Settings tab for fonts and layouts
- **🔊 Audio Settings**: Adjust volume, speed, and auto-play options
- **💡 Tooltip Control**: Configure hover delays and tooltip sizes
- **🎤 Text-to-Speech**: Enable pronunciation features in settings

---

## 📁 Complete Project Structure

### 🗂️ Full Directory Layout
```
EchoScribe/                    # Project root directory
├── 📦 Echoscribe/            # ✅ Main application package (from repository)
│   ├── 🧠 Core/             # Business logic layer
│   │   ├── __init__.py      # Package initializer
│   │   ├── dictionary.py    # Dictionary management & ECDICT integration
│   │   └── transcriber.py   # Whisper model wrapper & audio processing
│   ├── 🎨 ui/               # User interface layer
│   │   ├── __init__.py      # Package initializer
│   │   ├── main_window.py   # Main application window & all UI logic
│   │   └── style.py         # CSS stylesheets & visual themes
│   ├── __init__.py          # Package initializer
│   └── 🚀 main.py           # Application entry point & initialization
├── 📂 Assets/                # ✅ Static resources (from repository)
│   ├── ⚙️ config/          # Default configuration files
│   │   ├── settings.json    # Default application settings
│   │   └── favorites.json   # Default favorites (empty)
│   ├── 📖 dict/            # Dictionary data
│   │   └── ecdict.csv       # ECDICT English-Chinese dictionary (~50MB)
│   ├── 🔤 fonts/           # Custom fonts
│   │   └── font.ttf         # Application font
│   └── 🎯 icons/           # Application icons
│       └── echoscribe.ico   # Windows application icon
├── 🤖 Models/                # 📦 AI models (from Models.zip - ~120MB)
│   └── faster_whisper_base_en/ # Whisper model files
│       ├── config.json      # Model configuration
│       ├── model.bin        # Main model weights
│       ├── tokenizer.json   # Text tokenizer
│       └── vocabulary.txt   # Model vocabulary
├── 🛠️ vendor/              # 🛠️ Third-party tools (from vendor.zip - ~120MB)
│   └── ffmpeg/             # FFmpeg binaries
│       ├── ffmpeg.exe      # FFmpeg executable (Windows)
│       └── ffprobe.exe     # Media info tool (Windows)
├── 📋 requirements.txt      # ✅ Python dependencies (from repository)
├── 🔧 build.spec           # ✅ PyInstaller build configuration (from repository)
├── ⚖️ LICENSE.txt          # ✅ MIT license (from repository)
└── 📖 README.md            # ✅ This documentation (from repository)
```

### 📥 Download Sources

| Component | Source | Size | Description |
|-----------|--------|------|-------------|
| **Core Code** | 🔗 Git Repository | ~2MB | Main application code, UI, assets |
| **AI Models** | 📦 `Models.zip` | ~120MB | Whisper transcription model files |
| **FFmpeg Tools** | 🛠️ `vendor.zip` | ~120MB | Audio processing executables |

### ⚠️ Important Notes for Developers

1. **Repository Only Contains**:
   - Source code (`Echoscribe/` directory)
   - Static assets (`Assets/` directory)
   - Configuration files (`requirements.txt`, `build.spec`, etc.)

2. **Must Download Separately**:
   - **`Models.zip`** - Contains the Whisper model files (~120MB)
   - **`vendor.zip`** - Contains FFmpeg executables for audio processing (~120MB)

3. **Why This Structure?**:
   - **Git Efficiency**: Keeps repository lightweight
   - **Platform Support**: Different FFmpeg binaries for each OS
   - **License Compliance**: Clear separation of components with different licenses

4. **First-Time Setup Checklist**:
   - [ ] Clone repository
   - [ ] Download `Models.zip` from releases
   - [ ] Download `vendor.zip` from releases  
   - [ ] Extract both ZIP files to project root
   - [ ] Install Python dependencies
   - [ ] Verify all directories exist as shown above

---

## ⚙️ Configuration

### 🎛️ Application Settings
EchoScribe automatically saves all your preferences:

- **🎨 Visual Settings**: Font sizes, line heights, UI themes
- **🔊 Audio Settings**: Volume, playback speed, auto-play options
- **💡 Tooltip Settings**: Hover delays, tooltip fonts, display options
- **📚 Learning Settings**: TTS speed, pause-on-tooltip behavior

### 📍 Configuration Locations
Settings and favorites are stored in:

- **🪟 Windows**: `%APPDATA%\EchoScribe\`
  - Example: `C:\Users\YourName\AppData\Roaming\EchoScribe\`

### 🗂️ Configuration Files
- `settings.json` - Application preferences and UI settings
- `favorites.json` - Your saved vocabulary words

---

## 🔧 Building from Source

### Prerequisites
```bash
pip install pyinstaller
```

### Build Commands
```bash
# Create standalone executable
pyinstaller build.spec --clean

# Output location:
# - Windows: dist/EchoScribe.exe
```

### 📦 Creating Release Assets

For maintainers preparing releases:

#### 1. Create Models.zip
```bash
# Compress the Models directory
zip -r Models.zip Models/
# Result: Models.zip (~120MB)
```

#### 2. Create vendor.zip  
```bash
# Compress the vendor directory
zip -r vendor.zip vendor/
# Result: vendor.zip (~120MB)
```

#### 3. Release Checklist
- [ ] Build executable for target platform
- [ ] Create `Models.zip` with all model files
- [ ] Create `vendor.zip` with FFmpeg binaries
- [ ] Test clean installation from scratch
- [ ] Upload all files to GitHub releases
- [ ] Update download links in README

### Build Configuration
The `build.spec` file includes:
- All necessary dependencies and hidden imports
- Asset bundling (models, dictionaries, FFmpeg)
- Platform-specific optimizations  
- Icon and metadata configuration

### 🎯 Development vs Release Structure

| Environment | Models/ | vendor/ | Source | Platform |
|-------------|---------|---------|---------|----------|
| **Development** | ✅ Local files | ✅ Local files | Git repo | Windows |
| **User Release** | 📦 In executable | 📦 In executable | Pre-built EXE | Windows |
| **Dev Setup** | 📥 Models.zip | 📥 vendor.zip | Git clone | Windows |

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 Bug Reports
1. Check existing [GitHub Issues](https://github.com/TravelerLby/EchoScribe/issues)
2. Create detailed bug reports with:
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Audio file details (if relevant)

### 💡 Feature Requests
1. Browse [GitHub Discussions](https://github.com/TravelerLby/EchoScribe/discussions)
2. Propose new features with:
   - Clear use cases
   - Implementation ideas
   - Mockups or examples (if applicable)

### 🔧 Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with clear commit messages
4. Add tests if applicable
5. Submit a pull request with detailed description

### 📝 Documentation
- Improve README sections
- Add code comments
- Create user tutorials
- Translate documentation

---

## 📜 License & Attribution

### 📄 Main License
This project is licensed under the **MIT License** - see the [LICENSE.txt](LICENSE.txt) file for details.

### 🙏 Third-Party Components

EchoScribe builds upon amazing open-source projects:

#### 🤖 AI & Machine Learning
- **[OpenAI Whisper](https://github.com/openai/whisper)** - Speech recognition model (MIT License)
- **[faster-whisper](https://github.com/guillaumekln/faster-whisper)** - Optimized Whisper implementation (MIT License)

#### 📖 Dictionary Data
- **[ECDICT](https://github.com/skywind3000/ECDICT)** by skywind3000 - English-Chinese dictionary (MIT License)
  - 📊 **140,000+ entries** with phonetics, definitions, and translations
  - 🎯 **High-quality data** curated for language learning

#### 🎨 User Interface
- **[PySide6](https://www.qt.io/qt-for-python)** - Cross-platform GUI framework (LGPL License)
- **[Qt Framework](https://www.qt.io/)** - Underlying UI toolkit (LGPL License)

#### 🔊 Audio Processing
- **[FFmpeg](https://ffmpeg.org/)** - Multimedia framework (LGPL License)
- **[pydub](https://github.com/jiaaro/pydub)** - Audio manipulation library (MIT License)

#### 🗣️ Text-to-Speech
- **[pyttsx3](https://github.com/nateshmbhat/pyttsx3)** - Cross-platform TTS library (MPL License)

### ⚖️ License Compatibility
All components used in EchoScribe are compatible with commercial and non-commercial use. The combination of MIT and LGPL licenses allows for:
- ✅ Personal use
- ✅ Commercial use
- ✅ Modification and distribution
- ✅ Private use

---

## 🌟 Support & Community

### 💬 Get Help
- **📋 Issues**: [GitHub Issues](https://github.com/TravelerLby/EchoScribe/issues) for bugs and technical problems
- **💭 Discussions**: [GitHub Discussions](https://github.com/TravelerLby/EchoScribe/discussions) for questions and ideas
- **📧 Contact**: Open an issue for direct communication

### 🎯 Roadmap & Future Plans
- **🌍 Multi-language Support**: Additional language pairs beyond English-Chinese
- **☁️ Cloud Integration**: Optional cloud-based model updates
- **📱 Mobile Companion**: Sync favorites across devices
- **🎓 Learning Features**: Spaced repetition and vocabulary tests
- **🔌 Plugin System**: Community-developed extensions

### 💝 Show Your Support

If EchoScribe helps with your work or learning:

- ⭐ **Star this repository** - Helps others discover the project
- 🐦 **Share on social media** - Spread the word about free language learning tools
- 🗣️ **Leave feedback** - Your suggestions shape future development
- 🐛 **Report issues** - Help us improve the experience for everyone
- 🤝 **Contribute code** - Join our development community

### 🙏 Acknowledgments

Special thanks to:
- **OpenAI** for making Whisper open source
- **skywind3000** for the comprehensive ECDICT database
- **The Python community** for incredible tools and libraries
- **All contributors** who help improve EchoScribe
- **Users** who provide feedback and bug reports

---

<div align="center">
  
**🎉 Thank you for using EchoScribe! 🎉**

*Made with ❤️ for language learners and audio professionals worldwide*

---

**[⬆️ Back to Top](#-echoscribe)** | **[📥 Download](https://github.com/TravelerLby/EchoScribe/releases)** | **[🐛 Report Bug](https://github.com/TravelerLby/EchoScribe/issues)** | **[💡 Request Feature](https://github.com/TravelerLby/EchoScribe/discussions)**

</div>