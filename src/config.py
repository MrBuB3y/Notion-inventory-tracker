from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    notion_token: str
    inventory_database_id: str
    sales_database_id: str

    @classmethod
    def from_environment(cls) -> "Settings":
        load_dotenv()
        values = {
            "notion_token": os.getenv("NOTION_TOKEN"),
            "inventory_database_id": os.getenv("NOTION_INVENTORY_DATABASE_ID"),
            "sales_database_id": os.getenv("NOTION_SALES_DATABASE_ID"),
        }
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
        return cls(**values)
