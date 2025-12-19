from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed


def get_tokens_for_user(user) :
    if not user.is_active :
        raise AuthenticationFailed ( "User is not active" )

    refresh = RefreshToken.for_user ( user )

    return {
        'refresh' : str ( refresh ),
        'access' : str ( refresh.access_token ),
        'is_admin' : user.is_admin,
        'is_active' : user.is_active
    }