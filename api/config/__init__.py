from environs import Env
import logging
import logging.config
from pathlib import Path


default_app_path = Path(__file__).parent.parent
env = Env(expand_vars=True)
env.read_env(default_app_path/"main.env")
default_app_path = default_app_path/"run"

# configure logging
with env.prefixed('P2PMARKET_'):
    app_path = Path(env('PATH', default_app_path))
    logs = app_path.joinpath('logs')
logs.mkdir(parents=True, exist_ok=True)
print(app_path/'config/logging.conf')
logging.config.fileConfig(
        Path(__file__).parent/'logging.conf',
        defaults={'logpath': logs},
        disable_existing_loggers=False
)

# database config
with env.prefixed('P2PMARKET_'):
    db_path = Path(env('PATH', app_path)).joinpath(env('DB_NAME', 'database.db'))
    db_debug = env.bool('DB_DEBUG', False)
db_url = f"sqlite:///{db_path}"

