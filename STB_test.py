from unittest import TestCase, main
from unittest.mock import MagicMock
import STB


def test(num):
    if num == 1:
        return True
    return False


class Test_Bot_STB(TestCase):
    def testGetUserN(self):
        # Некорректный id пользователя
        user_id = -10394
        expected_result = None
        result = STB.getUser(user_id)
        self.assertEqual(result, expected_result)

    def testGetUserP(self):
        # Корректный id пользователя
        user_id = 134920
        STB.users.append(STB.User(user_id))
        expected_result = STB.User(user_id)
        result = STB.getUser(user_id)
        self.assertEqual(result.user_id, expected_result.user_id)

    def testConvertStrToArrayN(self):
        # Строка неправильного вида
        string = "1a2b3c"
        expected_result = None
        result = STB.convertStrToArray(string)
        self.assertEqual(result, expected_result)

    def testConvertStrToArrayP(self):
        # Строка правильного вида
        string = "[1, 2, 3]"
        expected_result = [1, 2, 3]
        result = STB.convertStrToArray(string)
        self.assertEqual(result, expected_result)

    def testDeleteUserN(self):
        # Некорректный id пользователя
        user_id = -10394
        expected_result = False
        result = STB.deleteUser(user_id)
        self.assertEqual(result, expected_result)

    async def testDeleteUserP(self):
        # Корректный id пользователя
        user_id = 134920
        password = "Password"
        expected_result = True
        await STB.createStorage(user_id, password)
        result = STB.deleteUser(user_id)
        self.assertEqual(result, expected_result)

    def testCheckUserN(self):
        # Некорректный id пользователя
        user_id = -10394
        expected_result = False
        result = STB.checkUser(user_id)
        self.assertEqual(result, expected_result)

    async def testCheckUserP(self):
        # Корректный id пользователя
        user_id = 134920
        password = "Password"
        expected_result = True
        await STB.createStorage(user_id, password)
        result = STB.checkUser(user_id)
        self.assertEqual(result, expected_result)

    def testGetDataFromDBN(self):
        # Некорректный id пользователя
        user_id = -10394
        expected_result = None
        result = STB.getDataFromDB(user_id, 'password')
        self.assertEqual(result, expected_result)

    async def testGetDataFromDBP(self):
        user_id = 134920
        password = "Password"
        expected_result = '[1, 2, 3]'
        await STB.createStorage(user_id, password)
        STB.updateData(user_id, 'messages_id', expected_result)
        result = STB.getDataFromDB(user_id, 'messages_id')
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    main()
