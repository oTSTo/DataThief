![Alt text](https://github.com/oTSTo/DataThief/blob/2356ca995eea0228b924623e2e7478b9460bdb2d/DataThiefLogo.png)
<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
  </a>
</p>

## Description
The code is a keylogger integrated with a Telegram bot that allows remote monitoring and control of a computer.
## Features
| **Feature**                  | **Description**                                                                 |
|------------------------------|---------------------------------------------------------------------------------|
| **Keylogger**                | Records keystrokes and sends them to the Telegram bot.                          |
| **Autostart**                | Moves the executable to the Windows startup folder to run automatically on boot.|
| **Startup Notification**     | Sends a message to the bot with the date, time, username, and IP address on startup. |
| **Command `/startlog`**      | Starts the keylogger.                                                           |
| **Command `/stoplog`**       | Stops the keylogger.                                                            |
| **Command `/infopc`**        | Displays system information (username, OS, IP address, etc.).                   |
| **Command `/infofile`**      | Displays the directory of the executable file.                                  |
| **Command `/rtask`**         | Lists running tasks (excluding system processes).                               |
| **Command `/popup`**         | Displays a pop-up with a specified message (e.g., `/popup Hello From Maximilian Bossets!`).       |
| **Command `/webcam`**        | Captures an image from the webcam and sends it to the bot.                      |
| **Command `/screenshot`**    | Captures a screenshot and sends it to the bot.                                  |
| **Command `/changewp`**      | Changes the desktop wallpaper using an image from a specified URL.              |
| **Command `/startrecaudio`** | Starts audio recording.                                                         |
| **Command `/stoprecaudio`**  | Stops audio recording and sends the file to the bot.                            |
| **Command `/panic`**         | Terminates the current process (PANIC mode).                                    |
| **Command `/taskkill`**      | Terminates a specific process (e.g., `/taskkill chrome.exe`).                   |
| **Command `/shutdown`**      | Shuts down the computer.                                                        |
| **Command `/users`**         | Displays the list of active users with their username, IP address, and unique ID.|
| **Command `/selectuser`**    | Selects a specific user to perform actions on (e.g., `/selectuser PC1`).        |
| **Command `/help`**          | Displays the list of available commands and their status (READY, PROGRESS, DONT WORK). |
| **Hide the file**            | Hides the file in the startup folder to make it less visible.                    |
| **Remote Management**        | All operations can be performed remotely via the Telegram bot.                   |
## MUST-HAVE
- [Telegram](https://telegram.org/)
- [Telegram Bot](https://telegram.me/BotFather) You can create one with [@BotFather](https://telegram.me/BotFather)

## CHANGES TO BE MADE IN THE CODE
- Add the BOT `TOKEN`
- Add the your `CHATID`
## HOW TO GET `TOKEN` AND `CHATID`
- The `TOKEN` is provided to you at the end of the bot creation process with [@BotFather](https://telegram.me/BotFather). <br>
- The `CHATID` can be obtained by following these steps:
  - Start the BOT.
  - Send any message to the bot.
  - Open a new window and enter https://api.telegram.org/bot`YOUR_TOKEN`/getUpdates.
  - The answer will be a JSON like this below
  - Copy the value inside `update_id` (it should be a number). In the example, it would be `YOUR UPDATE ID`.
```sh
{
  "ok": true,
  "result": [
    {
      "update_id": `YOUR UPDATE ID`,
      "message": {
        "message_id": 123,
        "from": {
          "id": 1234567890,
          "is_bot": false,
          "first_name": "Your Name",
          "last_name": "Your Surname",
          "username": "Your Telegram ID",
          "language_code": "en"
        },
        "chat": {
          "id": 1234567890,
          "first_name": "Your Name",
          "last_name": "Your Surname",
          "username": "Your Telegram ID",
          "type": "private"
        },
        "date": 1234567890,
        "text": "Message you send"
      }
    }
  ]
}
```
## ESSENTIAL LIBRARIES
```sh
#Execute this command for install the libraries
pip install telebot pynput psutil opencv-python pillow requests pyaudio

```
Libraries `os`, `threading`, `platform`, `socket`, `sys`, `shutil`, `subprocess`, e `datetime` are standard Python libraries, so there is no need to install them separately.
