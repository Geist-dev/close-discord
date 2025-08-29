# 🎮 Close Bot

**Close Bot** — лучший русскоязычный Discord-бот для организации матчей в **CS2, Dota 2 и Valorant**.  
Он автоматизирует процесс создания игр, управляет каналами, распределяет команды и помогает модераторам вести учёт игроков.  

![Banner](https://media.discordapp.net/attachments/1190674471619661987/1410780540772159609/2a52c4ab-9c98-4784-88fc-2a36e191d72a.png?ex=68b24343&is=68b0f1c3&hm=9a3c149478adfb16cd666f2fe20c4ab3cc9646676e937231eefc3827ac2d145b&=&format=webp&quality=lossless&width=1240&height=826) <!-- Можешь заменить путь на свою картинку баннера -->

---

## ✨ Возможности

- 📌 Автоматическое создание **игровых лобби** (`/close create`)
- 🎲 Распределение **капитанов и команд**
- 🔒 Управление **голосовыми каналами** (создание, удаление, права доступа)
- 📊 Учёт статистики, мутов, киков и банов
- ⚙️ Гибкая настройка через `/config`
- 🔔 Логирование всех действий
- ⏳ Автоматическое снятие наказаний по времени
- ✅ Поддержка **CS2 / Dota 2 / Valorant**

---

## 🚀 Установка и запуск

### Требования
- Python **3.10+**
- [Git](https://git-scm.com/)
- [Discord Developer Application](https://discord.com/developers/applications)

### Установка

```bash
# Клонируем репозиторий
git clone https://github.com/USERNAME/close-bot.git
cd close-bot

# Создаём виртуальное окружение
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

# Устанавливаем зависимости
pip install -r requirements.txt

# Запуск бота
python main.py
```

---

## ⚙️ Конфигурация

1. Создай бота в [Discord Developer Portal](https://discord.com/developers/applications).  
2. Скопируй токен и укажи его в `.env` файле:

```env
TOKEN=твой_токен
PREFIX=! 
```

3. Добавь бота на сервер.  
4. Используй команду:
```
/config
```
и настрой роли, каналы логов и прочие параметры.

---

## 📂 Структура проекта

```
close-bot/
│── cogs/                # Коги (модули бота)
│── utils/               # Утилиты (например, работа с БД)
│── dbs/                 # SQLite база данных
│── main.py              # Точка входа
│── requirements.txt
│── README.md
```

---

## 🔧 Запуск на сервере с PM2

```bash
pm2 start main.py --name close-bot --interpreter python3
pm2 save
```

---

## 🤝 Вклад

Pull Requests и предложения приветствуются!  
Если хочешь помочь в развитии бота — пиши в Issues.

---

## 📜 Лицензия

MIT License © 2025  
Свободно используйте и модифицируйте проект.
