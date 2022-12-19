from unittest import TestCase, main
from unittest.mock import MagicMock

import STB
from aiogram import types


def test(num):
    if num == 1:
        return True
    return False


class Test_Bot_STB(TestCase):
    def testGetUserP(self):
        # Неправильный id пользователя
        user_id = -10394
        expected_result = None
        result = STB.getUser(user_id)
        self.assertEqual(result, expected_result)

    def testGetUserN(self):
        user_id = 134920
        STB.users.append(STB.User(user_id))
        expected_result = STB.User(user_id)
        result = STB.getUser(user_id)
        self.assertEqual(result.user_id, expected_result.user_id)

    def testGetDataFromDBN(self):
        # Неправильный id пользователя
        user_id = -10394
        expected_result = None
        result = STB.getDataFromDB(user_id, 'password')
        self.assertEqual(result, expected_result)

    def testCheckUserN(self):
        # Неправильный id пользователя
        user_id = -10394
        expected_result = False
        result = STB.checkUser(user_id)
        self.assertEqual(result, expected_result)

    async def testSendData(self):
        user_id = 134920
        user = STB.User(user_id)
        user.forwardedMessages_id = [4290, 4291, 4292]
        STB.users.append(user)
        expected_result = user.forwardedMessages_id
        result = await STB.sendData(user_id)
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    main()
