import shutil
import os
import datetime

def copy_support_file():
    # Путь к исходному файлу
    source_file = "db/support"

    # Проверяем существование исходного файла
    if os.path.exists(source_file):
        # Генерируем имя для нового файла с помощью текущей даты и времени
        current_datetime = datetime.datetime.now()
        backup_filename = "backup_{:%Y-%m-%d_%H-%M-%S}".format(current_datetime)

        # Путь к папке, в которую нужно скопировать файл
        destination_folder = "db/backup"  # Замените на путь к вашей целевой папке

        # Проверяем существование целевой папки, если она не существует, создаем ее
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # Создаем полный путь для нового файла
        backup_file_path = os.path.join(destination_folder, backup_filename)

        # Копируем файл в указанную папку с новым именем
        shutil.copy(source_file, backup_file_path)
        print("Файл успешно скопирован. Новый путь файла:", backup_file_path)
    else:
        print("Исходный файл не найден.")

if __name__ == "__main__":
    copy_support_file()