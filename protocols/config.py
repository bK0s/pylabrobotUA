import logging
from pathlib import Path
from pylabrobot.config import Config

config = Config(
  logging=Config.Logging(
    level=logging.DEBUG,
    log_dir=Path("logs")
  )
)