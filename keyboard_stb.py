from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


buttonInstruction = KeyboardButton("Инструкция")
buttonOpenStorage = KeyboardButton("Открыть хранилище")
buttonCloseStorage = KeyboardButton("Закрыть хранилище")
buttonChangePassword = KeyboardButton("Изменить пароль")
buttonCleanStorage = KeyboardButton("Очистить хранилище")
buttonCreateStorage = KeyboardButton("Создать хранилище")
buttonSendData = KeyboardButton("Получить данные")
buttonCancel = KeyboardButton("Отмена")

current_kb = ReplyKeyboardMarkup()


def kb_add(buttons):
    '''
    Функция отвечает за добавление кнопок в клавиатуру
    :param buttons: Массив кнопок
    :return: Клавиатуру типа ReplyKeyboardMarkup
    '''
    global current_kb
    kb_user = ReplyKeyboardMarkup(resize_keyboard=True)
    for button in buttons:
        kb_user.add(button)
    current_kb = kb_user
    return kb_user
