"""Safe local defaults so test collection does not require production secrets."""

import os


os.environ.setdefault("MAIL_ADDRESS", "test@example.invalid")
os.environ.setdefault("MAIL_PASSWORD", "test-password")
os.environ.setdefault("MAIL_USERNAME", "test")
os.environ.setdefault("MAIL_SERVER", "localhost")
os.environ.setdefault("MAIL_PORT", "2525")
os.environ.setdefault("SECRET_KEY", "test-only-secret-key")
os.environ.setdefault("STORAGE_BACKEND", "local")
os.environ.setdefault("STORAGE_PATH", "tmp-test-data/storage")
