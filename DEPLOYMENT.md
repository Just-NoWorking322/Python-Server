# 🚀 Инструкция по бесплатному деплою проекта «ТОП СТР»

Проект полностью настроен для запуска на популярных бесплатных облачных серверах (**Render**, **Railway**, **PythonAnywhere**).
Все необходимые файлы (`Procfile`, `build.sh`, `render.yaml`, `whitenoise`, `requirements.txt`) уже добавлены в репозиторий.

---

## Вариант 1: Деплой на Render.com (Самый простой и рекомендуемый способ, 100% бесплатно)

Render предоставляет бесплатный хостинг для веб-сервисов с автоматическим деплоем из GitHub и бесплатным SSL-сертификатом (HTTPS).

### Пошаговая инструкция (занимает 3 минуты):

1. **Зарегистрируйтесь на сайте [Render.com](https://render.com/)**
   * Войдите через ваш аккаунт **GitHub**.
2. **Создайте новый Web Service:**
   * В панели управления Render нажмите синюю кнопку **«New +»** в правом верхнем углу и выберите **«Web Service»**.
3. **Подключите ваш GitHub репозиторий:**
   * Выберите репозиторий `Just-NoWorking322/Python-Server`.
   * Нажмите кнопку **«Connect»**.
4. **Укажите базовые настройки проекта:**
   * **Name:** `top-str` (или любое желаемое имя)
   * **Region:** Frankfurt (EU) или любой ближайший
   * **Branch:** `deploy` (или `main`, если объедините ветку)
   * **Runtime:** `Python 3`
   * **Build Command:**
     ```bash
     ./build.sh
     ```
     *(скрипт сам установит зависимости, соберет статику, применит миграции и наполнит базу тестовыми данными)*
   * **Start Command:**
     ```bash
     gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
     ```
   * **Instance Type:** Выберите **Free** ($0 / month).
5. **Нажмите «Deploy Web Service»:**
   * Render запустит сборку. Через 1–2 минуты ваш сайт будет доступен в интернете по постоянному адресу:
     `https://top-str.onrender.com` (или имя, которое вы указали).

---

## Вариант 2: Деплой на Railway.app

1. Перейдите на [Railway.app](https://railway.app/) и авторизуйтесь через GitHub.
2. Нажмите **«New Project»** -> **«Deploy from GitHub repo»**.
3. Выберите репозиторий `Just-NoWorking322/Python-Server` (ветку `deploy`).
4. Railway автоматически обнаружит `Procfile` и развернет веб-сервер.
5. Во вкладке **Settings** сгенерируйте публичный домен: **«Generate Domain»**.

---

## Вариант 3: Деплой на PythonAnywhere (Бесплатный тариф)

1. Зарегистрируйтесь на [PythonAnywhere.com](https://www.pythonanywhere.com/).
2. Откройте вкладку **Consoles** -> **Bash** и клонируйте репозиторий:
   ```bash
   git clone https://github.com/Just-NoWorking322/Python-Server.git
   cd Python-Server
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py seed_data
   ```
3. Во вкладке **Web** создайте новое веб-приложение на Django, укажите путь к `wsgi.py` и активируйте виртуальное окружение.

---

## 🔑 Учетные записи после деплоя (создаются автоматически скриптом `seed_data`):

* 👑 **Администратор:**
  * Логин: `admin`
  * Пароль: `admin123`
* 🛠 **Мастера:**
  * Сантехник: `master_santehnik` / `master123`
  * Клинер: `master_cleaner` / `master123`
  * Репетитор: `master_tutor` / `master123`
  * IT-мастер: `master_it` / `master123`
  * Стилист: `master_beauty` / `master123`

---

## 🌐 Страницы на развернутом сервере:
* Главная страница сайта (Каталог, поиск, заказ): `https://<ваш-домен>/`
* Интерактивная документация для мобилки и фронтенда: `https://<ваш-домен>/swagger/`
* Панель управления (Админка): `https://<ваш-домен>/admin/`
