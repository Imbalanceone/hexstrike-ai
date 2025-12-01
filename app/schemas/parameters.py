from pydantic import BaseModel, Field


class Parameters(BaseModel):
    USE_IP_FILTER: bool = Field(description="Логический ключ, использовать ли фильтр по ип адресам", default=False)


########


class SecretParameters(BaseModel):
    DEV_IP: list[str] = Field(description="Список dev ip адресов", default_factory=list)
    HOSTS: dict[str, dict[str, str]] = Field(description="Словарь хостов", default_factory=dict)
