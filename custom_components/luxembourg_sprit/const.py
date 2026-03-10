"""Constants for Luxembourg Spritpreise."""

DOMAIN = "luxembourg_sprit"

CONF_VEHICLE_NAME = "vehicle_name"
CONF_TANK_SIZE = "tank_size"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 60
DEFAULT_TANK_SIZE = 50

RSS_URL = "https://www.lesfrontaliers.lu/feed/"

FUEL_KEYWORDS = ["sp95", "super 95", "carburant", "prix à la pompe", "essence"]

PRICE_PATTERNS = [
    r"sp95[^\d]*(\d[,\.]\d{3})\s*(?:€|euro)",
    r"(\d[,\.]\d{3})\s*(?:€|euro)\s*le litre",
    r"sp95[^\d]*(\d[,\.]\d{3})",
    r"super\s*95[^\d]*(\d[,\.]\d{3})",
    r"essence[^\d]*(\d[,\.]\d{3})\s*(?:€|euro)",
]

ATTR_PRICE = "price"
ATTR_PREVIOUS_PRICE = "previous_price"
ATTR_DIFF = "diff"
ATTR_DIFF_PCT = "diff_pct"
ATTR_TANK_COST = "tank_cost"
ATTR_TANK_DIFF = "tank_diff"
ATTR_ARTICLE_TITLE = "article_title"
ATTR_ARTICLE_LINK = "article_link"
ATTR_ARTICLE_DATE = "article_date"
ATTR_LAST_CHECK = "last_check"
ATTR_STATUS = "status"
