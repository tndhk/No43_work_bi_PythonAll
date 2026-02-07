"""Authentication provider protocol and implementations."""
import os
from typing import Protocol, Optional, List
from src.auth.flask_login_setup import User
from src.data.config import settings


class AuthProvider(Protocol):
    """Protocol for authentication providers.
    
    This allows swapping authentication backends (form, SAML, etc.)
    without changing the rest of the application.
    """

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        ...

    def get_user_groups(self, user_id: str) -> List[str]:
        """Get groups for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of group names the user belongs to
        """
        ...

    def get_login_url(self) -> str:
        """Get the login URL for this provider.
        
        Returns:
            Login URL (e.g., "/login" for form auth, SAML endpoint for SAML)
        """
        ...


class FormAuthProvider:
    """Form-based authentication provider.
    
    Uses username/password from environment variables.
    Future: Can be replaced with SAMLAuthProvider for SAML SSO.
    """

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with form credentials.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User object if credentials match, None otherwise
        """
        # Validate inputs
        if not username or not password:
            return None

        # Check credentials against environment (if set) or settings defaults
        expected_username = os.getenv("BASIC_AUTH_USERNAME") or settings.basic_auth_username
        expected_password = os.getenv("BASIC_AUTH_PASSWORD") or settings.basic_auth_password

        if username == expected_username and password == expected_password:
            # Get user groups (stub for now, will be implemented in next phase)
            groups = self.get_user_groups(username)
            return User(username, groups)

        return None

    def get_user_groups(self, user_id: str) -> List[str]:
        """Get groups for a user.
        
        Currently returns empty list. Will be implemented in next phase
        with YAML config file.
        
        Args:
            user_id: User ID
            
        Returns:
            Empty list for now (stub)
        """
        # Stub: Will be implemented in next phase with YAML config
        return []

    def get_login_url(self) -> str:
        """Get the login URL for form authentication.
        
        Returns:
            "/login"
        """
        return "/login"


# Global auth provider instance
# Can be swapped based on config.auth_provider_type in the future
_auth_provider: Optional[AuthProvider] = None


def get_auth_provider() -> AuthProvider:
    """Get the current authentication provider.
    
    Returns:
        AuthProvider instance
    """
    global _auth_provider
    if _auth_provider is None:
        _auth_provider = FormAuthProvider()
    return _auth_provider


def set_auth_provider(provider: AuthProvider) -> None:
    """Set the authentication provider (for testing or SAML switching).
    
    Args:
        provider: AuthProvider instance
    """
    global _auth_provider
    _auth_provider = provider
