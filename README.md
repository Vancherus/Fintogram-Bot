## <h1 align="center">Fintogram - асинхронный telegram-бот, позволяющий сохранять мыслеформы (англ. thoughtforms) и делиться ими с пользователями.</a>
<p align="center">
  <img width="494" height="497" alt="логотип" src="https://github.com/user-attachments/assets/8c44599f-6f44-4480-b8c5-2da4a500f1eb" />
</p>  
<b>Мыслеформа</b> - это цифровой контейнер мысли/идеи, которому присваивается собственный идентификатор. 
<hr>
<h3 align='center'>При этом <b>Fintogram</b> очень универсален: вы можете как хранить свои идеи, так и делиться ими. Хранение выполняется в PostgreSQL.</h3>
<hr>
Добавленные/полученные мыслеформы с идентификаторами можно посмотреть по кнопке 'Мои мыслеформы' в inline-меню:
<p align="center">
  <img width="447" height="272" alt="изображение" src="https://github.com/user-attachments/assets/b1133f81-d09d-4087-980b-d4fbd2a1accd" />
</p>  
Отправка происходит по telegram username'у получателя и уникальному ID мыслеформы (можно скопировать по inline-кнопке, см. выше):
<p align="center">
  <img width="593" height="89" alt="изображение" src="https://github.com/user-attachments/assets/dcc5ee88-ca98-43b0-95b6-a1bba93cd199" />
  <img width="604" height="277" alt="изображение" src="https://github.com/user-attachments/assets/c3e8ff89-6a57-4c6d-b7f3-376920b34a44" />
</p>
Бот разработан таким образом, что при попытке отправить мыслеформу, получателю в тот же момент придет уведомление о том, кто хочет ему ее отправить.
Получателю при этом дается право согласиться/отказаться от получения мыслеформы. 
<hr>
<h3 align='center'>Таким образом, с помощью Fintogram можно оставлять личные сообщения платными, давая возможность пользователелям возможность отправлять бесплатные запросы на отправку мыслей/идей (ведь уведомления приходят в чат с ботом). </h3>
<hr>

## 📦 Установка и запуск
1. **Клонируй репозиторий:**
   ```bash
   git clone https://github.com/vancherus/fintogrambot.git
   cd fintogrambot
2. **Создай и активируй виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/Scripts/acivate
3. **Установи зависимости:**
   ```bash
   pip install -r requirements.txt  
4. **Создай .env-файл с токеном бота (можно взять у @BotFather) и DSN (Data Source Name) - строкой, которую использует SQLAlchemy (в связке с драйвером asyncpg) для подключения к базе данных:**
   ```bash
   BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ
   DB_URL=postgresql+asyncpg://name:password@localhost:5432/database_name
Где name - имя пользователя в PostgreSQL (указывается в pgadmin), password - пароль для этого пользователя, localhost - адрес сервера БД (localhost = тот же пк, где запущен бот), 5432 - стандартный порт для PostgreSQL, database_name - имя базы данных.

5. **Запусти бота:**
   ```bash
   python app.py
Готово! Бот запущен и готов к работе 🎉  

<h2 align='center'>🤝 Вклад</h2>
<p align='center'>PR и issues приветствуются! Хочешь добавить новую функцию? Напиши issue или сделай fork.</p>
