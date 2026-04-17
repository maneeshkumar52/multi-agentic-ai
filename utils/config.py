import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # SMTP Configuration
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')
    AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT')

    # Email Settings
    FROM_EMAIL = os.getenv('FROM_EMAIL')
    DEFAULT_TO_EMAIL = os.getenv('DEFAULT_TO_EMAIL')

    # Application Settings
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', './outputs'))

    @classmethod
    def validate(cls):
        """Returns list of errors (empty list if valid)"""
        errors = []
        required_fields = [
            ('SMTP_HOST', cls.SMTP_HOST),
            ('SMTP_PORT', cls.SMTP_PORT),
            ('SMTP_USER', cls.SMTP_USER),
            ('SMTP_PASSWORD', cls.SMTP_PASSWORD),
            ('FROM_EMAIL', cls.FROM_EMAIL),
            ('DEFAULT_TO_EMAIL', cls.DEFAULT_TO_EMAIL),
            ('OUTPUT_DIR', cls.OUTPUT_DIR),
        ]

        for field_name, value in required_fields:
            if not value:
                errors.append(f"Missing required field: {field_name}")

        # Check if OUTPUT_DIR is a valid path
        if cls.OUTPUT_DIR and not isinstance(cls.OUTPUT_DIR, Path):
            errors.append("OUTPUT_DIR must be a Path object")

        return errors

    @classmethod
    def ensure_output_dir(cls):
        """Creates output directory if it doesn't exist"""
        if cls.OUTPUT_DIR:
            cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def is_azure_openai_configured(cls):
        """Checks if Azure OpenAI is configured"""
        return all([
            cls.AZURE_OPENAI_API_KEY,
            cls.AZURE_OPENAI_ENDPOINT,
            cls.AZURE_OPENAI_API_VERSION,
            cls.AZURE_OPENAI_DEPLOYMENT
        ])

# Auto-create output directory when module loads
Config.ensure_output_dir()