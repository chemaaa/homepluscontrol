""" API endpoints for the Home+ Home information. """
HOMES_DATA_URL = "https://api.netatmo.com/api/homesdata"
HOMES_STATUS_URL = "https://api.netatmo.com/api/homestatus"

""" API endpoint to set the stat of the module. """
SET_STATE_URL = "https://api.netatmo.com/api/setstate"

""" Legrand/Netatmo product types """
PRODUCT_TYPES = {
    "NLG": "gateway",
    "NLGS": "gateway",
    "NLP": "plug",
    "NLPM": "plug",
    "NLPBS": "plug",
    "NLF": "light",
    "NLFN": "light",
    "NLM": "light",
    "NLL": "light",
    "NLPT": "light",
    "NBR": "automation",
    "NBO": "automation",
    "NBS": "automation",
    "NLT": "remote",
}
