# подключаем библиотеку для работы с базой данных
import sqlite3
# подключаем графическую библиотеку для создания интерфейсов
from tkinter import *
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

# подключаем графическую библиотеку
window = Tk()
# заголовок окна
window.title("Бюджет 0.1")

# создаём надписи для полей ввода и размещаем их по сетке
l1 = Label(window, text="Название")
l1.grid(row=0, column=0)

l2 = Label(window, text="Стоимость")
l2.grid(row=0, column=2)

l3 = Label(window, text="Комментарий")
l3.grid(row=1, column=0)

# создаём поле ввода названия покупки, говорим, что это будут строковые переменные и размещаем их тоже по сетке
product_text = StringVar()
e1 = Entry(window, textvariable=product_text)
e1.grid(row=0, column=1)

# то же самое для комментариев и цен
price_text = StringVar()
e2 = Entry(window, textvariable=price_text)
e2.grid(row=0, column=3)

comment_text = StringVar()
e3 = Entry(window, textvariable=comment_text)
e3.grid(row=1, column=1)

# создаём список, где появятся наши покупки, и сразу определяем его размеры в окне
list1 = Listbox(window, height=25, width=65)
list1.grid(row=2, column=0, rowspan=6, columnspan=2)

# на всякий случай добавим сбоку скролл, чтобы можно было быстро прокручивать длинные списки
sb1 = Scrollbar(window)
sb1.grid(row=2, column=2, rowspan=6)

# привязываем скролл к списку
list1.configure(yscrollcommand=sb1.set)
sb1.configure(command=list1.yview)

# создаём кнопки действий и привязываем их к своим функциям
# кнопки размещаем тоже по сетке
b1 = Button(window, text="Посмотреть все", width=12, command=print('view_command'))
b1.grid(row=2, column=3) #size of the button

b2 = Button(window, text="Поиск", width=12, command=print('search_command'))
b2.grid(row=3, column=3)

b3 = Button(window, text="Добавить", width=12, command=print('add_command'))
b3.grid(row=4, column=3)

b4 = Button(window, text="Обновить", width=12, command=print('update_command'))
b4.grid(row=5, column=3)

b5 = Button(window, text="Удалить", width=12, command=print('delete_command'))
b5.grid(row=6, column=3)

b6 = Button(window, text="Закрыть", width=12, command=print('on_closing'))
b6.grid(row=7, column=3)

# пусть окно работает всё время до закрытия
window.mainloop()
