import customtkinter # модуль
from tkinter import *
from tkinter import ttk #таблиці та їх стилізація
from datetime import datetime
import sqlite3 #бібліотека для роботи з базою даних

customtkinter.set_appearance_mode("light") #тема застосунку світла 
customtkinter.set_default_color_theme("green") #колір віджетів зелений 


def db_start():
    global conn, cur
    conn = sqlite3.connect('tasks_db.db') #підключаємось до бази даних
    cur = conn.cursor() 
    cur.execute('''CREATE TABLE IF NOT EXISTS notes_table (completed bool, task text, date text)''') #створення таблиці


def loading_data(): #Відбувається SQL запит на отримання даних з таблиці notes_table
    cur.execute("SELECT * FROM notes_table")
    rows = cur.fetchall()

    for row in rows:
        if row[0] == 'True':
            tree.insert('', 'end', values=(row[1], row[2], '✖'), tags='checked')
        else:
            tree.insert('', 'end', values=(row[1], row[2], '✖'), tags='unchecked')


def processing_events(e):
    try:
        selected_item = tree.selection()[0] #зберігаємо id обраної комірки
        values = tree.item(selected_item, option="values") #збергіаємо дані з обраної строки

        if tree.identify_column(e.x) == '#0': #якшо у строці було натистуна перша комірка 
            rowid = tree.identify_row(e.y) #то її id буде зберігатись у rowid 
            tag = tree.item(rowid, 'tags')[0]

            if tag == 'checked': #з отриманого тега ми будемо змінювати його на протилежний
                tree.item(rowid, tags='unchecked')
                cur.execute('''UPDATE notes_table SET completed = ? WHERE task = ?''', ('False', values[0], )) #якшо стояла галочка то вона буде змінена на пустий квадрат
                conn.commit()
            else:
                tree.item(rowid, tags='checked')
                cur.execute('''UPDATE notes_table SET completed = ? WHERE task = ?''', ('True', values[0],))
                conn.commit()
        elif tree.identify_column(e.x) == '#3': #буде спрацьовувати у випадку вибору 3 комірки котра яка призначеня для видалення задач
            tree.delete(selected_item)
            cur.execute('''DELETE FROM notes_table WHERE task = ?''', (values[0], )) #буде видалятись задача, те саме буде відбуватись у базі даних
            conn.commit()
        else:
            pass
    except IndexError:
        pass


def add(task): 
    tree.insert('', 'end', values=(task, f'{datetime.now():%d-%m-%y %H:%M:%S}', '✖'), tags='unchecked')                   #завдяки методу insert будуть додаватись дані у нашу таблицю
    cur.execute("INSERT INTO notes_table VALUES ('%s','%s','%s')" % (False, task, f'{datetime.now():%d-%m-%y %H:%M:%S}')) #дані додаються у базу
    conn.commit()


def add_task():
    window = customtkinter.CTkToplevel(root) #дочірнє вікно
    window.title('Додати задачу') #заголовок якого Додати задачу
    window.wm_attributes('-topmost', True) #дочірнє вікно буде знаходитись поверх іншинх вікон
    window.geometry('300x80') #розмір вінка

    task_text = customtkinter.CTkEntry(window, width=250) #текстове поле і її ширина
    task_text.pack(pady=5) #додаємо відступ по y котрий дорівняє п'яти

    customtkinter.CTkButton(window, text='Додати', #додаємо кнопку до дочірнього вікна Додати
                            font=customtkinter.CTkFont(family='Times New Roman', size=20, weight='bold'), #характеристики кнопки Додати
                            command=lambda: add(task_text.get())).pack() #анонімна функція щоб передати значення з текстового поля task_text

    window.mainloop()


root = customtkinter.CTk() #екземляр класу
root.title("Task Manager") #заголовок застосунку 
root.geometry('810x305') #розмір вікна
root.resizable(0, 0) #забороняємо зміни розміру вікна 

style = ttk.Style() #додавання стилів
style.theme_use('default') #використовуються стандартні теми

style.configure('Treeview',
                background='#F6B571', #колір фону
                foreground='white', #колір тексту
                rowheight=25, #висота строки
                fieldbackground='#F5DD9C', #колір фону полів
                bordercolor='#6d9975', #колір
                borderwidth=0) #ширина границь
style.map('Treeview', background=[('selected', '#BED476')]) #колір обраної комірки

style.configure('Treeview.Heading', #стилі заголовків таблиці
                background='#BED476', #колір фону
                foreground='white', #колір тексту
                relief='flat') #рельєф
style.map('Treeview.Heading', #стилі обраного заголовку
          background=[('active', '#3484F0')]) #колір і працює коли наводиш на нього

#змінні у котрих зберігаються галочки
#перше галочка
#друге пустий квадрат
im_checked = PhotoImage('checked', data=b'GIF89a\x0e\x00\x0e\x00\xf0\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x0e\x00\x0e\x00\x00\x02#\x04\x82\xa9v\xc8\xef\xdc\x83k\x9ap\xe5\xc4\x99S\x96l^\x83qZ\xd7\x8d$\xa8\xae\x99\x15Zl#\xd3\xa9"\x15\x00;')
im_unchecked = PhotoImage('unchecked', data=b'GIF89a\x0e\x00\x0e\x00\xf0\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x0e\x00\x0e\x00\x00\x02\x1e\x04\x82\xa9v\xc1\xdf"|i\xc2j\x19\xce\x06q\xed|\xd2\xe7\x89%yZ^J\x85\x8d\xb2\x00\x05\x00;')

tree = ttk.Treeview(root) #таблиця
tree.tag_configure('checked', image=im_checked) #тег галочки
tree.tag_configure('unchecked', image=im_unchecked) #тег пустого квадрату
tree['columns'] = ('column1', 'column2', 'column3', 'column4') #столбці
#заголовки стовбці та їх розміри
tree.heading('#0', text='Статус') 
tree.column("#0", width=50)
tree.heading('#1', text='Задача')
tree.column("#1", width=600)
tree.heading('#2', text='Дата')
tree.column("#2", width=100)
tree.heading('#3', text='Видалити')
tree.column("#3", width=60, anchor=CENTER) #у стовбці знаходиться хрестик для видалення задачі

tree.pack()

btn_add_task = customtkinter.CTkButton(root, text='Додати задачу', #кнопка Додати задачу
                                       font=customtkinter.CTkFont(family='Times New Roman', size=25, weight='bold'), #характеристики кнопки
                                       command=add_task) 
btn_add_task.pack(anchor=S, side=BOTTOM, pady=5) #відображаємо кнопку по центру знизу вікна

db_start()
loading_data()
tree.bind('<Button-1>', processing_events) #бінд на ліву кнопку мищі

root.mainloop()
conn.close() #закриття з'єднання з базою даних

                        