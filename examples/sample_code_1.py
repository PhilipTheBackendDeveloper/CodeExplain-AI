"""
Sample Code 1 — A user authentication system.

Demonstrates: classes, methods, decorators, error handling, type annotations.
This file is used for CodeExplain AI demos.
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class User:
    """Represents an authenticated system user."""
    username: str
    email: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    login_attempts: int = 0
    last_login: Optional[datetime] = None

    def is_locked(self) -> bool:
        """Return True if the account is locked due to too many failed attempts."""
        return self.login_attempts >= 5


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class UserStore:
    """In-memory user storage (for demonstration purposes)."""

    def __init__(self):
        self._users: dict[str, User] = {}

    def add_user(self, user: User) -> None:
        """Add a user to the store."""
        if user.username in self._users:
            raise ValueError(f"User '{user.username}' already exists.")
        self._users[user.username] = user

    def find_user(self, username: str) -> Optional[User]:
        """Find a user by username. Returns None if not found."""
        return self._users.get(username)

    def get_all_active(self) -> list[User]:
        """Return all active users."""
        return [u for u in self._users.values() if u.is_active]


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Hash a password using SHA-256 with a salt.

    Args:
        password: The plain-text password to hash.
        salt: Optional existing salt. If not provided, a new one is generated.

    Returns:
        A tuple of (hash_hex, salt_hex).
    """
    if salt is None:
        salt = secrets.token_hex(32)
    combined = (salt + password).encode("utf-8")
    hashed = hashlib.sha256(combined).hexdigest()
    return hashed, salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify a plain-text password against a stored hash and salt."""
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == stored_hash


class AuthService:
    """
    Authentication service that handles user registration and login.

    Example usage:
        service = AuthService()
        service.register("alice", "alice@example.com", "secure_password_123")
        user = service.login("alice", "secure_password_123")
    """

    def __init__(self, store: Optional[UserStore] = None):
        self._store = store or UserStore()
        self._sessions: dict[str, str] = {}  # token -> username
        self._salts: dict[str, str] = {}     # username -> salt

    def register(self, username: str, email: str, password: str) -> User:
        """
        Register a new user.

        Args:
            username: Unique username.
            email: Email address.
            password: Plain-text password (will be hashed).

        Returns:
            The newly created User object.

        Raises:
            ValueError: If username already exists or password too short.
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters.")

        password_hash, salt = hash_password(password)
        user = User(username=username, email=email, password_hash=password_hash)
        self._store.add_user(user)
        self._salts[username] = salt
        return user

    def login(self, username: str, password: str) -> str:
        """
        Authenticate a user and return a session token.

        Raises:
            AuthenticationError: On invalid credentials or locked account.
        """
        user = self._store.find_user(username)

        if user is None:
            raise AuthenticationError("Invalid username or password.")

        if user.is_locked():
            raise AuthenticationError(f"Account '{username}' is locked.")

        salt = self._salts.get(username, "")
        if not verify_password(password, user.password_hash, salt):
            user.login_attempts += 1
            remaining = 5 - user.login_attempts
            raise AuthenticationError(
                f"Invalid password. {remaining} attempts remaining."
            )

        # Successful login
        user.login_attempts = 0
        user.last_login = datetime.utcnow()
        token = secrets.token_urlsafe(32)
        self._sessions[token] = username
        return token

    def logout(self, token: str) -> bool:
        """Invalidate a session token. Returns True if found."""
        if token in self._sessions:
            del self._sessions[token]
            return True
        return False

    def get_user_from_token(self, token: str) -> Optional[User]:
        """Resolve a session token to a User object."""
        username = self._sessions.get(token)
        if username:
            return self._store.find_user(username)
        return None

    def get_active_sessions(self) -> int:
        """Return the number of active sessions."""
        return len(self._sessions)


if __name__ == "__main__":
    # Demo
    service = AuthService()
    service.register("alice", "alice@example.com", "my_secure_pass!")
    token = service.login("alice", "my_secure_pass!")
    print(f"Logged in. Token: {token[:16]}...")
    user = service.get_user_from_token(token)
    print(f"Session user: {user.username}")
