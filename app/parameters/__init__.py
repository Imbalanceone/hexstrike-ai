import shutil
import sys
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel
from pydantic_yaml import parse_yaml_raw_as, to_yaml_str

from app.schemas.parameters import Parameters, SecretParameters

if Path("/tmps").exists():
    ROOT_DATA_DIR = Path("/tmps")
elif getattr(sys, "frozen", False):
    ROOT_DATA_DIR = Path(sys.executable).resolve().parent
else:
    ROOT_DATA_DIR = Path(__file__).resolve().parent.parent.parent

CONFIGS_DIR = ROOT_DATA_DIR / "configs"

if not CONFIGS_DIR.exists():
    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
    # Если запускаемся из бинарника — копируем дефолтные файлы
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        if Path("/tmps").exists():
            builtin_configs = Path(sys._MEIPASS) / "tmps" / "configs"
        else:
            builtin_configs = Path(sys._MEIPASS) / "data" / "configs"
        logger.info(builtin_configs)
        if builtin_configs.exists():
            for file in builtin_configs.iterdir():
                shutil.copy(file, CONFIGS_DIR / file.name)


def resource_path(relative_path: str) -> Path:
    """
    Возвращает абсолютный путь к файлу конфигов:
    1) Всегда /tmps/<...>
    2) Если файла нет — попробует прочитать из встроенных ресурсов (_MEIPASS)
    """
    external = ROOT_DATA_DIR / relative_path
    if external.exists():
        return external
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        if Path("/tmps").exists():
            internal = Path(sys._MEIPASS) / "tmps" / relative_path
            if internal.exists():
                return internal
        else:
            return Path(sys.executable).parent / relative_path
    # Dev mode
    return external


class BaseParams:
    params: BaseModel
    params_class: type[BaseModel]
    CONFIG_YAML_PATH: Path = resource_path("configs/example-secret-parameters.yaml")

    @classmethod
    def update_config_data_from_file(cls):
        with open(cls.CONFIG_YAML_PATH, 'r', encoding="utf-8") as file:
            cls.params = parse_yaml_raw_as(cls.params_class, file.read())

    @classmethod
    def save_config_data(cls):
        with open(cls.CONFIG_YAML_PATH, 'w', encoding='utf8') as file:
            file.write(to_yaml_str(cls.params))

    @classmethod
    def get_parameters(cls) -> str:
        return cls.params.model_dump_json()

    @classmethod
    def set_parameters(cls, params: dict) -> None:
        cls.params = cls.params_class(**params)

    @classmethod
    def get_parameter_schema(cls) -> dict[str, Any]:
        return cls.params.model_json_schema()


class HexstrikeParams(BaseParams):
    params: Parameters = None
    params_class = Parameters
    CONFIG_YAML_PATH = resource_path("configs/parameters.yaml")


class HexstrikeSecretParams(BaseParams):
    params: Parameters = None
    params_class = SecretParameters
    CONFIG_YAML_PATH = resource_path("configs/secret-parameters.yaml")


HexstrikeParams.update_config_data_from_file()
HexstrikeSecretParams.update_config_data_from_file()
