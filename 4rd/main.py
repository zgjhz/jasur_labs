import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

# Загрузка данных и вычисление рейтингов
class BookDataProcessor:
    @staticmethod
    def load_books(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    @staticmethod
    def calculate_rating(book, preferences):
        score = 0
        if book['genre'].lower() in preferences['genres']:
            score += 3
        if book['author'][0].lower() in preferences['authors']:
            score += 2

        for keyword in preferences['keywords']:
            if keyword in book['description'].lower():
                score += 1

        if int(book.get('first_publish_year', 0)) >= preferences.get('min_year', 0):
            score += 1

        return score

    @staticmethod
    def recommend_books(books, preferences):
        rated_books = [
            {**book, "rating": BookDataProcessor.calculate_rating(book, preferences)}
            for book in books
        ]
        return sorted(rated_books, key=lambda b: b["rating"], reverse=True)

# Приложение для рекомендаций книг
class BookRecommenderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Рекомендации книг")
        self.geometry("700x600")

        self.books = BookDataProcessor.load_books(r"4rd/books.json")
        self.to_read_list = []

        self._setup_ui()

    def _setup_ui(self):
        # Верхняя панель ввода
        self.pref_frame = ttk.LabelFrame(self, text="Ваши предпочтения")
        self.pref_frame.pack(fill="x", padx=10, pady=10)

        self._create_preference_inputs()

        # Панель кнопок
        self.action_frame = ttk.Frame(self)
        self.action_frame.pack(fill="x", padx=10, pady=5)

        self._create_action_buttons()

        # Таблица рекомендаций
        self.recommendation_frame = ttk.LabelFrame(self, text="Рекомендации")
        self.recommendation_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self._create_recommendation_table()

        # Таблица "Прочитать"
        self.to_read_frame = ttk.LabelFrame(self, text="Список для чтения")
        self.to_read_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self._create_to_read_table()

    def _create_preference_inputs(self):
        inputs = ["Жанры", "Авторы", "Ключевые слова", "Минимальный год"]
        self.entries = {}

        for i, label in enumerate(inputs):
            ttk.Label(self.pref_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(self.pref_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label] = entry

    def _create_action_buttons(self):
        ttk.Button(self.action_frame, text="Получить рекомендации", command=self.display_recommendations).pack(side="left", padx=5)
        ttk.Button(self.action_frame, text="Сохранить рекомендации", command=self.save_recommendations).pack(side="left", padx=5)
        ttk.Button(self.action_frame, text="Добавить в список для чтения", command=self.add_to_to_read_list).pack(side="right", padx=5)

    def _create_recommendation_table(self):
        self.recommendation_tree = ttk.Treeview(self.recommendation_frame, columns=("Title", "Author", "Genre", "Year", "Rating"), show="headings")

        headings = ["Название", "Автор", "Жанр", "Год", "Рейтинг"]
        for col, heading in zip(self.recommendation_tree["columns"], headings):
            self.recommendation_tree.heading(col, text=heading)

        self.recommendation_tree.pack(fill="both", expand=True, padx=5, pady=5)

    def _create_to_read_table(self):
        self.to_read_tree = ttk.Treeview(self.to_read_frame, columns=("Title", "Author", "Genre"), show="headings")

        headings = ["Название", "Автор", "Жанр"]
        for col, heading in zip(self.to_read_tree["columns"], headings):
            self.to_read_tree.heading(col, text=heading)

        self.to_read_tree.pack(fill="both", expand=True, padx=5, pady=5)

    def display_recommendations(self):
        preferences = {
            "genres": [g.strip().lower() for g in self.entries["Жанры"].get().split(',') if g.strip()],
            "authors": [a.strip().lower() for a in self.entries["Авторы"].get().split(',') if a.strip()],
            "keywords": [k.strip().lower() for k in self.entries["Ключевые слова"].get().split(',') if k.strip()],
            "min_year": int(self.entries["Минимальный год"].get() or 0)
        }

        recommendations = BookDataProcessor.recommend_books(self.books, preferences)

        for row in self.recommendation_tree.get_children():
            self.recommendation_tree.delete(row)

        for book in recommendations:
            self.recommendation_tree.insert("", "end", values=(book["title"], book["author"], book["genre"], book["first_publish_year"], book["rating"]))

        if not recommendations:
            messagebox.showinfo("Результаты", "Подходящие книги не найдены.")

    def add_to_to_read_list(self):
        selected = self.recommendation_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите книгу из списка рекомендаций.")
            return

        for item in selected:
            book = self.recommendation_tree.item(item)["values"]
            entry = {"title": book[0], "author": book[1], "genre": book[2]}
            if entry not in self.to_read_list:
                self.to_read_list.append(entry)

        self._update_to_read_table()

    def _update_to_read_table(self):
        for row in self.to_read_tree.get_children():
            self.to_read_tree.delete(row)

        for book in self.to_read_list:
            self.to_read_tree.insert("", "end", values=(book["title"], book["author"], book["genre"]))

    def save_recommendations(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )

        if not file_path:
            return

        recommendations = [
            self.recommendation_tree.item(row)["values"]
            for row in self.recommendation_tree.get_children()
        ]
        data = [
            {"title": r[0], "author": r[1], "genre": r[2], "first_publish_year": r[3], "rating": r[4]}
            for r in recommendations
        ]

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        messagebox.showinfo("Сохранение", f"Рекомендации успешно сохранены в файл {file_path}.")

if __name__ == "__main__":
    app = BookRecommenderApp()
    app.mainloop()
