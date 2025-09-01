from rest_framework_simplejwt.tokens import RefreshToken

def blacklist_refresh_token(refresh_token: str):
    """Blacklist a refresh token."""
    token = RefreshToken(refresh_token)
    token.blacklist()