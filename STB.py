from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
from config import host, user, password, db_name
import keyboard_stb as kb
import pymysql
import bcrypt

connection = pymysql.connect(
    host=host,
    port=3306,
    user=user,
    password=password,
    database=db_name,
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True)

TOKEN = config.TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

users = list()


class User:
    '''
    Класс, отвечающий всем параметрам пользователя
    '''

    def __init__(self, user_id):
        self.user_id = user_id
        self.messages_id = []
        self.forwardedMessages_id = []


def convertStrToArray(string):
    messages_id = [int(x) for x in (string[1:-1]).split(', ') ]
    print(messages_id)
    return messages_id


def convertArrayToStr(array):
    string = str(array)
    print(string)
    return string


with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        user = User(row['user_id'])
        if row['messages_id']:
            user.messages_id = convertStrToArray(row['messages_id'])
        users.append(user)


class CreateStorage(StatesGroup):
    '''
    Машина-состояние, которое отвечает за процесс создания хранилища
    '''
    setPassword = State()


class OpenStorage(StatesGroup):
    '''
    Машина-состояние, которое отвечает за процесс открытия хранилища
    '''
    getPassword = State()


class DeleteStorage(StatesGroup):
    '''
    Машина-состояние, которое отвечает за процесс удаления хранилища
    '''
    getPermission = State()


class StorageMode(StatesGroup):
    '''
    Машина-состояние, которое отвечает за режим хранилища
    '''
    modeStorage = State()


class ChangePassword(StatesGroup):
    '''
    Машина-состояние, которое отвечает за процесс смены и установки пароля
    '''
    getCurrentPassword = State()
    setNewPassword = State()


def getUser(id):
    '''
    Функция отвечает за проверку на наличие пользователя в массиве пользователей
    :param id: id Пользователя
    :return: class User/none
    '''
    for user in users:
        if user.user_id == id:
            return user
    return None


@dp.message_handler()
async def start(message: types.message):
    """
    Функция отвечает за обработку всех поступающих сообщений, не попавших под фильтр машины-состояния.
    :param message: сообщения пользоввателя
    :return: None
    """

    if str.lower(message.text) == '/start':
        if not checkUser(message.from_user.id):
            await bot.send_message(message.from_user.id, "Здравствуйте! Я буду охранять Вашу информацию. "
                                                         "Напишите 'инструкция' для помощи в использовании",
                                   reply_markup=kb.kb_add([kb.buttonInstruction, kb.buttonCreateStorage]))
        else:
            await bot.send_message(message.from_user.id, "Здравствуйте! Я буду охранять Вашу информацию. "
                                                 "Напишите 'инструкция' для помощи в использовании",
                                   reply_markup=kb.kb_add(
                                       [kb.buttonInstruction, kb.buttonOpenStorage, kb.buttonChangePassword,
                                        kb.buttonDeleteStorage]))
        return
    if str.lower(message.text) == 'инструкция':
        await bot.send_message(message.from_user.id, "Инструкцию по использованию можно посмотреть здесь: https://github.com/Tamer435/SecureStorageBot/blob/main/README.md")
        return
    if str.lower(message.text) == 'изменить пароль':
        if checkUser(message.from_user.id):
            await bot.send_message(message.from_user.id, "Введите действующий пароль",
                                   reply_markup=kb.kb_add([kb.buttonCancel]))
            await ChangePassword.getCurrentPassword.set()
        else:
            await bot.send_message(message.from_user.id, "У Вас ещё нет хранилища",
                                   reply_markup=kb.kb_add([kb.buttonInstruction, kb.buttonCreateStorage]))
        return
    if str.lower(message.text) == 'удалить хранилище':
        if checkUser(message.from_user.id):
            await bot.send_message(message.from_user.id, "Вы уверены? Данные будут полностью удалены, а пароль будет сброшен. Ответьте в формате 'дА'/отмена",
                                   reply_markup=kb.kb_add([kb.buttonCancel]))
            await DeleteStorage.getPermission.set()
        return
    if str.lower(message.text) == 'создать хранилище':
        if not checkUser(message.from_user.id):
            await CreateStorage.setPassword.set()
            await bot.send_message(message.from_user.id, "Введите пароль для хранилища",
                                   reply_markup=kb.kb_add([kb.buttonCancel]))
        else:
            await bot.send_message(message.from_user.id, "Хранилище уже создано", reply_markup=kb.kb_add(
                [kb.buttonInstruction, kb.buttonOpenStorage, kb.buttonChangePassword, kb.buttonDeleteStorage]))
        return
    if str.lower(message.text) == 'открыть хранилище':
        if checkUser(message.from_user.id):
            await bot.send_message(message.from_user.id, "Введите пароль", reply_markup=kb.kb_add([kb.buttonCancel]))
            await OpenStorage.getPassword.set()
        else:
            await bot.send_message(message.from_user.id, "У Вас ещё нет хранилища", reply_markup=kb.kb_add([kb.buttonInstruction, kb.buttonCreateStorage]))
        return
    if not checkUser(message.from_user.id):
        await bot.send_message(message.from_user.id, "Я Вас не понимаю ❌ \nПосмотрите инструкцию.",
                               reply_markup=kb.kb_add([kb.buttonInstruction, kb.buttonCreateStorage]))
    else:
        await bot.send_message(message.from_user.id, "Я Вас не понимаю ❌ \nПосмотрите инструкцию.",
                               reply_markup=kb.kb_add(
                                   [kb.buttonInstruction, kb.buttonOpenStorage, kb.buttonChangePassword,
                                    kb.buttonDeleteStorage]))


