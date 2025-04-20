# ExuviaAgent 🤖

ExuviaAgent is a multilingual Telegram bot for class booking, progress tracking, and user interaction in a CrossFit or fitness environment.

Built with [Aiogram](https://github.com/aiogram/aiogram), it provides:
- 📆 Class scheduling and enrollment
- 💪 WOD and performance tracking
- 🧑‍🤝‍🧑 Role-based menu navigation
- 🌍 Internationalization (i18n) support
- 🧪 Mocked development mode with test users and classes
- 🔐 Telegram ID-based user configuration via `.env`

---

## 📦 Features

- **Inline Menu Navigation** based on user role  
- **My Classes & Upcoming Classes** with real-time toggle enrollment  
- **Dynamic InlineKeyboardButtons** reflecting subscription state  
- **Notion (or mock) backend abstraction**  
- **Multilingual support** with `.po/.mo` files (English and Italian)

---

## 🚀 Getting Started

### 1. Clone the repo

```
git clone https://github.com/your-org/ExuviaAgent.git
cd ExuviaAgent
```

### 2. Create and activate a virtual environment

```
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```
TELEGRAM_TOKEN=your-telegram-bot-token
APP_ENV=development  # or production

# Mock User IDs
USER_TG_ID_FRANCESCO=XXX
USER_TG_ID_LUCIA=YYY
USER_TG_ID_MANUEL=ZZZ
```

---

## 💬 Commands

The bot is menu-driven, but supports these base commands:

- `/start` – Start the bot
- `/my_classes` – Quick access to enrolled classes

---

## 🗂 Project Structure

```
ExuviaAgent/
├── handlers/         # Aiogram handlers (start, navigation, schedule)
├── keyboards/        # Inline menus & callback structures
├── models/           # Role definitions, schema enums
├── notion/           # Integration & mock logic for class/user data
├── locales/          # i18n .po/.mo files
├── config.py         # Settings and bot initialization
├── main.py           # Entry point
```

---

## 🌐 Localization

Translations are located under `/locales/<lang>/LC_MESSAGES/exuviaagent.po`. Compile them with:

```
msgfmt locales/en/LC_MESSAGES/exuviaagent.po -o locales/en/LC_MESSAGES/exuviaagent.mo
msgfmt locales/it/LC_MESSAGES/exuviaagent.po -o locales/it/LC_MESSAGES/exuviaagent.mo
```

---

## 🧪 Development Mode

Set `APP_ENV=development` to:

- Use mock class/user data
- Log Telegram IDs for new users
- Test role-based access with pre-defined IDs

---

## 📋 TODO

- [ ] Admin panel for managing classes  
- [ ] Notion API integration in production  
- [ ] Class waitlist support  
- [ ] Reminder system  

---

## 👥 Authors

- Francesco Mondora – [@fmondora](https://github.com/fmondora)  
- Assisted by ChatGPT 🤖  

---

## 📄 License

This project is licensed under the **GNU Lesser General Public License v3.0 (LGPL-3.0)**.  
See [LICENSE](LICENSE) for full details.
