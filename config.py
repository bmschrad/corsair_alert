import os

# Logging setup
log_format = os.getenv("P_LOG_FORMAT", "%(asctime)s %(levelname)s: %(message)s")
log_level = os.getenv("P_LOG_LEVEL", "INFO")

# Timer Settings
LED_DELAY = os.getenv("DELAY_LED", 1) # (seconds) how long before cycling leds
UPDATE_DELAY = os.getenv("DELAY_UPDATE", 20) # (seconds) time until date source is checked again
hb_threshold = os.getenv("HB_THRESHOLD", 7) # (minutes) define when hb is too

# File Settings
sdk_path = "C:\\CUESDK.x64_2015.dll"

ops_api_uri = os.getenv("OPS_API_URI", None)
api_crt = os.getenv("OPS_API_CRT", None)
