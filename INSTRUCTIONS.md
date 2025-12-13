# INSTRUCTIONS TO INSTALL MONKEYTRAIN ON PYTHON

---

## Hardware Needed
- A computer (Windows, macOS, or Linux)
- Internet connection (for downloading)
- Installation generally takes around 5 - 10 minutes

---

# Installation Steps
Step 1: Install Python
*Python is the programming language that runs MonkeyTrain*

#### **WINDOWS USERS:**

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow button that says **"Download Python 3.x.x"**
3. Once downloaded, open the installer file
4. **IMPORTANT:** Check the box that says **"Add Python to PATH"**
5. Click **"Install Now"**
6. Wait for installation to finish (1-2 minutes)
7. Click **"Close"**



#### **MacOS USERS**
1. Open **Terminal** (find it in Applications → Utilities)
2. Copy and paste this command, then press Enter:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Wait for Homebrew to install (this might take a few minutes)
4. Type this command and press Enter:
   ```bash
   brew install python3
   ```
5. Wait for Python to install

**Verify it worked:**
- In Terminal, type `python3 --version`
- You should see something like `Python 3.12.0`



#### **LINUX USERS**
1. Open **Terminal**
2. Type these commands one at a time:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```
3. Enter your password when asked

**Verify it worked:**
- Type `python3 --version`
- You should see something, like `Python 3.12.0`

---

### Step 2: Install Pygame
*Pygame is the library that creates the game window and graphics.*

#### **WINDOWS USERS:**
1. Open **Command Prompt**:
   - Press `Windows Key`
   - Type `cmd`
   - Press Enter
2. Type this command and press Enter:
   ```bash
   pip install pygame
   ```
3. Wait for installation (30-60 seconds)
4. You should see: `Successfully installed pygame-2.x.x`



#### **MacOS USERS:**

1. Open **Terminal**
2. Type this command and press Enter:
   ```bash
   pip3 install pygame
   ```
3. Wait for installation (30-60 seconds)
4. You should see: `Successfully installed pygame-2.x.x`



#### **LINUX USERS:**

1. Open **Terminal**
2. Type this command and press Enter:
   ```bash
   pip3 install pygame
   ```
3. Wait for installation (30-60 seconds)
4. You should see: `Successfully installed pygame-2.x.x`

---

### Step 4: Run the Game

#### **Windows:**

**Method 1 - Using Command Prompt (Recommended):**
1. Open **Command Prompt** (`Windows Key`, type `cmd`, press Enter)
2. Navigate to your game folder:
   ```bash
   cd Desktop\MonkeyTrain
   ```
3. Run the game:
   ```bash
   python monkeytrain.py
   ```
4. The game window should appear!

**Method 2 - Double Click:**
1. Find `monkeytrain.py` in your folder
2. Right-click it
3. Choose **"Open with"** → **"Python"**
4. The game window should appear!

#### **macOS:**

1. Open **Terminal**
2. Navigate to your game folder:
   ```bash
   cd ~/Desktop/MonkeyTrain
   ```
3. Run the game:
   ```bash
   python3 monkeytrain.py
   ```
4. The game window should appear!

#### **Linux:**

1. Open **Terminal**
2. Navigate to your game folder:
   ```bash
   cd ~/Desktop/MonkeyTrain
   ```
3. Run the game:
   ```bash
   python3 monkeytrain.py
   ```
4. The game window should appear!

--

## 🎮 You're Ready!
Once you see the MonkeyTrain game window with the main menu, you're all set!
