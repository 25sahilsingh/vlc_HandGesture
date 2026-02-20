import time
from time import sleep
import cv2
import mediapipe as mp
import subprocess
import socket
# ===============================
# CONFIG
# ===============================
VIDEO_FILE = "sample.mp4"
MODEL_PATH = "gesture_recognizer.task"
VLC_HOST = "127.0.0.1"
VLC_PORT = 9999
MIN_X = 0.15   # ignore left 15%
MAX_X = 0.85   # ignore right 15%
SEEK_THRESHOLD = 3  # seconds, to reduce jitter
last_seek = None
MIN_Y = 0.25      # ignore top 15%
MAX_Y = 0.75      # ignore bottom 15%
VOLUME_THRESHOLD = 2   # percent change to avoid jitter
last_volume = 256
SEEK_SENSITIVITY = 300
VOLUME_SENSITIVITY = 300

# ===============================
# VLC CONTROLLER
# ===============================

class VLCController:
    def __init__(self):
        self.proc = subprocess.Popen(
            [
                "vlc",
                VIDEO_FILE,
                "--extraintf", "rc",
                "--rc-host", f"{VLC_HOST}:{VLC_PORT}",
                "--no-video-title-show",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Give VLC a moment to open RC socket (small, practical delay)
        time.sleep(1)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((VLC_HOST, VLC_PORT))

        # 🔥 IMPORTANT: drain VLC RC startup banner ONCE
        try:
            self.sock.recv(4096)
        except Exception:
            pass

    def send(self, cmd: str):
        try:
            self.sock.sendall((cmd + "\n").encode())

            response = self.sock.recv(4096).decode()

            # remove RC prompt and whitespace
            response = response.replace(">", "").strip()
            return response

        except Exception:
            return ""

    def close(self):
        try:
            self.send("quit")
            self.sock.close()
        except Exception:
            pass

# ===============================
# MEDIAPIPE SETUP
# ===============================

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
RunningMode = mp.tasks.vision.RunningMode
Image = mp.Image

_latest_gestures = []
_latest_landmarks = []
_latest_handedness=[]
playing=True
fullscreen=False
video_length=0
# ===============================
# MODES
# ===============================
MODE = "NORMAL"  # NORMAL | SEEK | VOLUME
prev_x = None
prev_y = None

# ===============================
# CALLBACK
# ===============================

def result_callback(result, output_image, timestamp_ms):
    global _latest_gestures, _latest_landmarks,_latest_handedness
    _latest_gestures = []
    _latest_landmarks = []
    _latest_handedness=[]
    if result and result.gestures:
        for i in range(len(result.gestures)):
            gesture = result.gestures[i][0]
            _latest_gestures.append(gesture.category_name)

    if result and result.hand_landmarks:
        for hand in result.hand_landmarks:
            _latest_landmarks.append([(lm.x, lm.y) for lm in hand])
    if result and result.handedness:
        for i in range(len(result.handedness)):
            hand = result.handedness[i][0]  # first category
            _latest_handedness.append(hand.category_name)
        # -_latest_handedness.append(result)
# ===============================
# HELPERS
# ===============================

# ===============================
# GESTURE HANDLER
# ===============================

def handle_gestures(vlc: VLCController):
    global MODE, prev_x, prev_y,playing,fullscreen,video_length
    rightindex=1
    #needed if you want to know which gesture is being detected
   # print(_latest_handedness)
   # print(_latest_gestures)
    if len(_latest_handedness)==1:
        global last_volume
        if(_latest_gestures[0]=="Closed_Fist"):
            if playing:
                vlc.send("pause")
                playing=False
            else:
                pass
        if(_latest_gestures[0]=="Open_Palm"):
            vlc.send("play")
            playing=True
        if _latest_gestures[0]=="Thumb_Up":
            print(last_volume)
            if last_volume is not None:
                vlc.send("volume "+str(last_volume))
        if _latest_gestures[0]=="Thumb_Down":
            if last_volume is not None:
                vlc.send("volume 0")
    if len(_latest_handedness)>1:
        if(_latest_handedness[0]=="Left"):#format of latest_gesture=[['Open_Palm', 'Right'], ['Open_Palm', 'Left']] 0
            rightindex=0
        global last_seek

        if _latest_gestures[not rightindex] == "Closed_Fist" and _latest_gestures[rightindex] == "Pointing_Up":

            x = _latest_landmarks[rightindex][8][0]  # fingertip X (0–1)

            # 1️⃣ Clamp to usable range
            x = max(MIN_X, min(x, MAX_X))

            # 2️⃣ Normalize to 0–1
            x_norm = (x - MIN_X) / (MAX_X - MIN_X)

            # 3️⃣ Map to video length
            seek_target = int(x_norm * video_length)

            # 4️⃣ Optional jitter control
            if last_seek is None or abs(seek_target - last_seek) >= SEEK_THRESHOLD:
                print("Seeking to:", seek_target)
                vlc.send("seek " + str(seek_target))
                last_seek = seek_target



        if _latest_gestures[not rightindex] == "Open_Palm" and _latest_gestures[rightindex] == "Pointing_Up":

            y = _latest_landmarks[rightindex][8][1]  # fingertip Y (0–1)

            # 1️⃣ Clamp usable range
            y = max(MIN_Y, min(y, MAX_Y))

            # 2️⃣ Normalize to 0–1 (invert Y: up = louder)
            y_norm = 1.0 - ((y - MIN_Y) / (MAX_Y - MIN_Y))

            # 3️⃣ Map to VLC volume (0–100)
            volume_target = int(y_norm * 320)

            # 4️⃣ Optional jitter control
            if last_volume is None or abs(volume_target - last_volume) >= VOLUME_THRESHOLD:
                print("Volume:", volume_target)
                vlc.send("volume " + str(volume_target))
                last_volume = volume_target
        # NEXT MEDIA
        if _latest_gestures[not rightindex] == "Open_Palm" and _latest_gestures[rightindex] == "Thumb_Up":
            vlc.send("next")

        # PREVIOUS MEDIA
        if _latest_gestures[not rightindex] == "Thumb_Up" and _latest_gestures[rightindex] == "Open_Palm":
            vlc.send("prev")

        if _latest_gestures[not rightindex] == "Open_Palm" and _latest_gestures[rightindex] == "Open_Palm":
            if not fullscreen:
                vlc.send("F")
                fullscreen=True
        if _latest_gestures[not rightindex] == "Closed_Fist" and _latest_gestures[rightindex] == "Closed_Fist":
            vlc.send("shutdown")
        if _latest_gestures[not rightindex] == "Thumb_Down" and _latest_gestures[rightindex] == "Thumb_Down":
            vlc.send("stop")
# ===============================
# MAIN
# ===============================

def main():
    vlc = VLCController()
    global video_length
    options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=RunningMode.LIVE_STREAM,
        result_callback=result_callback,
        num_hands=2,
    )

    recognizer = GestureRecognizer.create_from_options(options)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
    if not cap.isOpened():
        print("Camera not available")
        return
    while True:#this while and try is to get the int value and not the start value in console
        try:
            video_length = vlc.send("get_length")
            video_length = int(video_length)
            break
        except:
            pass
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            recognizer.recognize_async(
                mp_image,
                int(time.time() * 1000)
            )

            handle_gestures(vlc)
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        cap.release()
        vlc.close()

# ===============================
# ENTRY
# ===============================

if __name__ == "__main__":
    main()