async def createStorage(user_id, message):
    '''
    Функция отвечает за создание хранилища и внесение пользователя в базу данных
    :param user_id: id пользователя
    :param message: сообщения
    :return: None
    '''
    salt = bcrypt.gensalt()
    hashedPassword = bcrypt.hashpw(message.encode('utf-8'), salt)

    with connection.cursor() as cursor:
        insert_query = "INSERT INTO users(user_id, password, salt) VALUES (%s, '%s', '%s')" % (user_id, hashedPassword.decode('utf-8'), salt.decode('utf-8'))
        cursor.execute(insert_query)
        connection.commit()
    cursor.close()
    user = User(user_id)
    users.append(user)


@dp.message_handler(state=CreateStorage.setPassword)
async def setPassword(message: types.message, state: CreateStorage=CreateStorage):
    '''
    Функция отвечает за установку пароля пользователя.
    :param message: сообщение пользователя типа types.message
    :param state: машина состояний типа CreateStorage
    :return: None
    '''
    if message.text != '' and len(message.text) >= 8 and str.lower(message.text) != message.text and str.upper(
            message.text) != message.text and ' ' not in message.text:
        await createStorage(message.from_user.id, message.text)
        await bot.delete_message(message.from_user.id, message.message_id)
        await state.finish()
        await bot.send_message(message.from_user.id, "Ваше хранилище было успешно создано ✅", reply_markup=kb.kb_add(
            [kb.buttonInstruction, kb.buttonOpenStorage, kb.buttonChangePassword, kb.buttonDeleteStorage]))
    elif str.lower(message.text) == 'отмена':
        await state.finish()
        await bot.send_message(message.from_user.id, "Создание хранилища было отменено ❌",
                               reply_markup=kb.kb_add([kb.buttonInstruction, kb.buttonCreateStorage]))
    else:
        await bot.send_message(message.from_user.id, "Ваш пароль составлен неверно ❌. Используйте больше 8 символов  "
                                                     "разных регистров, исключая пробелы")


@dp.message_handler(state=OpenStorage.getPassword)
async def getPassword(message: types.message, state: OpenStorage):
    '''
    Функция отвечает за проверку корректности пароляю
    :param message: Сообщение пользователя типа types.message
    :param state: Машина состояний типа OpenStorage
    :return: None
    '''
    if comparePasswords(message.text, message.from_user.id):
        await bot.send_message(message.from_user.id, "Хранилище открыто ✅",
                               reply_markup=kb.kb_add([kb.buttonCloseStorage, kb.buttonSendData]))
        await bot.delete_message(message.from_user.id, message.message_id)
        await state.finish()
        await StorageMode.modeStorage.set()
    elif str.lower(message.text) == "отмена":
        await bot.send_message(message.from_user.id, "Открытие отменено", reply_markup=kb.kb_add(
            [kb.buttonInstruction, kb.buttonOpenStorage, kb.buttonChangePassword, kb.buttonDeleteStorage]))
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, "Неверный пароль ❌")
        await bot.delete_message(message.from_user.id, message.message_id)


