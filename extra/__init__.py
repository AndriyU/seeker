import datetime
from .alchemy import SQLAlchemy
db = SQLAlchemy(session_options={'autoflush': False})


DEFAULT_LIMIT = 15
MAX_LIMIT = 200
CURRENT_YEAR = datetime.date.today().year
WP_REDIS_KEY = 'core:wp:posts:'