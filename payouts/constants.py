from decimal import Decimal

from payouts.choices import PayoutStatus

MIN_PAYOUT_AMOUNT = Decimal("0.01")

FINAL_PAYOUT_STATUSES = (
    PayoutStatus.SUCCESS,
    PayoutStatus.FAILED,
    PayoutStatus.CANCELED,
)

TASK_RESULT_SUCCESS = "SUCCESS"
TASK_RESULT_NOT_FOUND = "ERROR_NOT_FOUND"
TASK_RESULT_TIMEOUT = "ERROR_TIMEOUT"
