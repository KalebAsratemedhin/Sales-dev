"""
LinkedIn REST API constants (documented endpoints).
"""

# REST API base and version (Microsoft Learn docs)
LINKEDIN_API_BASE = "https://api.linkedin.com/rest"
LINKEDIN_VERSION = "202406"
RESTLI_PROTOCOL_VERSION = "2.0.0"

# Login
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/uas/login"
LINKEDIN_LOGIN_SUBMIT_URL = "https://www.linkedin.com/uas/login-submit"

# Cookie names we care about for API requests
LINKEDIN_SESSION_COOKIE_NAMES = ("li_at", "JSESSIONID")
