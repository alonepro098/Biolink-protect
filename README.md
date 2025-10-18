<h1 align="center">BioLink Protector Telegram Bot</h1>

<p align="center">
  <a href="https://github.com/strad-dev131/BioLink-Protector"><img src="https://img.shields.io/github/stars/strad-dev131/BioLink-Protector?color=blue&style=flat" alt="GitHub Repo stars"></a>
  <a href="https://github.com/strad-dev131/BioLink-Protector/issues"><img src="https://img.shields.io/github/issues/strad-dev131/BioLink-Protector" alt="GitHub issues"></a>
  <a href="https://github.com/strad-dev131/BioLink-Protector/pulls"><img src="https://img.shields.io/github/issues-pr/strad-dev131/BioLink-Protector" alt="GitHub pull requests"></a>
  <a href="https://github.com/strad-dev131/BioLink-Protector/graphs/contributors"><img src="https://img.shields.io/github/contributors/strad-dev131/BioLink-Protector?style=flat" alt="GitHub contributors"></a>
  <a href="https://github.com/strad-dev131/BioLink-Protector/network/members"><img src="https://img.shields.io/github/forks/strad-dev131/BioLink-Protector?style=flat" alt="GitHub forks"></a>
</p>

<p align="center">
  <em>BioLink Protector is a Telegram bot that automatically monitors user bios in group chats for links. If a link is found, the bot can warn, mute, or ban based on configurable settings—helping maintain a clean and safe environment.</em>
</p>
<hr>

## What's New

- More reliable link detection using normalization + linkify-it (handles obfuscations like `hxxp`, `[dot]`, Unicode confusables, bare domains).
- Scans bios both on message and when users join the group.
- Configurable penalty duration (temporary mute/ban) with `/setduration`, or permanent by setting to `0`.
- Toggle detection per group with `/toggle` and view config with `/status`.
- Faster admin checks with caching; reduces API calls, better performance on large groups.
- Works 24×7 on any VPS (tested on Python 3.12), and deployable to Heroku or Render.

## Features

- Auto-scan bios for links when users post.
- Configurable **warnings**, **mutes**, **bans**.
- **Whitelist** & **Unwhitelist** trusted members.
- **Cancel Warning** to reset a user’s warnings.
- **Admin-only controls** with interactive inline keyboards.
- On-join scanning to catch link-in-bio before users post.

## 🎮 Demo Bot

Try it live: [@LinkXdetectorBot](https://t.me/LinkXdetectorBot)

## Requirements

- Python 3.8+ (recommended 3.12)
- MongoDB (Atlas or self-hosted)
- Environment variables: `API_ID`, `API_HASH`, `BOT_TOKEN`, `MONGO_URI`

## Installation

```bash
git clone https://github.com/strad-dev131/BioLink-Protector
cd BioLink-Protector
pip install -r requirements.txt
```

## Configuration

Set environment variables or edit `config.py`:

- `API_ID` / `API_HASH` from [my.telegram.org](https://my.telegram.org)
- `BOT_TOKEN` from [@BotFather](https://t.me/BotFather)
- `MONGO_URI` MongoDB connection string
- Optional defaults:
  - `DETECTION_ENABLED` (default: true)
  - `DEFAULT_PENALTY_DURATION` in seconds (default: 0 for permanent)

## Deploy

### Run locally / VPS
```sh
python bio.py
```

To run 24×7 on a VPS, use `systemd`:
```
[Unit]
Description=BioLink Protector Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/biolink-protector
ExecStart=/usr/bin/python3 /opt/biolink-protector/bio.py
Restart=always
Environment=API_ID=...
Environment=API_HASH=...
Environment=BOT_TOKEN=...
Environment=MONGO_URI=...

[Install]
WantedBy=multi-user.target
```

### Heroku
- Push this repo to Heroku.
- Set env vars in the app settings: `API_ID`, `API_HASH`, `BOT_TOKEN`, `MONGO_URI`.
- Procfile runs: `worker: python bio.py`.

### Render
- Create a new Web Service.
- Runtime: Python.
- Start command: `python bio.py`.
- Set env vars: `API_ID`, `API_HASH`, `BOT_TOKEN`, `MONGO_URI`.

## Usage

Admin commands:
- `/config` → choose “Warn”, “Mute”, or “Ban” and set warn count
- `/free [reply|id]` → whitelist a user
- `/unfree [reply|id]` → remove from whitelist
- `/freelist` → view all whitelisted users
- `/status` → show current configuration
- `/toggle` → enable/disable bio scanning
- `/setduration <seconds|30m|2h|1d|0>` → temporary or permanent penalty duration

Auto-scan:
- When a non-whitelisted user posts, their bio is checked—warn/mute/ban applies.
- New members’ bios are checked on join.

✨ **Note**: Fork + Star the repo if you liked it, and share with proper credit.

## Author

- Name: Elite Sid
- Telegram: [@TeamXUpdate](https://t.me/TeamXUpdate)

Feel free to reach out if you have any questions or feedback.
