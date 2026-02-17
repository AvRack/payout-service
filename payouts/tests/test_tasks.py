import pytest
from django.conf import settings
from pytest_mock import MockerFixture

from payouts.choices import PayoutStatus
from payouts.constants import (
    TASK_RESULT_NOT_FOUND,
    TASK_RESULT_SUCCESS,
    TASK_RESULT_TIMEOUT,
)
from payouts.tasks import process_payout_task
from payouts.tests.factories import PayoutFactory

pytestmark = pytest.mark.django_db


def test_process_payout_task_success(mocker: MockerFixture) -> None:
    mocker.patch("time.sleep", return_value=None)
    payout = PayoutFactory()

    result = process_payout_task(str(payout.id))

    payout.refresh_from_db()
    assert payout.status == PayoutStatus.SUCCESS
    assert "Successfully processed" in payout.comment
    assert result == TASK_RESULT_SUCCESS


def test_process_payout_task_timeout(mocker: MockerFixture) -> None:
    mocker.patch("time.sleep", return_value=None)

    settings.PAYOUT_GATEWAY_DELAY = 15
    settings.PAYOUT_GATEWAY_TIMEOUT = 10

    payout = PayoutFactory()

    result = process_payout_task(str(payout.id))

    payout.refresh_from_db()
    assert payout.status == PayoutStatus.FAILED
    assert "Gateway timeout" in payout.comment
    assert result == TASK_RESULT_TIMEOUT


def test_process_payout_task_not_found(mocker: MockerFixture) -> None:
    mocker.patch("time.sleep", return_value=None)

    random_uuid = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

    result = process_payout_task(random_uuid)

    assert result == TASK_RESULT_NOT_FOUND
