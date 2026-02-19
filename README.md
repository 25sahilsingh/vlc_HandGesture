# 🖐️ VLC Hand Gesture Controller (Jetson Orin Nano)

Minimal, optimized gesture-controlled VLC media player built for **NVIDIA Jetson Orin Nano (JetPack 6.x)** using **MediaPipe + OpenCV (Headless) + VLC RC Interface**.

---

## 🚀 Clone Repository

```bash
git clone https://github.com/25sahilsingh/vlc_HandGesture.git
cd vlc_HandGesture
```

---

## 🏗️ System Requirements

- **Hardware:** NVIDIA Jetson Orin Nano  
- **OS:** JetPack 6.x (Ubuntu 22.04 LTS)  
- **Python:** 3.10 (Required for MediaPipe stability)  
- **Camera:** USB Webcam (USB 3.0 recommended)  

---

## 📁 Minimal Project Structure

```
vlc_HandGesture/
│── main.py
│── gesture_recognizer.task
│── gesture_image/
│    ├── open_palm.png
│    ├── closed_fist.png
│    ├── pointing_up.png
│    ├── thumb_up.png
│    ├── thumb_down.png
│── Report.docx
│── README.md
│── .gitignore
```

### Structure Notes

- `main.py` → Main execution script  
- `gesture_recognizer.task` → MediaPipe gesture model  
- `gesture_image/` → Gesture reference images mapped to actions  
- `Report.docx` → Project documentation/report  
- `README.md` → Setup + usage instructions  

---

# 🛠️ Installation

---

## 1️⃣ Install Python 3.10 (via pyenv – Recommended)

⚠️ Do NOT modify system Python on Jetson.

### 🔹 Install Required Build Dependencies (IMPORTANT)

```bash
sudo apt update
sudo apt install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl git \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
libffi-dev liblzma-dev
```

These dependencies are required for successfully compiling Python via pyenv on Ubuntu 22.04 / JetPack 6.x.

---

### 🔹 Install pyenv

```bash
curl -fsSL https://pyenv.run | bash
```

---

## 🔹 Configure Bash Startup Files (IMPORTANT)

Stock Bash startup files vary between Linux distributions.  
To ensure pyenv works in **both interactive and login shells**, add configuration to:

- `~/.bashrc`
- AND one of: `~/.profile`, `~/.bash_profile`, or `~/.bash_login`

---

### Add to `~/.bashrc`

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
```

---

### If you have `~/.profile`

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
echo 'eval "$(pyenv init - bash)"' >> ~/.profile
```

---

### OR if you use `~/.bash_profile`

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init - bash)"' >> ~/.bash_profile
```

---

### ⚠️ Important Bash Warning

Some systems configure `BASH_ENV` to source `.bashrc` automatically.

On such systems, you should put:

```
eval "$(pyenv init - bash)"
```

ONLY in `.bash_profile`, NOT in `.bashrc`.

Otherwise, you may experience:
- Infinite shell loop
- Strange pyenv behavior

(See pyenv issue #264 for details.)

---

## 🔹 Restart Shell

```bash
exec "$SHELL"
```

---

## 🔹 Install Python 3.10 (Recommended Specific Version)

```bash
pyenv install 3.10.13
pyenv global 3.10.13
pyenv rehash
python --version
```

Expected:

```
Python 3.10.13
```

---

## 2️⃣ Install VLC

```bash
sudo apt update
sudo apt install vlc -y
```

---

## 3️⃣ Install Python Dependencies

```bash
pip install --upgrade pip
pip install mediapipe
pip install opencv-python-headless
```

---

# ▶️ Run

Place your video file in the project directory.

```bash
python main.py
```

---

# 🎮 Gesture → Action Mapping

Gesture reference images are inside `gesture_image/`.

| Gesture | Action |
|----------|----------|
| 🖐 Open Palm | Play |
| ✊ Closed Fist | Pause |
| ☝ Pointing Up (Right Hand) | Volume Control (Slide Up/Down) |
| ✊ + ☝ | Seek (Slide Left/Right) |
| 👍 Thumb Up | Next Media |
| 👎 Thumb Down | Stop Playback |
| 🖐 + 🖐 | Toggle Fullscreen |
| ✊ + ✊ | Shutdown Script |

> Lighting and clear background significantly improve detection accuracy.

---

# ⚡ Jetson Optimization (Important)

Enable max performance mode:

```bash
sudo nvpmodel -m 0
sudo jetson_clocks
```

Kill existing VLC if RC port error occurs:

```bash
pkill vlc
```

If webcam does not start, change:

```python
cv2.VideoCapture(0)
```

to:

```python
cv2.VideoCapture(1)
```

---

# 🧠 Performance Tips

- Use 720p webcam resolution  
- Avoid cluttered background  
- Use USB 3.0 port  
- Close unused applications  
- Ensure adequate lighting  

---

# 📄 Documentation

`Report.docx` contains:

- System architecture  
- Gesture recognition pipeline  
- VLC RC communication design  
- Jetson-specific performance considerations  

For professional publishing, consider adding:

- Architecture diagram (PNG inside repo)  
- Demo GIF  
- Short 30-sec demo video  

---

# 📌 Notes

- Designed specifically for JetPack 6.x  
- Python 3.10 mandatory  
- Uses VLC Remote Control (RC) interface on port 9999  
- Optimized for Jetson Orin Nano hardware constraints  

---

# 🔮 Future Improvements

- Gesture sensitivity calibration  
- On-screen overlay feedback  
- Playlist support  
- Custom gesture training  

---
