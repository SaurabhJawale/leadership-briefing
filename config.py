"""
============================================================
config.py — Centralised Configuration
Employee Daily Work Tracking Agent  v1.1.0
============================================================
"""

# ---------------------------------------------------------------------------
# Standard Library Imports
# ---------------------------------------------------------------------------
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Third-Party Imports
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
except ImportError:
    print(
        "[FATAL] python-dotenv is not installed. "
        "Run: pip3 install python-dotenv"
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Load .env before anything else so os.getenv() picks up the values
# ---------------------------------------------------------------------------
load_dotenv()


# ===========================================================================
# SECTION 1 — DIRECTORY / PATH CONFIGURATION
# ===========================================================================

BASE_DIR:    Path = Path(__file__).resolve().parent
DATA_DIR:    Path = BASE_DIR / "data"
REPORTS_DIR: Path = BASE_DIR / "reports"
LOGS_DIR:    Path = BASE_DIR / "logs"

for _directory in (DATA_DIR, REPORTS_DIR, LOGS_DIR):
    _directory.mkdir(parents=True, exist_ok=True)

DEFAULT_EXCEL_PATH: Path = DATA_DIR / "employee_tasks.xlsx"
REPORT_FILENAME_TEMPLATE: str = "manager_report_{timestamp}.txt"
LOG_FILENAME_TEMPLATE: str = "agent_{timestamp}.log"


# ===========================================================================
# SECTION 2 — LOGGING CONFIGURATION
# ===========================================================================

_RUN_TIMESTAMP: str = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE: Path = LOGS_DIR / LOG_FILENAME_TEMPLATE.format(timestamp=_RUN_TIMESTAMP)

LOG_LEVEL:       int = logging.INFO
LOG_FORMAT:      str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger: logging.Logger = logging.getLogger("EmployeeTrackingAgent")


# ===========================================================================
# SECTION 3 — ENVIRONMENT VARIABLE KEY NAMES
# ===========================================================================

class EnvKeys:
    LLM_PROVIDER:        str = "LLM_PROVIDER"
    GROQ_API_KEY:        str = "GROQ_API_KEY"
    GEMINI_API_KEY:      str = "GEMINI_API_KEY"
    SENDER_EMAIL:        str = "SENDER_EMAIL"
    SENDER_APP_PASSWORD: str = "SENDER_APP_PASSWORD"
    MANAGER_EMAIL:       str = "MANAGER_EMAIL"
    EXCEL_FILE_PATH:     str = "EXCEL_FILE_PATH"


# ===========================================================================
# SECTION 4 — GROQ API SETTINGS
# ===========================================================================

class GroqConfig:
    API_URL:       str = "https://api.groq.com/openai/v1/chat/completions"
    DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
    AVAILABLE_MODELS: list = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "gemma2-9b-it",
        "mixtral-8x7b-32768",
    ]
    TEMPERATURE:  float = 0.4
    MAX_TOKENS:   int   = 2000
    TIMEOUT_SEC:  int   = 60
    SYSTEM_PROMPT: str  = (
        "You are a senior project management analyst. "
        "Write clear, professional, and actionable manager reports. "
        "Be concise, data-driven, and specific. Avoid generic filler text."
    )


# ===========================================================================
# SECTION 5 — GEMINI API SETTINGS
# ===========================================================================

class GeminiConfig:
    DEFAULT_MODEL: str = "gemini-1.5-flash"
    API_URL_TEMPLATE: str = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "{model}:generateContent?key={api_key}"
    )
    TEMPERATURE:       float = 0.4
    MAX_OUTPUT_TOKENS: int   = 2000
    TIMEOUT_SEC:       int   = 60


# ===========================================================================
# SECTION 6 — BUSINESS RULES
# ===========================================================================

class BusinessRules:
    STATUS_COMPLETED: str = "completed"

    BLOCKER_KEYWORDS: frozenset = frozenset({
        "waiting",
        "approval",
        "vendor",
        "dependency",
        "access",
        "blocked",
        "blocker",
        "stuck",
    })

    GREEN_THRESHOLD:  float = 70.0
    YELLOW_THRESHOLD: float = 40.0

    MAX_DELAYED_IN_PROMPT:   int = 10
    MAX_BLOCKERS_IN_PROMPT:  int = 10
    MAX_TASK_ROWS_IN_PROMPT: int = 100
    TOP_CONTRIBUTORS_COUNT:  int = 5

    REQUIRED_COLUMNS: frozenset = frozenset({
        "Employee",
        "Project",
        "Task",
        "Status",
        "Due Date",
        "Comments",
    })

    CRITICAL_COLUMNS: list = ["Employee", "Task", "Status"]