@dp.message_handler(state=StorageMode.modeStorage)
async def addMessages(message: types.message, state: StorageMode):
    '''
    Функция отвечает за добавление id сообщений в массив(хранилище сообщений)
    :param message: Сообщения пользовавтеля типа types.message
    :param state: Машина состояний типа StorageMode
    :return:
    '''
    if str.lower(message.text) == 'закрыть хранилище':
        await state.finish()
        await bot.send_message(message.from_user.id, "Хранилище закрыто. Очистите историю чата с ботом.",
                               reply_markup=kb.kb_add(
                                   [kb.buttonInstruction, kb.buttonOpenStorage, kb.buttonChangePassword,
                                    kb.buttonDeleteStorage]))
        updateData(message.from_user.id, 'messages_id', convertArrayToStr(getUser(message.from_user.id).messages_id))
        return
    elif str.lower(message.text) == 'получить данные':
        await bot.send_message(message.from_user.id, "Ответьте на сообщение, чтобы удалить его из хранилища")
        await sendData(message.from_user.id)
        return

    repliedMessage = message.reply_to_message
    if repliedMessage is not None:
        i = 0
        user = getUser(message.from_user.id)
        sentMessages_id = user.forwardedMessages_id
        for id in sentMessages_id:
            if repliedMessage.message_id == id:
                del user.messages_id[i]
                sentMessages_id.remove(id)
                await bot.delete_message(message.from_user.id, id)
                await bot.delete_message(message.from_user.id, message.message_id)
                return
            i += 1
    else:
        getUser(message.from_user.id).messages_id.append(message.message_id)


@dp.message_handler(state=StorageMode.modeStorage, content_types=["any"])
async def addFiles(message: types.message):
    '''
    Функция отвечает за добаввление id файлов в массив(хранилище сообщений)
    :param message: Сообщения пользователя типа types.message
    :return: None
    '''
    user = getUser(message.from_user.id)
    user.messages_id.append(message.message_id)


async def sendData(user_id):
    '''
    Функция отвечает за перессылку сообщений пользователя из хранилища в чат.
    :param user_id: id пользователя
    :return: Массив отправленных ботом сообщений
    '''
    sentMessages_id = getUser(user_id).forwardedMessages_id
    for sentMessage_id in sentMessages_id:
        await bot.delete_message(user_id, sentMessage_id)
    sentMessages_id.clear()
    for id in getUser(user_id).messages_id:
        message = await bot.forward_message(user_id, from_chat_id=user_id, message_id=id)
        sentMessages_id.append(message.message_id)
    return sentMessages_id


@dp.message_handler(state=ChangePassword.getCurrentPassword)
async def getCurrentPassword(message: types.message, state: ChangePassword):
    '''
    Функция отвечает за полученнее действующего пароля.
    :param message: Сообщения пользователя типа types.message
    :param state: Машина состояний типа ChangePassowrd
    :return: None
    '''
    if comparePasswords(message.text, message.from_user.id):
        await bot.send_message(message.from_user.id, "Введите новый пароль")
        await bot.delete_message(message.from_user.id, message.message_id)
        await ChangePassword.setNewPassword.set()
    elif str.lower(message.text) == 'отмена':
        await bot.send_message(message.from_user.id, "Смена пароля отменена", reply_markup=kb.kb_add(
            [kb.buttonInstruction, kb.buttonOpenStorage, kb.buttonChangePassword,
             kb.buttonDeleteStorage]))
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, "Неверный пароль ❌")
        await bot.delete_message(message.from_user.id, message.message_id)


