"""Constants for Luxembourg Spritpreise."""

DOMAIN = "luxembourg_sprit"

# Config keys
CONF_VEHICLE_NAME = "vehicle_name"
CONF_TANK_SIZE = "tank_size"
CONF_FUEL_TYPE = "fuel_type"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_TANK_SIZE = 50
DEFAULT_FUEL_TYPE = "Super 95"

FUEL_TYPES = ["Super 95", "Super 98", "Diesel", "LPG"]

# Data sources
RSS_URL = "https://www.lesfrontaliers.lu/feed/"
CARBU_URL = "https://carbu.com/luxembourg/index.php/prixmaximum"

# RSS keywords per fuel type
FUEL_KEYWORDS = {
    "Super 95": ["sp95", "super 95"],
    "Super 98": ["sp98", "super 98"],
    "Diesel":   ["diesel"],
    "LPG":      ["lpg", "gpl"],
}
GENERAL_KEYWORDS = ["carburant", "prix à la pompe", "essence"]

# RSS price patterns (generic, all fuel types)
PRICE_PATTERNS = [
    r"(\d[,\.]\d{3})\s*(?:€|euro)\s*le litre",
    r"sp9[58][^\d]*(\d[,\.]\d{3})",
    r"super\s*9[58][^\d]*(\d[,\.]\d{3})",
    r"diesel[^\d]*(\d[,\.]\d{3})",
    r"essence[^\d]*(\d[,\.]\d{3})\s*(?:€|euro)",
    r"(\d[,\.]\d{3})\s*(?:€|euro)\s*(?:par litre|/l)",
]

# Sensor attribute keys
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
ATTR_SOURCE = "source"
