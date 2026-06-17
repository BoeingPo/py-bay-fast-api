import uuid
from decimal import Decimal

from botocore.exceptions import ClientError

from app.exceptions import ConcertNotFoundError, InsufficientSeatsError
from app.infrastructure.db.dynamo import deserialize, get_table, serialize


class ConcertRepository:
    def __init__(self, table) -> None:
        self._table = table

    def list_all(self) -> list[dict]:
        result = self._table.scan()
        return [deserialize(i) for i in result.get("Items", [])]

    def get_by_id(self, concert_id: str) -> dict | None:
        result = self._table.get_item(Key={"id": concert_id})
        item = result.get("Item")
        return deserialize(item) if item else None

    def create(self, data: dict) -> dict:
        concert = serialize({
            "id": str(uuid.uuid4()),
            "available_seats": data["total_seats"],
            **data,
        })
        self._table.put_item(Item=concert)
        return deserialize(concert)

    def decrement_seats(self, concert_id: str, n: int) -> None:
        try:
            self._table.update_item(
                Key={"id": concert_id},
                UpdateExpression="SET available_seats = available_seats - :n",
                ConditionExpression="available_seats >= :n AND attribute_exists(id)",
                ExpressionAttributeValues={":n": Decimal(str(n))},
            )
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code == "ConditionalCheckFailedException":
                raise InsufficientSeatsError()
            raise

    def increment_seats(self, concert_id: str, n: int) -> None:
        self._table.update_item(
            Key={"id": concert_id},
            UpdateExpression="SET available_seats = available_seats + :n",
            ExpressionAttributeValues={":n": Decimal(str(n))},
        )


def get_concert_repo() -> ConcertRepository:
    return ConcertRepository(get_table("Concerts"))