# ===========================================================================
# SECTION 7 — EMAIL SETTINGS
# ===========================================================================

class EmailConfig:
    SUBJECT_TEMPLATE: str = "📊 Daily Work Tracking Report – {date}"
    DATE_FORMAT:      str = "%B %d, %Y"
    BODY_PREAMBLE:    str = (
        "Please find today's employee work tracking report below and attached.\n\n"
    )


# ===========================================================================
# SECTION 8 — REPORT SETTINGS
# ===========================================================================

class ReportConfig:
    FILENAME_TIMESTAMP_FORMAT: str = "%Y%m%d_%H%M%S"
    FILE_EXTENSION:  str = ".txt"
    SEPARATOR_WIDTH: int = 64
    AGENT_VERSION:   str = "1.1.0"


# ===========================================================================
# SECTION 9 — MASTER CONFIG OBJECT
# ===========================================================================

@dataclass
class Config:
    # ── Paths ────────────────────────────────────────────────────────────
    BASE_DIR:           Path = field(default_factory=lambda: BASE_DIR)
    DATA_DIR:           Path = field(default_factory=lambda: DATA_DIR)
    REPORTS_DIR:        Path = field(default_factory=lambda: REPORTS_DIR)
    LOGS_DIR:           Path = field(default_factory=lambda: LOGS_DIR)
    LOG_FILE:           Path = field(default_factory=lambda: LOG_FILE)
    DEFAULT_EXCEL_PATH: Path = field(default_factory=lambda: DEFAULT_EXCEL_PATH)

    RUN_TIMESTAMP: str = field(default_factory=lambda: _RUN_TIMESTAMP)

    # ── Sub-config namespaces ────────────────────────────────────────────
    groq:   GroqConfig    = field(default_factory=GroqConfig)
    gemini: GeminiConfig  = field(default_factory=GeminiConfig)
    rules:  BusinessRules = field(default_factory=BusinessRules)
    email:  EmailConfig   = field(default_factory=EmailConfig)
    report: ReportConfig  = field(default_factory=ReportConfig)
    env:    EnvKeys       = field(default_factory=EnvKeys)

    # ── Flat convenience aliases ─────────────────────────────────────────
    GROQ_API_URL: str      = field(default_factory=lambda: GroqConfig.API_URL)
    GROQ_MODEL:   str      = field(default_factory=lambda: GroqConfig.DEFAULT_MODEL)
    BLOCKER_KEYWORDS: frozenset = field(
        default_factory=lambda: BusinessRules.BLOCKER_KEYWORDS
    )
    STATUS_COMPLETED: str  = field(
        default_factory=lambda: BusinessRules.STATUS_COMPLETED
    )
    REQUIRED_COLUMNS: frozenset = field(
        default_factory=lambda: BusinessRules.REQUIRED_COLUMNS
    )

    # ── Runtime values read from .env ─────────────────────────────────────

    @property
    def llm_provider(self) -> str:
        return os.getenv(EnvKeys.LLM_PROVIDER, "groq").lower().strip()

    @property
    def groq_api_key(self) -> str:
        return os.getenv(EnvKeys.GROQ_API_KEY, "").strip()

    @property
    def gemini_api_key(self) -> str:
        return os.getenv(EnvKeys.GEMINI_API_KEY, "").strip()

    @property
    def sender_email(self) -> str:
        return os.getenv(EnvKeys.SENDER_EMAIL, "").strip()

    @property
    def sender_app_password(self) -> str:
        return os.getenv(EnvKeys.SENDER_APP_PASSWORD, "").strip()

    @property
    def manager_email(self) -> str:
        return os.getenv(EnvKeys.MANAGER_EMAIL, "").strip()

    @property
    def excel_file_path(self) -> Path:
        override = os.getenv(EnvKeys.EXCEL_FILE_PATH, "").strip()
        return Path(override) if override else self.DEFAULT_EXCEL_PATH

    @property
    def email_configured(self) -> bool:
        return all([self.sender_email, self.sender_app_password, self.manager_email])

    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)

    # ── Validation ────────────────────────────────────────────────────────

    def validate(self, strict: bool = False) -> None:
        issues: list = []

        supported_providers = {"groq", "gemini"}
        if self.llm_provider not in supported_providers:
            msg = (
                f"LLM_PROVIDER='{self.llm_provider}' is not supported. "
                f"Valid values: {sorted(supported_providers)}"
            )
            logger.error(msg)
            if strict:
                raise ValueError(msg)

        if self.llm_provider == "groq" and not self.groq_configured:
            issues.append(
                "GROQ_API_KEY is not set. "
                "Get a free key at https://console.groq.com  "
                "(report will use rule-based fallback)"
            )
        if self.llm_provider == "gemini" and not self.gemini_configured:
            issues.append(
                "GEMINI_API_KEY is not set. "
                "Get a free key at https://aistudio.google.com/app/apikey  "
                "(report will use rule-based fallback)"
            )

        if not self.sender_email:
            issues.append("SENDER_EMAIL is not set — email delivery will be skipped.")
        if not self.sender_app_password:
            issues.append(
                "SENDER_APP_PASSWORD is not set — email delivery will be skipped."
            )
        if not self.manager_email:
            issues.append("MANAGER_EMAIL is not set — email delivery will be skipped.")

        if not self.excel_file_path.exists():
            issues.append(
                f"Excel file not found at expected location: {self.excel_file_path}  "
                "Place employee_tasks.xlsx in the data/ folder or set EXCEL_FILE_PATH in .env"
            )

        for issue in issues:
            if strict:
                logger.error("CONFIG ERROR: %s", issue)
            else:
                logger.warning("CONFIG WARNING: %s", issue)

        if strict and issues:
            raise ValueError(
                f"Configuration validation failed with {len(issues)} issue(s). "
                "Check the log for details."
            )

    def summary(self) -> str:
        def _mask(value: str) -> str:
            if not value:
                return "⚠  NOT SET"
            if len(value) <= 4:
                return "****"
            return value[:4] + "*" * (len(value) - 4)

        llm_status = (
            f"{self.llm_provider.upper()} "
            f"({'✓ key set' if (self.groq_configured if self.llm_provider == 'groq' else self.gemini_configured) else '⚠ key missing — fallback mode'})"
        )
        email_status = (
            "✓ configured"
            if self.email_configured
            else "⚠ incomplete — email delivery disabled"
        )

        return (
            "\n"
            "╔══════════════════════════════════════════════════╗\n"
            "║    Employee Work Tracking Agent — Config         ║\n"
            "╠══════════════════════════════════════════════════╣\n"
            f"║  Version        : v{ReportConfig.AGENT_VERSION:<28}║\n"
            f"║  Base directory : {str(self.BASE_DIR)[-28:]:<28}  ║\n"
            f"║  Excel file     : {str(self.excel_file_path.name):<28}  ║\n"
            f"║  LLM provider   : {llm_status:<28}  ║\n"
            f"║  Groq model     : {self.GROQ_MODEL:<28}  ║\n"
            f"║  Email          : {email_status:<28}  ║\n"
            f"║  Log file       : {str(self.LOG_FILE.name):<28}  ║\n"
            "╚══════════════════════════════════════════════════╝"
        )