@dp.message_handler(state=ChangePassword.setNewPassword)
async def changePassword(message: types.message, state: ChangePassword):
    '''
    Функция отвечает за изменение пароля пользовател.
    :param message: Сообщения пользователя типа types.message
    :param state: Машина состояний типа ChangePassword
    :return: None
    '''
    if message.text != '' and len(message.text) >= 8 and str.lower(message.text) != message.text and str.upper(
            message.text) != message.text and ' ' not in message.text:
        updateData(message.from_user.id, 'password', "%s" % str(bcrypt.hashpw(message.text.encode('utf-8'), str(getDataFromDB(message.from_user.id, 'salt')).encode('utf-8')).decode('utf-8')))
        await bot.delete_message(message.from_user.id, message.message_id)
        await state.finish()
        await bot.send_message(message.from_user.id, "Пароль был успешно сменен ✅", reply_markup=kb.kb_add(
            [kb.buttonInstruction, kb.buttonOpenStorage, kb.buttonChangePassword, kb.buttonDeleteStorage]))
    elif str.lower(message.text) == 'отмена':
        await bot.send_message(message.from_user.id, "Смена пароля отменена ❌", reply_markup=kb.kb_add(
            [kb.buttonInstruction, kb.buttonOpenStorage, kb.buttonChangePassword,
             kb.buttonDeleteStorage]))
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, "Ваш пароль составлен неверно. Используйте больше 8 символов  "
                                                     "разных регистров, исключая пробелы")


@dp.message_handler(state=DeleteStorage.getPermission)
async def deleteStorage(message: types.message, state: DeleteStorage):
    '''
    Функция отвечает за удаление пользователя из базы данных.
    :param message: Сообщения пользователя типа types.message
    :param state: Машина состояний типа DeleteStorage
    :return: None
    '''
    if message.text == "дА":
        deleteUser(message.from_user.id)
        await bot.send_message(message.from_user.id, "Хранилище удалено ✅", reply_markup=kb.kb_add(
            [kb.buttonInstruction, kb.buttonCreateStorage]))
        await state.finish()
    elif str.lower(message.text) == 'отмена':
        await bot.send_message(message.from_user.id, "Удаление отменено", reply_markup=kb.kb_add(
            [kb.buttonInstruction, kb.buttonOpenStorage, kb.buttonChangePassword,
             kb.buttonDeleteStorage]))
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, "Чтобы подтвердить удаление вручную напишите 'дА', если хотите отменить удаление нажмите кнопку 'отмена'")
        await bot.delete_message(message.from_user.id, message.message_id)


def getDataFromDB(user_id, dataType):
    '''
    Функция отвечает за полученние данных из базы данных.
    :param user_id: id пользователя
    :param dataType: Название столбца из таблицы.
    :return: Данные из таблицы
    '''
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE user_id=%s" % user_id)
        rows = cursor.fetchall()
        try:
            result = rows[0][dataType]
            return result
        except:
            return None


def deleteUser(user_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE user_id=%s" % user_id)
    users.remove(getUser(user_id))


def updateData(user_id, dataType, newData):
    '''
    Функция отвечает за обновление данных в таблице SQL
    :param user_id: id пользователя
    :param dataType: Тип данных обновляемых обьектов
    :param newData: Новые данные
    :return: None
    '''
    with connection.cursor() as cursor:
        cursor.execute("UPDATE users SET %s='%s' WHERE user_id=%s" % (dataType, newData, user_id))


def checkUser(user_id):
    '''
    Функция отвечает за проверку наличия пользователя в базе данных(Таблицы SQL)
    :param user_id: id пользователя
    :return: Bool
    '''
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE user_id=%s" % user_id)
        row = cursor.fetchall()
        if row:
            return True
        else:
            return False


def comparePasswords(message, user_id):
    '''
    Функция отвечает за совпадение хэшированного сообщения и пароля пользователя.
    :param message: Сообщение пользователя типа types.message
    :param user_id: id Пользователя
    :return: Bool
    '''
    if bcrypt.hashpw(message.encode('utf-8'), str(getDataFromDB(user_id, 'salt')).encode('utf-8')).decode('utf-8') == getDataFromDB(user_id, 'password'):
        return True
    return False


if __name__ == "__main__":
    executor.start_polling(dp)
