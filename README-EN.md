<h1 align="center">AnimLoid</h1>

<p align="center">
  <strong>A powerful, cross-platform command-line tool for anime enthusiasts</strong>
</p>

<p align="center">
  <a href="https://github.com/RetakJunior/AnimLoid/releases"><img src="https://img.shields.io/github/v/release/RetakJunior/AnimLoid?style=flat-square" alt="Release"></a>
  <a href="https://github.com/RetakJunior/AnimLoid/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-blue?style=flat-square" alt="License"></a>
  <a href="https://github.com/RetakJunior/AnimLoid/stargazers"><img src="https://img.shields.io/github/stars/RetakJunior/AnimLoid?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/RetakJunior/AnimLoid/actions"><img src="https://img.shields.io/github/actions/workflow/status/RetakJunior/AnimLoid/tests.yml?style=flat-square" alt="Tests"></a>
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#features">Features</a> •
  <a href="#usage">Usage</a> •
  <a href="#sources">Sources</a> •
  <a href="README.md">Türkçe</a>
</p>

---

## Features

### Multiple Sources

- **Turkish**: Animecix, Turkanime, Anizle
- **English**: HiAnime, AllAnime

### Smart Streaming

- High-quality HLS/MP4 playback with MPV
- Resume from where you left off (timestamp-based)
- Watch history and statistics
- Completed (✓) and in-progress (●) episode markers

### Powerful Download System

- **Aria2** for multi-connection fast downloads
- **yt-dlp** for complex stream support
- Queue system with concurrent downloads
- Resume interrupted downloads
- Smart file naming (`Anime Name - S1E1.mp4`)

### Local Library

- Auto-scan downloaded anime
- External drive support (USB, HDD)
- Offline anime indexing
- Search across all sources

### Additional Features

- SQLite database (fast and reliable)
- System notifications on download completion
- Discord RPC integration (show what you're watching on Discord)
- Search history
- Debug mode and logging
- Automatic update checks

---

## Installation

### PyPI (Universal)

```bash
pip install animloid
```

### Portable

Download the appropriate file for your platform from [Releases](https://github.com/RetakJunior/AnimLoid/releases).

### Developer Setup

```bash
git clone https://github.com/RetakJunior/AnimLoid.git
cd AnimLoid
pip install -e .
```

---

## Usage

```bash
animloid
```

### Keyboard Controls

| Key      | Action                   |
| -------- | ------------------------ |
| `↑` `↓`  | Navigate menu            |
| `Enter`  | Select                   |
| `s`      | Search Anime (Main menu) |
| `d`      | Downloads (Main menu)    |
| `w`      | Watchlist (Main menu)    |
| `c`      | Settings (Main menu)     |
| `q`      | Exit (Main menu)         |
| `Ctrl+C` | Go back / Exit           |

**Note:** All shortcuts can be customized in Settings > Keyboard Shortcuts.

---

## Sources

| Source    | Language |
| --------- | -------- |
| Animecix  | Turkish  |
| Turkanime | Turkish  |
| Anizle    | Turkish  |
| HiAnime   | English  |
| AllAnime  | English  |

---

## Configuration

Config location: `~/.animloid/animloid.db` (SQLite)

| Setting                    | Description          | Default                |
| -------------------------- | -------------------- | ---------------------- |
| `aria2_enabled`            | Use Aria2            | `true`                 |
| `max_concurrent_downloads` | Concurrent downloads | `3`                    |
| `download_dir`             | Download folder      | `./animloid-downloads` |
| `discord_rpc_enabled`      | Discord RPC          | `false`                |
| `debug_mode`               | Debug logging        | `false`                |

---

## License

This project is licensed under [CC BY-NC-ND 4.0](LICENSE).

---

<p align="center">
  <a href="https://github.com/RetakJunior/AnimLoid/issues">Report Issue</a>
</p>
