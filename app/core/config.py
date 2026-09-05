from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict


class CapMode(str, Enum):
    """
    CAP theorem tradeoff'unun explicit kod karşılığı.

    CP: Quorum saglanamazsa (timeout / yetersiz oy) karar VERME, kaydı
        'pending' bırak ya da hata dön. Tutarlılık öncelikli, yanlış
        karar riskini sıfıra indirir ama sistem bazen "cevap vermez".

    AP: Quorum saglanamazsa eldeki azınlık oylarla YİNE DE karar ver,
        ama sonucu confidence="low" / needs_review=True olarak işaretle.
        Erişilebilirlik öncelikli, sistem her zaman cevap verir ama
        bazı kararlar daha az güvenilir olabilir.
    """
    CP = "CP"
    AP = "AP"


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://quorumcheck:quorumcheck@localhost:5432/quorumcheck"
    REDIS_URL: str = "redis://localhost:6379/0"

    VALIDATOR_COUNT: int = 3          # N: paralel validator worker sayısı
    QUORUM_THRESHOLD: int = 2         # floor(N/2) + 1
    VALIDATOR_TIMEOUT_SECONDS: int = 10

    CAP_MODE: CapMode = CapMode.AP    # varsayılan tradeoff kararı

    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "claude-sonnet-4-5"
    RAG_TOP_K: int = 3

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
