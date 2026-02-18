import pytest
from django.urls import reverse
from pytest_mock import MockerFixture
from rest_framework import status
from rest_framework.test import APIClient

from payouts.choices import CurrencyChoices, PayoutStatus
from payouts.models import Payout
from payouts.tests.factories import PayoutFactory

pytestmark = pytest.mark.django_db


def test_get_payout_list_count(api_client: APIClient) -> None:
    p_1, p_2, p_3 = PayoutFactory.create_batch(3)
    url = reverse("payout-list")

    response = api_client.get(url)
    response_ids = [item["id"] for item in response.data]

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    assert str(p_1.id) in response_ids
    assert str(p_2.id) in response_ids
    assert str(p_3.id) in response_ids


def test_create_payout_success(api_client: APIClient, mocker: MockerFixture) -> None:
    mock_task = mocker.patch("payouts.tasks.process_payout_task.delay")
    url = reverse("payout-list")
    amount = 100.00
    payload = {
        "amount": str(amount),
        "currency": CurrencyChoices.USD,
        "recipient_details": {"card_number": "1111222233334444"},
        "comment": "test",
    }

    response = api_client.post(url, payload, format="json")

    payout = Payout.objects.first()
    assert response.status_code == status.HTTP_201_CREATED
    assert payout.amount == amount
    assert payout.currency == CurrencyChoices.USD
    assert payout.recipient_details == payload["recipient_details"]
    assert payout.status == PayoutStatus.PENDING

    mock_task.assert_called_once_with(str(payout.id))


@pytest.mark.parametrize(
    ("amount", "currency", "expected_field", "expected_code"),
    [
        ("0.00", "RUB", "amount", "min_value"),
        ("-50.00", "RUB", "amount", "min_value"),
        ("100.00", "GBP", "currency", "invalid_choice"),
    ],
)
def test_create_payout_validation_errors(
    api_client: APIClient,
    mocker: MockerFixture,
    amount: str,
    currency: str,
    expected_field: str,
    expected_code: str,
) -> None:
    url = reverse("payout-list")
    mock_task = mocker.patch("payouts.tasks.process_payout_task.delay")
    payload = {
        "amount": amount,
        "currency": currency,
        "recipient_details": {"card_number": "1111222233334444"},
    }

    response = api_client.post(url, payload, format="json")
    error_tuples = [(e["field"], e["code"]) for e in response.data["errors"]]

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (expected_field, expected_code) in error_tuples

    mock_task.assert_not_called()


def test_patch_payout_status_success(api_client: APIClient) -> None:
    payout = PayoutFactory(status=PayoutStatus.PROCESSING)
    url = reverse("payout-detail", kwargs={"id": payout.id})
    payload = {"status": PayoutStatus.PENDING}

    response = api_client.patch(url, payload, format="json")

    payout.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert payout.status == PayoutStatus.PENDING


def test_patch_payout_status_cannot_change(api_client: APIClient) -> None:
    payout = PayoutFactory(status=PayoutStatus.SUCCESS)
    url = reverse("payout-detail", kwargs={"id": payout.id})
    payload = {"status": PayoutStatus.FAILED}

    response = api_client.patch(url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot change status" in str(response.data)


def test_patch_payout_other_fields(api_client: APIClient) -> None:
    payout = PayoutFactory(currency=CurrencyChoices.USD, status=PayoutStatus.PROCESSING)
    url = reverse("payout-detail", kwargs={"id": payout.id})
    payload = {"status": PayoutStatus.PENDING, "currency": CurrencyChoices.RUB}

    response = api_client.patch(url, payload, format="json")

    payout.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert payout.status == PayoutStatus.PENDING
    assert payout.currency == CurrencyChoices.USD
