import sqlite3 as sqlite

class BotDB:
    def __init__(self, db_file) -> None:
        self.db = sqlite.connect(db_file)
        self.cursor = self.db.cursor()
        try:
            self.db.execute(
                """
                CREATE TABLE IF NOT EXISTS anime_series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                series_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                dub_type TEXT NOT NULL DEFAULT 'Стандартная',
                duration INTEGER,
                UNIQUE(file_path)  -- Уникальность по пути к файлу
                );
                """
            )
        except sqlite.Error as e:
            print(f"Error: {e}")

    def series_exists(self, file_path):
        cursor = self.db.execute(
            "SELECT * FROM anime_series where file_path='{file_path}'".format(file_path=file_path)
        )
        return bool(cursor.fetchall())

    def add_series(self, file_name, file_path, series_number, title, dub_type, duration):
        try:
            if not self.series_exists(file_path):
                self.db.execute(
                    """
                    INSERT INTO anime_series VALUES ('{file_name}','{file_path}', '{series_number}', '{title}', '{dub_type}' 'duration')""".format(
                        file_name = file_name, file_path = file_path, series_number = series_number, title = title, dub_type = dub_type, duration = duration
                    )
                )
                self.db.commit()
            else:
                print("User exists!")
        except sqlite.Error as e:
            print(f"Error: {e}")

