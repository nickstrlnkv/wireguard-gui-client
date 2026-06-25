# Wireguard GUI client for Linux
A modern, fast, and independent graphical user interface (GUI) for managing WireGuard connections in Linux. The project is designed specifically for beginners and casual users who want to use a secure VPN tunnel without the need for a terminal or CLI commands.

## Features

* **Complete independence:** The application is independent of desktop environments (GNOME, KDE, XFCE) and looks equally modern on any distribution.
* **Convenient import:** Add .conf configuration files with one click via the native file explorer.
* **Local storage:** All imported profiles are neatly stored in the local confs/ directory within the project.
* **Modern UI:** Responsive  interface based on Material Design 3 guidelines.

## Tech stack
 
| Component        | Purpose                                           |
| ---------------- | ------------------------------------------------- |
| Python 3.10+     | Application language                              |
| [Flet](https://flet.dev/) (`flet`) | GUI framework (Flutter renderer) |
| `wireguard-tools` (`wg-quick`, `wg`) | Brings the VPN tunnel up/down |
| `polkit` (`pkexec`) | Runs `wg-quick` as root with a GUI auth dialog |
 

> The only Python dependency is `flet`. `wireguard-tools` and `polkit` are
> **system packages** and must be installed via your distribution's package
> manager (they are not pip packages).
 
## Requirements
 
- A Linux desktop (developed/tested on Fedora KDE Plasma; works on other distros)
- Python **3.10+**
- System packages:
  - `wireguard-tools` — provides `wg-quick` and `wg`
  - `polkit` — provides `pkexec` and a graphical authentication agent (usually
    preinstalled on GNOME/KDE)


### Install system dependencies
 
**Fedora / RHEL:**
```bash
sudo dnf install wireguard-tools polkit
```

**Debian / Ubuntu:**
```bash
sudo apt install wireguard-tools policykit-1
```

### For Fedora/CentOS/RHEL
```bash
sudo dnf install wireguard-tools gstreamer1-plugins-bad-free
```

**Arch:**
```bash
sudo pacman -S wireguard-tools polkit
```



## Local Launch and Development
You can clone the repository and run the project locally by following these steps:

### 1. Cloning repository
```bash
git clone https://github.com/nickstrlnkv/wireguard-gui-client.git
cd wireguard-gui-client
```

### 2. Create and activate a virtual environment (venv)
Create an isolated environment to prevent project dependencies from conflicting with system packages:
```bash
python3 -m venv venv
source venv/bin/activate
```
Once activated, you should see `(venv)` at the beginning of your terminal prompt.

### 3. Installing Dependencies
Install Flet and other required packages within the virtual environment:
```bash
pip install -r requirements.txt
```

### 4. Launch the application
Make sure you're in the project's root folder (where `main.py` is located) and run:
```bash
python3 src/main.py
```

or with Flet's hot reload during development :)
```bash
flet run src/main.py
```

## Project structure
 
```
wireguard-gui-client/
├── src/
│   ├── main.py        # application entry point and UI
│   ├── settings.py    # window title/size/colors and other constants
│   └── confs/         # imported .conf files (git-ignored, see Security)
├── requirements.txt
└── README.md
```

## Security & permissions
 
This app handles VPN configuration files that contain **private keys**, and it
runs a tool that requires **root privileges**. Please keep the following in mind:
 
- **Root access via `pkexec`.** `wg-quick` cannot create network interfaces
  without root. The app launches it through `pkexec`, which shows a graphical
  authentication dialog each time. The app itself runs as your normal user —
  only the `wg-quick` call is elevated. **Do not run the whole GUI with `sudo`.**
- **`.conf` files contain secrets.** WireGuard config files include your
  private key. Imported files are stored in `src/confs/` and should be created
  with `0600` permissions (owner read/write only):
  ```python
  os.chmod(dest, 0o600)
  ```
  If you see `Warning: '...' is world accessible`, the permissions are too open.
- **Never commit `.conf` files.** Make sure `src/confs/` is in `.gitignore` so
  private keys never end up in version control:
  ```gitignore
  src/confs/
  *.conf
  ```
- **Interface name limits.** `wg-quick up <path>` derives the interface name
  from the file name (without `.conf`). Linux interface names are limited to
  ~15 characters and may contain only letters, digits, `_`, `-`, `.`. Keep file
  names short (e.g. `home.conf`, not `my-very-long-config-name.conf`).
- **Optional passwordless setup.** If you want to avoid the password prompt on
  every connect, add a narrowly-scoped polkit rule (in
  `/etc/polkit-1/rules.d/`) or a `sudoers` entry limited to `wg-quick` only.
  Grant the minimum necessary — never make `wg-quick` blanket-passwordless for
  all users.
 

## Contributing
 
Contributions are welcome!
 
1. Fork the repository and create a feature branch:
   ```bash
   git checkout -b feature/my-change
   ```
2. Set up the dev environment (see [Getting started](#getting-started)).
3. Make your changes. Please:
   - Keep edits focused and follow the existing code style.
   - Do **not** commit real `.conf` files or any secrets.
   - Update the README if you change setup, dependencies, or behavior.
4. Test that the app launches and that connect/disconnect work against a real
   WireGuard config on your machine.
5. Commit with a clear message and open a Pull Request describing **what**
   changed and **why**.
 
Bug reports and feature requests: please open an issue with steps to reproduce,
your distro/desktop environment, Python version, and Flet version
(`pip show flet`).
 