# ===========================================================================
# SECTION 10 — SINGLETON INSTANCE
# ===========================================================================

cfg = Config()

# Module-level constants for direct import (used by main.py)
REQUIRED_COLUMNS: frozenset = BusinessRules.REQUIRED_COLUMNS
STATUS_COMPLETED: str       = BusinessRules.STATUS_COMPLETED
BLOCKER_KEYWORDS: frozenset = BusinessRules.BLOCKER_KEYWORDS


# ===========================================================================
# SECTION 11 — SELF-TEST
# ===========================================================================

if __name__ == "__main__":
    print(cfg.summary())
    print("\nRunning soft validation (warnings only) …")
    cfg.validate(strict=False)

    print("\n── Key values ──────────────────────────────────────")
    print(f"  LLM provider       : {cfg.llm_provider}")
    print(f"  Groq API URL       : {cfg.GROQ_API_URL}")
    print(f"  Groq model         : {cfg.GROQ_MODEL}")
    print(f"  Groq key set       : {cfg.groq_configured}")
    print(f"  Gemini key set     : {cfg.gemini_configured}")
    print(f"  Email configured   : {cfg.email_configured}")
    print(f"  Excel path         : {cfg.excel_file_path}")
    print(f"  Excel exists       : {cfg.excel_file_path.exists()}")
    print(f"  Blocker keywords   : {sorted(cfg.BLOCKER_KEYWORDS)}")
    print(f"  Required columns   : {sorted(cfg.REQUIRED_COLUMNS)}")
    print(f"  Completion target  : {cfg.rules.GREEN_THRESHOLD}%")
    print(f"  Reports dir        : {cfg.REPORTS_DIR}")
    print(f"  Logs dir           : {cfg.LOGS_DIR}")
    print(f"  Log file           : {cfg.LOG_FILE.name}")
    print("────────────────────────────────────────────────────")
    print("✅  config.py loaded successfully.")
