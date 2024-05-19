from abc import ABC, abstractmethod
import json


class Saver(ABC):
    """Abstract class for saving data."""
    @abstractmethod
    def save(self):
        raise NotImplementedError


class JsonSaver(Saver):
    """Class for saving to json file."""
    def save(self, filename: str, data: list[dict]):
        """Save passed data to filename.json."""
        with open(f'{filename}.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
