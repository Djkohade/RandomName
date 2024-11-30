import os
import random
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from datetime import datetime
import sys

# Константы для файлов
DirPath = os.path.dirname(os.path.realpath(__file__))

SETTINGS_FILE = DirPath + "/files/settings.json"
LIST_FILE = DirPath + "/files/list.txt"
VIEW_FILE = DirPath + "/files/view.txt"
DROP_FILE = DirPath + "/files/drop.txt"
LANGUAGE_DIR = DirPath + "/files/language/"

class RandomFilePickerApp:
    def __init__(self, master):
        self.master = master
        
        # Инициализация переменной для языка
        self.language_var = tk.StringVar(value="EN")  # Установите значение по умолчанию
        self.master.iconbitmap(DirPath+ "/files/icon.ico")
        # Инициализация файла настроек
        self.settings_file = SETTINGS_FILE

        # Проверка и создание необходимых файлов
        self.check_and_create_files()

        # Загружаем настройки при инициализации приложения
        self.load_settings()
        
        # Устанавливаем заголовок окна
        self.master.title(self.get_translation("app_title"))
        self.master.geometry("500x400")
        
        self.description_label = tk.Label(master, text=self.get_translation("select_folder_and_formats"), wraplength=500)
        self.description_label.pack(pady=10)

        self.configure_button = tk.Button(master, text=self.get_translation("configure_template"), command=self.show_configure)
        self.configure_button.pack(pady=10)

        self.randomize_button = tk.Button(master, text=self.get_translation("randomize"), command=self.pick_random_file)
        self.randomize_button.pack(pady=10)

        self.result_label = tk.Label(master, text="")
        self.result_label.pack(pady=10)

        self.path_label = tk.Label(master, text="", fg="blue")
        self.path_label.pack(pady=5)
        self.path_label.pack_forget()

        self.copy_button = tk.Button(master, text=self.get_translation("copy_name"), command=self.copy_to_clipboard)
        self.not_today_button = tk.Button(master, text=self.get_translation("not_today"), command=self.not_today)
        self.drop_button = tk.Button(master, text=self.get_translation("drop"), command=self.drop_file)

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=5)

        self.show_path_button = tk.Button(self.button_frame, text=self.get_translation("show_path"), command=self.toggle_path)
        self.show_path_button.pack(side=tk.LEFT)

        self.copy_button.pack(side=tk.LEFT)

        self.footer_frame = tk.Frame(master)
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.stats_button = tk.Button(self.footer_frame, text=self.get_translation("statistics"), command=self.show_statistics)
        self.stats_button.pack(side=tk.LEFT, anchor='w', padx=10)

        # Изменение кнопки смены языка
        self.language_combobox = ttk.Combobox(self.footer_frame, textvariable=self.language_var, width=10)  # Установите ширину
        self.language_combobox.pack(side=tk.LEFT, padx=10)

        self.copyright_label = tk.Label(self.footer_frame, text=" © Djkohade : 2024-" + str(datetime.now().year) + " - v 2.5.6", fg="gray")
        self.copyright_label.pack(side=tk.RIGHT, padx=10)

        self.hide_buttons()
        self.load_languages()

    def check_and_create_files(self):
        """Проверяет наличие необходимых файлов и создает их, если они отсутствуют."""
        if not os.path.exists(SETTINGS_FILE):
            default_settings = {
                "file_formats": "mkv,avi,ts,mpeg,mp4,3gp,mov,wmv,vob",  # Пример форматов
                "input_folder": "",
                "history": False,
                "selected_language": "EN",
                "randomize_count": 0,
                "last_randomize_time": ""
            }
            with open(SETTINGS_FILE, "w") as f:
                json.dump(default_settings, f)

        for filepath in [LIST_FILE, VIEW_FILE, DROP_FILE]:
            if not os.path.exists(filepath):
                open(filepath, 'w').close()  # Создаем пустой файл

    def load_languages(self):
        """Загружает доступные языки из папки files/language/."""
        languages = []
        if os.path.exists(LANGUAGE_DIR):
            for file in os.listdir(LANGUAGE_DIR):
                if file.endswith(".json"):
                    lang_name = os.path.splitext(file)[0]
                    languages.append(lang_name)
        self.language_combobox['values'] = languages
        self.language_combobox.set(self.settings.get("selected_language", "en"))
        self.language_combobox.bind("<<ComboboxSelected>>", self.on_language_change)

    def load_settings(self):
        """Загружает настройки из файла settings.json."""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                self.settings = json.load(f)
                self.file_formats = self.settings.get("file_formats", "")
                self.input_folder = self.settings.get("input_folder", "")
                self.history_var = tk.BooleanVar(value=self.settings.get("history", False))
                self.language_var.set(self.settings.get("selected_language", "en"))  # Установите язык из настроек
        else:
            self.settings = {}
            self.history_var = tk.BooleanVar(value=False)

    def save_settings(self):
        """Сохраняет настройки в файл settings.json."""
        self.settings["file_formats"] = self.file_formats
        self.settings["input_folder"] = self.input_folder
        self.settings["history"] = self.history_var.get()
        self.settings["selected_language"] = self.language_var.get()
        with open(self.settings_file, "w") as f:
            json.dump(self.settings, f)

    def get_translation(self, key):
        """Получает перевод для заданного ключа."""
        lang = self.language_var.get()
        lang_file = os.path.join(LANGUAGE_DIR, f"{lang}.json")
        if os.path.exists(lang_file):
            with open(lang_file, "r", encoding='utf-8') as f:
                translations = json.load(f)
                return translations.get(key, key)  # Возвращаем ключ, если перевод не найден
        return key  # Возвращаем ключ, если файл не найден

    def show_configure(self):
        """Отображает окно настроек."""
        self.configure_window = tk.Toplevel(self.master)
        self.configure_window.title(self.get_translation("configure_template"))

        self.configure_window.attributes("-topmost", True)
        self.configure_window.grab_set()
        self.configure_window.protocol("WM_DELETE_WINDOW", self.on_configure_close)

        tk.Label(self.configure_window, text=self.get_translation("input_folder")).pack(pady=5)
        self.folder_entry = tk.Entry(self.configure_window, width=50)
        self.folder_entry.insert(0, self.input_folder)
        self.folder_entry.pack(pady=5)

        tk.Button(self.configure_window, text=self.get_translation("select_folder"), command=self.select_folder).pack(pady=5)

        tk.Label(self.configure_window, text=self.get_translation("formats")).pack(pady=5)
        self.format_entry = tk.Entry(self.configure_window, width=50)
        self.format_entry.insert(0, self.file_formats)
        self.format_entry.pack(pady=5)

        self.history_checkbox = tk.Checkbutton(self.configure_window, text=self.get_translation("history_checkbox"), variable=self.history_var)
        self.history_checkbox.pack(pady=5)

        self.history_info_label = tk.Label(self.configure_window, text=self.get_translation("history_info"))
        self.history_info_label.pack(pady=5)

        tk.Button(self.configure_window, text=self.get_translation("save_template"), command=self.save_template).pack(pady=10)

        self.clear_history_button = tk.Button(self.configure_window, text=self.get_translation("clear_history"), command=self.show_clear_history_confirmation, fg="red")
        self.clear_history_button.pack(pady=5)

        self.clear_history_message = tk.Label(self.configure_window, text="", fg="green")
        self.clear_history_message.pack(pady=5)

        self.update_clear_history_button_visibility()

    def on_configure_close(self):
        """Обработчик закрытия окна настроек."""
        self.configure_window.destroy()

    def select_folder(self):
        """Открывает диалог выбора папки."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_path)

    def save_template(self):
        """Сохраняет настройки и создает список файлов."""
        self.input_folder = self.folder_entry.get()
        self.file_formats = self.format_entry.get()
        self.save_settings()
        self.create_file_list()
        self.result_label.config(text=self.get_translation("template_saved"))

        self.update_clear_history_button_visibility()
        self.configure_window.destroy()

    def create_file_list(self):
        """Создает список файлов в выбранной папке с указанными форматами, пропуская уже отсканированные."""
        formats = [fmt.strip() for fmt in self.file_formats.split(",")]
        file_list = []

        viewed_files = []
        if os.path.exists(VIEW_FILE):
            with open(VIEW_FILE, "r", encoding='utf-8') as view_file:
                viewed_files = view_file.read().splitlines()

        for root, dirs, files in os.walk(self.input_folder):
            for file in files:
                if any(file.endswith(fmt) for fmt in formats):
                    file_name = os.path.splitext(file)[0]
                    if file_name not in viewed_files:
                        file_list.append(file_name)

        file_list = list(set(file_list))

        try:
            with open(LIST_FILE, "w", encoding='utf-8') as f:
                f.write("\n".join(file_list))
        except Exception as e:
            print(f"Ошибка при записи в файл {LIST_FILE}: {e}")

    def pick_random_file(self):
        """Выбирает случайный файл из списка и удаляет его из list.txt."""
        files = []
        try:
            with open(LIST_FILE, "r", encoding='utf-8') as f:
                files = f.read().splitlines()
        except UnicodeDecodeError as e:
            print(f"Ошибка чтения файла {LIST_FILE}: {e}")

        if self.history_var.get():
            try:
                with open(VIEW_FILE, "r", encoding='utf-8') as view_file:
                    viewed_files = view_file.read().splitlines()
            except UnicodeDecodeError as e:
                print(f"Ошибка чтения файла {VIEW_FILE}: {e}")
                viewed_files = []

            try:
                with open(DROP_FILE, "r", encoding='utf-8') as drop_file:
                    dropped_files = drop_file.read().splitlines()
            except UnicodeDecodeError as e:
                print(f"Ошибка чтения файла {DROP_FILE}: {e}")
                dropped_files = []

            files = [f for f in files if f not in viewed_files and f not in dropped_files]

        if files:
            selected_file = random.choice(files)
            full_file_path = os.path.join(self.input_folder, selected_file + os.path.splitext(selected_file)[1])

            with open(VIEW_FILE, "a+", encoding='utf-8') as view_file:
                view_file.seek(0)
                if selected_file not in view_file.read().splitlines():
                    view_file.write(selected_file + "\n")

            files.remove(selected_file)

            with open(LIST_FILE, "w", encoding='utf-8') as f:
                f.write("\n".join(files))

            self.result_label.config(text=f"{self.get_translation('file')}: {selected_file}")
            self.path_label.config(text=full_file_path)
            self.update_randomize_count()

            self.show_buttons()
            self.show_path_button.pack(pady=5)
            self.path_label.pack_forget()
            self.show_path_button.config(text=self.get_translation("show_path"))
        else:
            self.result_label.config(text=self.get_translation("no_new_names"))
            self.hide_buttons()

    def toggle_path(self):
        """Переключает видимость пути к файлу."""
        if self.path_label.winfo_viewable():
            self.path_label.pack_forget()
            self.show_path_button.config(text=self.get_translation("show_path"))
        else:
            self.path_label.pack(pady=5)
            self.show_path_button.config(text=self.get_translation("hide_path"))

    def update_randomize_count(self):
        """Обновляет счетчик рандомизации и время последней рандомизации."""
        count = self.settings.get("randomize_count", 0) + 1
        self.settings["randomize_count"] = count
        self.settings["last_randomize_time"] = str(datetime.now())
        self.save_settings()

    def copy_to_clipboard(self):
        """Копирует название выбранного файла в буфер обмена."""
        self.master.clipboard_clear()
        self.master.clipboard_append(self.result_label.cget("text"))

    def not_today(self):
        """Добавляет последний выбранный файл обратно в список и удаляет его из view.txt."""
        try:
            # Читаем все выбранные файлы из view.txt
            with open(VIEW_FILE, "r", encoding='utf-8') as view_file:
                viewed_files = view_file.read().strip().splitlines()

            if viewed_files:
                # Получаем последний выбранный файл
                viewed_file = viewed_files[-1]  # Берем последний файл
                file_name = os.path.splitext(viewed_file)[0]  # Имя файла без расширения

                # Читаем существующие файлы из list.txt
                with open(LIST_FILE, "r", encoding='utf-8') as list_file:
                    existing_files = list_file.read().strip().splitlines()

                # Добавляем файл в list.txt, если его там нет
                if file_name not in existing_files:
                    with open(LIST_FILE, "a", encoding='utf-8') as list_file:
                        list_file.write(file_name + "\n")  # Добавляем имя файла в конец
                    self.result_label.config(text=f"{file_name} {self.get_translation('added_back')}")
                else:
                    self.result_label.config(text=f"{file_name} {self.get_translation('already_in_list')}")

                # Удаляем файл из view.txt
                viewed_files = [f for f in viewed_files if f != viewed_file]  # Удаляем последний файл
                with open(VIEW_FILE, "w", encoding='utf-8') as view_file:
                    view_file.write("\n".join(viewed_files) + "\n")  # Записываем обратно в файл

            else:
                self.result_label.config(text=self.get_translation("need_randomize"))

        except Exception as e:
            print(f"Произошла ошибка: {e}")

        self.hide_buttons()

    def drop_file(self):
        """Добавляет последний выбранный файл в файл drop.txt и очищает историю."""
        with open(VIEW_FILE, "r", encoding='utf-8') as view_file:
            viewed_file = view_file.read().strip()
        if viewed_file:
            with open(DROP_FILE, "r", encoding='utf-8') as drop_file:
                existing_dropped_files = drop_file.read().splitlines()

            if viewed_file not in existing_dropped_files:
                with open(DROP_FILE, "a", encoding='utf-8') as drop_file:
                    drop_file.write(viewed_file + "\n")

            with open(VIEW_FILE, "w", encoding='utf-8') as view_file:
                view_file.write("")

        self.hide_buttons()

    def show_clear_history_confirmation(self):
        """Показывает окно подтверждения для очистки истории."""
        self.confirmation_window = tk.Toplevel(self.configure_window)
        self.confirmation_window.title(self.get_translation("confirmation"))
        self.confirmation_window.attributes("-topmost", True)

        tk.Label(self.confirmation_window, text=self.get_translation("confirm_clear_history")).pack(pady=10)

        tk.Button(self.confirmation_window, text=self.get_translation("yes"), command=self.clear_history).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Button(self.confirmation_window, text=self.get_translation("no"), command=self.confirmation_window.destroy).pack(side=tk.RIGHT, padx=20, pady=10)

    def clear_history(self):
        """Очищает историю, удаляя файлы view.txt и drop.txt."""
        open(VIEW_FILE, "w").close()
        open(DROP_FILE, "w").close()
        self.clear_history_message.config(text=self.get_translation("history_cleared"))
        self.update_clear_history_button_visibility()
        self.confirmation_window.destroy()

    def update_clear_history_button_visibility(self):
        """Обновляет видимость кнопки очистки истории в зависимости от содержимого файлов."""
        if os.path.exists(VIEW_FILE) and os.path.exists(DROP_FILE):
            view_empty = os.stat(VIEW_FILE).st_size == 0
            drop_empty = os.stat(DROP_FILE).st_size == 0
            if view_empty and drop_empty:
                self.clear_history_button.pack_forget()
            else:
                self.clear_history_button.pack(pady=5)

    def hide_buttons(self):
        """Скрывает кнопки копирования, не сегодня и дропа."""
        self.copy_button.pack_forget()
        self.not_today_button.pack_forget()
        self.drop_button.pack_forget()
        self.show_path_button.pack_forget()

    def show_buttons(self):
        """Показывает кнопки копирования, не сегодня и дропа."""
        self.copy_button.pack(pady=5)
        self.not_today_button.pack(pady=5)
        self.drop_button.pack(pady=5)

    def show_statistics(self):
        """Отображает окно со статистикой использования приложения."""
        stats_window = tk.Toplevel(self.master)
        stats_window.title(self.get_translation("statistics"))
        stats_window.geometry("300x200")

        randomize_count = self.settings.get("randomize_count", 0)
        with open(VIEW_FILE, "r", encoding='utf-8') as view_file:
            viewed_count = len(view_file.readlines())
        with open(DROP_FILE, "r", encoding='utf-8') as drop_file:
            dropped_count = len(drop_file.readlines())

        tk.Label(stats_window, text=self.get_translation("randomized_count").format(randomize_count)).pack(pady=5)
        tk.Label(stats_window, text=self.get_translation("viewed_count").format(viewed_count)).pack(pady=5)
        tk.Label(stats_window, text=self.get_translation("dropped_count").format(dropped_count)).pack(pady=5)

        tk.Button(stats_window, text=self.get_translation("close"), command=stats_window.destroy).pack(pady=10)

    def on_language_change(self, event):
        """Обработчик изменения языка."""
        self.save_settings()
        
        # Перезапускаем приложение
        os.execv(sys.executable, ['python'] + sys.argv)

    def update_translations(self):
        """Обновляет все тексты в интерфейсе согласно выбранному языку."""
        self.description_label.config(text=self.get_translation("select_folder_and_formats"))
        self.configure_button.config(text=self.get_translation("configure_template"))
        self.randomize_button.config(text=self.get_translation("randomize"))
        self.copy_button.config(text=self.get_translation("copy_name"))
        self.not_today_button.config(text=self.get_translation("not_today"))
        self.drop_button.config(text=self.get_translation("drop"))
        self.stats_button.config(text=self.get_translation("statistics"))
        self.copyright_label.config(text=" © Djkohade : 2024-" + str(datetime.now().year) + " - v 2.5.6")

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomFilePickerApp(root)
    root.mainloop()
