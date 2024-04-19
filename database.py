# import requests
import sqlite3


# class Login:
# def __init__(self, url):
# self.url = url
# self.data = {}
#
# def get_request(self):
# response = requests.get(f"{self.url}")
# data = response.json()['items']
# return data
#
# @staticmethod
# def get_list_all_users_with_scores(data):
# users = []
# for i in range(len(data)):
# users.append("Username: " +
#  data[i]["Name"] + "; Score: " + str(data[i]["Score"]))
# return users
#
# def add_new_user(self, username: str, score: int):
# new_city = {"Name": username,
# "Score": score}
# response = requests.post(url=self.url, json=new_city)
# print(response.json())
#
# def main(self):
# self.data = self.get_request()
# return self.get_list_all_users_with_scores(data=self.data)
#
#
# if __name__ == '__main__':
# Login_class = Login(
# "http://127.0.0.1:8090/api/collections/Leaderboard/records")
# Login_class.main()

class Login:
    def __init__(self):
        # Подключаемся к базе данных
        self.conn = sqlite3.connect('mydatabase.db')
        self.cursor = self.conn.cursor()
        # Создаем таблицу, если она еще не существует
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT,
                score INTEGER
            )
        ''')
        self.conn.commit()

    def add_update(self, username, score):
        self.cursor.execute(
            'SELECT * FROM users WHERE username = ?', (username,))
        ex_user = self.cursor.fetchone()
        if ex_user is None:
            self.cursor.execute(
                'INSERT INTO users (username, score) VALUES (?, ?)', (username, score))
        else:
            stored_score = ex_user[1]
            if score > stored_score:
                self.cursor.execute(
                    'UPDATE users SET score = ? WHERE username = ?', (score, username))
        print(username, score)
        # Сохраняем изменения
        self.conn.commit()

    def get_users(self):
        # Выводим таблицу в консоль
        self.cursor.execute('SELECT * FROM users')
        print(self.cursor.fetchall())
        return self.cursor.fetchall()
