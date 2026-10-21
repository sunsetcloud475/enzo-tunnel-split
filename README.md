# EnzoArena Split Tunneling

**EnzoArena Split Tunneling** is a modern Windows application that allows you to force specific programs to use a particular network interface (Ethernet, Wi-Fi, VPN, etc.).

This is useful when you want certain applications (games, browsers, download managers, etc.) to go through a different network connection than the rest of your system — true **app-based split tunneling**.

---

### Features

- Beautiful and modern dark interface
- Fully Persian (Farsi) + RTL support
- Select any network interface available on your system
- Create and save rules for applications
- Launch applications bound to a specific interface
- Pick apps from running processes or by browsing

---

### Requirements

- Windows 10 / 11
- Python 3.9 or higher
- **ForceBindIP** (required)

> **Important:** This application depends on [ForceBindIP](https://r1ch.net/projects/forcebindip) to bind applications to a specific network interface.  
> You must place `ForceBindIP64.exe` in the same folder as the application.

---

### Installation

1. Download or clone this repository
2. Install the required packages:

```bash
pip install customtkinter psutil
