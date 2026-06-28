"""Library business rules — aligned with common ILS (Integrated Library System) practices."""

from datetime import date, timedelta

# Maximum concurrent active loans per membership tier
LOAN_LIMITS: dict[str, int] = {
    "student": 5,
    "faculty": 10,
    "public": 3,
}

# Loan period in days per membership tier
LOAN_PERIODS_DAYS: dict[str, int] = {
    "student": 14,
    "faculty": 30,
    "public": 21,
}


def loan_limit(membership_type: str) -> int:
    return LOAN_LIMITS.get(membership_type, 3)


def loan_period_days(membership_type: str) -> int:
    return LOAN_PERIODS_DAYS.get(membership_type, 14)


def default_due_date(membership_type: str, from_date: date | None = None) -> date:
    start = from_date or date.today()
    return start + timedelta(days=loan_period_days(membership_type))
