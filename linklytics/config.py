import logging
import os
import warnings

from pydantic import field_validator
from pydantic_settings import BaseSettings

os.makedirs("output", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

warnings.filterwarnings(
    "ignore", category=UserWarning, module="openpyxl"
)  # The Linkedin xlsx doesn't have default styles so we ignore the warning


class Config(BaseSettings):
    analytics_path: str = "data"

    @field_validator("analytics_path", mode="before")
    def validate_path(cls, v):
        if not os.path.isdir(v):
            logging.error(f"The /{v} directory does not exist. Creating it...")
            os.makedirs(v)
        files = os.listdir(v)
        if len(files) != 1:
            logging.error(
                f"There must be only one file in the /{v} directory. Exiting..."
            )
            exit(1)
        if not files[0].endswith(".xlsx"):
            logging.error(f"The file must be a xlsx file. Found {files[0]}. Exiting...")
            exit(1)
        return v


config = Config()
