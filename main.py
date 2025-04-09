# подключаем библиотеку для работы с базой данных
import sqlite3    
# создаём класс для работы с базой данных
class DB:                        
    # конструктор класса
    def __init__(self):           
        # соединяемся с файлом базы данных
        self.conn = sqlite3.connect("mybooks.db")  
        # создаём курсор для виртуального управления базой данных
        self.cur = self.conn.cursor()    
        # если нужной нам таблицы в базе нет — создаём её
        self.cur.execute(             
            "CREATE TABLE IF NOT EXISTS buy (id INTEGER PRIMARY KEY, product TEXT, price TEXT, comment TEXT)") 
        # сохраняем сделанные изменения в базе
        self.conn.commit()  

    # деструктор класса
    def __del__(self):        
        # отключаемся от базы при завершении работы
        self.conn.close()   
   
    # просмотр всех записей
    def view(self):        
        # выбираем все записи о покупках
        self.cur.execute("SELECT * FROM buy") 
        # собираем все найденные записи в колонку со строками
        rows = self.cur.fetchall()  
        # возвращаем сроки с записями расходов
        return rows

    # добавляем новую запись
    def insert(self, product, price, comment):  
        # формируем запрос с добавлением новой записи в БД
        self.cur.execute("INSERT INTO buy VALUES (NULL,?,?,?)", (product, price, comment,)) 
        # сохраняем изменения
        self.conn.commit()
        

    # обновляем информацию о покупке
    def update(self, id, product, price):   
        # формируем запрос на обновление записи в БД
        self.cur.execute("UPDATE buy SET product=?, price=? WHERE id=?", (product, price, id,))
        # сохраняем изменения 
        self.conn.commit()

    # удаляем запись
    def delete(self, id):                   
        # формируем запрос на удаление выделенной записи по внутреннему порядковому номеру
        self.cur.execute("DELETE FROM buy WHERE id=?", (id,))
        # сохраняем изменения
        self.conn.commit()

    # ищем запись по названию покупки
    def search(self, product="", price=""):  
        # формируем запрос на поиск по точному совпадению
        self.cur.execute("SELECT * FROM buy WHERE product=?", (product,))
        # формируем полученные строки и возвращаем их как ответ
        rows = self.cur.fetchall()
        return rows

# создаём экземпляр базы данных на основе класса
db = DB()
