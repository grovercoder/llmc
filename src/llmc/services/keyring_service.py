import keyring

SERVICE_NAME = "llmc"


class KeyringService:
    @staticmethod
    def set_key(provider_id: str, api_key: str) -> bool:
        """Store API key in system keyring."""
        try:
            keyring.set_password(SERVICE_NAME, provider_id, api_key)
            return True
        except Exception as e:
            return False

    @staticmethod
    def get_key(provider_id: str) -> str | None:
        """Retrieve API key from system keyring."""
        try:
            return keyring.get_password(SERVICE_NAME, provider_id)
        except Exception:
            return None

    @staticmethod
    def remove_key(provider_id: str) -> bool:
        """Remove API key from system keyring."""
        try:
            keyring.delete_password(SERVICE_NAME, provider_id)
            return True
        except keyring.errors.PasswordDeleteError:
            return False
        except Exception:
            return False

    @staticmethod
    def is_available() -> bool:
        """Check if keyring is available on this system."""
        try:
            keyring.get_keyring()
            return True
        except Exception:
            return False