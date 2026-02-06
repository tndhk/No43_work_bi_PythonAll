"""Flask-Login setup and User model."""
from flask_login import LoginManager, UserMixin
from typing import List


class User(UserMixin):
    """User model for Flask-Login.
    
    Attributes:
        id: User ID (username)
        groups: List of group names the user belongs to
    """

    def __init__(self, user_id: str, groups: List[str]):
        """Initialize user.
        
        Args:
            user_id: User ID (username)
            groups: List of group names
        """
        self.id = user_id
        self.groups = groups

    def __repr__(self):
        return f"<User {self.id}>"


# Global login manager instance
_login_manager: LoginManager = None


def init_login_manager(app) -> None:
    """Initialize Flask-Login manager.
    
    Args:
        app: Flask app instance
    """
    global _login_manager
    _login_manager = LoginManager()
    _login_manager.init_app(app)
    _login_manager.login_view = "/login"
    _login_manager.login_message = "Please log in to access this page."

    @_login_manager.user_loader
    def load_user(user_id: str) -> User:
        """Load user from session.
        
        Args:
            user_id: User ID from session
            
        Returns:
            User object
        """
        # For now, create a user with empty groups
        # In next phase, load groups from YAML config
        return User(user_id, [])


def get_login_manager() -> LoginManager:
    """Get the login manager instance.
    
    Returns:
        LoginManager instance
    """
    return _login_manager
