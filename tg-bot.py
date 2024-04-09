import telebot
import psycopg2
import re

# Установка соединения с базой данных PostgreSQL
conn = psycopg2.connect(
    host="",
    port="",
    database="DB_proekt",
    user="postgres",
    password=""
)
cursor = conn.cursor()

# Инициализация бота
bot = telebot.TeleBot('6918700653:AAF8-WR7hY8hBy*******************')


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    bot.send_message(user_id,
                     "Приветствуем вас в нашем магазине STEAM-аккаунтов. Здесь вы сможете продать свой аккаунт, а также купить аккаунт другого пользователя. Для продолжения выберите интересующую вас услугу:",
                     reply_markup=create_main_keyboard())


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    if message.text == "Продать":
        handle_sell(message)
    elif message.text == "Купить":
        handle_buy(message)
    else:
        bot.send_message(user_id, "Неизвестная команда. Выберите доступную опцию.")


def handle_sell(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Введите ссылку на аккаунт:")
    bot.register_next_step_handler(message, handle_account_link)


def handle_account_link(message):
    user_id = message.chat.id
    account_link = message.text.strip()

    # Проверка соответствия ссылки на аккаунт требуемой маске ввода
    if re.match(r"https://steamcommunity.com/profiles/\d{17}/", account_link):
        # Проверка наличия аккаунта в базе данных
        if check_account_exists(account_link):
            bot.send_message(user_id, "Такой аккаунт уже существует. Попробуйте другой ссылку:")
            bot.register_next_step_handler(message, handle_account_link)
            return
        bot.send_message(user_id, "Укажите уровень аккаунта:")
        bot.register_next_step_handler(message, handle_steam_level, account_link)
    else:
        bot.send_message(user_id, "Неверная ссылка на аккаунт. Попробуйте снова.")
        bot.register_next_step_handler(message, handle_account_link)


def handle_steam_level(message, account_link):
    user_id = message.chat.id
    steam_level = message.text

    # Проверяем, является ли введенный текст числом
    if not re.match(r'^\d+$', steam_level):
        bot.send_message(user_id, "Ошибка! Введите число в качестве уровня аккаунта:")
        bot.register_next_step_handler(message, handle_steam_level, account_link)
        return

    bot.send_message(user_id, "Какие игры у вас есть на аккаунте? Введите их через запятую:")
    bot.register_next_step_handler(message, handle_games, account_link, steam_level)


def handle_games(message, account_link, steam_level):
    user_id = message.chat.id
    games = message.text.split(",")

    # Рассчитываем приблизительную стоимость аккаунта
    approx_price = int(steam_level) * 20  # 20 рублей за каждый уровень

    # Добавляем стоимость за игры
    for game in games:
        if "csgo" in game.lower():
            approx_price += 450
        elif "rust" in game.lower():
            approx_price += 550
        elif "pubg" in game.lower():
            approx_price += 150
        else:
            approx_price += 20

    bot.send_message(user_id, f"Приблизительная стоимость аккаунта: {approx_price} рублей. Введите свою цену:")
    bot.register_next_step_handler(message, handle_price, account_link, steam_level, games)


def handle_price(message, account_link, steam_level, games):
    user_id = message.chat.id
    price = message.text

    bot.send_message(user_id, "Введите логин:")
    bot.register_next_step_handler(message, handle_login, account_link, steam_level, games, price)


def handle_login(message, account_link, steam_level, games, price):
    user_id = message.chat.id
    login = message.text

    bot.send_message(user_id, "Введите пароль:")
    bot.register_next_step_handler(message, handle_password, account_link, steam_level, games, price, login)


def handle_password(message, account_link, steam_level, games, price, login):
    user_id = message.chat.id
    password = message.text

    # Запрос данных банковской карты
    bot.send_message(user_id, "Введите номер банковской карты:")
    bot.register_next_step_handler(message, handle_card_number, account_link, steam_level, games, price, login, password)

def handle_card_number(message, account_link, steam_level, games, price, login, password):
    user_id = message.chat.id
    card_number = message.text

    # Вставляем данные аккаунта в таблицу "accounts" с учетом user_chat_id и номера карты
    insert_query = """
    INSERT INTO accounts (account_link, steam_level, games, price, login, password, card, user_chat_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING account_id
    """
    cursor.execute(insert_query, (account_link, steam_level, games, price, login, password, card_number, user_id))
    account_id = cursor.fetchone()[0]
    conn.commit()

    bot.send_message(user_id, f"Аккаунт успешно сохранен. Ваш ID аккаунта: {account_id}")


def check_account_exists(account_link):
    select_query = "SELECT * FROM accounts WHERE account_link = %s"
    cursor.execute(select_query, (account_link,))
    return cursor.fetchone() is not None


def create_main_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    sell_button = telebot.types.KeyboardButton("Продать")
    buy_button = telebot.types.KeyboardButton("Купить")
    keyboard.add(sell_button, buy_button)
    return keyboard


def handle_buy(message):
    user_id = message.chat.id

    # Вывод всех аккаунтов из базы данных
    select_query = "SELECT * FROM sale"
    cursor.execute(select_query)
    accounts = cursor.fetchall()

    if accounts:
        for account in accounts:
            account_info = f"ID: {account[0]}\nLink: {account[1]}\nLevel: {account[2]}\nGames: {account[3]}\nPrice: {account[4]} рублей\n\n"
            bot.send_message(user_id, account_info)

        # Запрашиваем у пользователя ID аккаунта, который он хочет купить
        bot.send_message(user_id, "Введите ID аккаунта, который вы хотите купить:")
        bot.register_next_step_handler(message, handle_choose_account)
    else:
        bot.send_message(user_id, "В базе данных нет доступных аккаунтов")

    # Добавим вариант "Вернуться в главное меню" после отображения аккаунтов
    bot.send_message(user_id, "Выберите действие:", reply_markup=create_main_keyboard())


def handle_choose_account(message):
    user_id = message.chat.id

    # Проверка, является ли введенный пользователем ID аккаунта допустимым целым числом
    try:
        chosen_account_id = int(message.text)
    except ValueError:
        bot.send_message(user_id, "Неверный формат ID аккаунта. Пожалуйста, введите число.")
        return

    # Получение информации об аккаунте по выбранному ID
    select_query = "SELECT * FROM sale WHERE account_id = %s"
    cursor.execute(select_query, (chosen_account_id,))
    account = cursor.fetchone()

    if account:
        account_info = f"ID: {account[0]}\nLink: {account[1]}\nLevel: {account[2]}\nGames: {account[3]}\nPrice: {account[4]} рублей\n\n"
        bot.send_message(user_id, account_info)

        # Запрашиваем у пользователя номер карты и код
        bot.send_message(user_id, "Введите номер карты:")
        bot.register_next_step_handler(message, handle_payment_info, chosen_account_id)
    else:
        bot.send_message(user_id, "Аккаунт с указанным ID не найден.")
        handle_buy(message)  # Повторно выводим список аккаунтов


def handle_payment_info(message, chosen_account_id):
    user_id = message.chat.id
    card_number = message.text

    # Проверка соответствия номера карты маске
    if not re.match(r'^\d{16}$', card_number):
        bot.send_message(user_id, "Номер карты введен неверно. Пожалуйста, введите 16 цифр.")
        bot.register_next_step_handler(message, handle_payment_info, chosen_account_id)
        return

    bot.send_message(user_id, "Введите код карты:")
    bot.register_next_step_handler(message, handle_card_code, chosen_account_id, card_number)


def handle_card_code(message, chosen_account_id, card_number):
    user_id = message.chat.id
    card_code = message.text

    # Проверка соответствия кода карты маске
    if not re.match(r'^\d{3}$', card_code):
        bot.send_message(user_id, "Код карты введен неверно. Пожалуйста, введите 3 цифры.")
        bot.register_next_step_handler(message, handle_card_code, chosen_account_id, card_number)
        return

    bot.send_message(user_id, "Введите код подтверждения оплаты от банка:")
    bot.register_next_step_handler(message, handle_bank_confirmation, chosen_account_id, card_number, card_code)


def handle_bank_confirmation(message, chosen_account_id, card_number, card_code):
    user_id = message.chat.id
    bank_confirmation_code = message.text

    # Проверка соответствия кода подтверждения маске
    if not re.match(r'^\d{4}$', bank_confirmation_code):
        bot.send_message(user_id, "Код подтверждения введен неверно. Пожалуйста, введите 4 цифры.")
        bot.register_next_step_handler(message, handle_bank_confirmation, chosen_account_id, card_number, card_code)
        return

    # Получение логина и пароля из таблицы sale
    select_account_query = "SELECT login, password FROM sale WHERE account_id = %s"
    cursor.execute(select_account_query, (chosen_account_id,))
    login, password = cursor.fetchone()

    # После успешной оплаты передаем логин и пароль
    bot.send_message(user_id, f"Оплата успешно подтверждена. Аккаунт куплен!\n"
                              f"Логин: {login}\n"
                              f"Пароль: {password}")

    # Удаление проданного аккаунта из таблицы sale
    remove_sold_account(chosen_account_id)


def remove_sold_account(account_id):
    delete_query = "DELETE FROM sale WHERE account_id = %s"
    cursor.execute(delete_query, (account_id,))
    conn.commit()

if __name__ == '__main__':
    try:
        bot.polling()
    finally:
        cursor.close()
        conn.close()
