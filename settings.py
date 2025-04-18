import json
import os

class SettingsManager:
    def __init__(self):
        self.settings_file = "settings.json"
        self.default_settings = {
            "theme": "Светлая",
            "default_scale": 1.0,
            "font_size": 10
        }
        self.settings = self.load_settings()

    def load_settings(self):
        # Загрузка настроек из файла
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return self.default_settings.copy()
        return self.default_settings.copy()

    def get_setting(self, key, default=None):
        # Получение значения настройки
        return self.settings.get(key, default if default is not None else self.default_settings.get(key))

    def set_setting(self, key, value):
        # Установка значения настройки
        self.settings[key] = value

    def save_settings(self):
        # Сохранение настроек в файл
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)