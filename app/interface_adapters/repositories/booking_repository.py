from botocore.exceptions import ClientError

from app.exceptions import BookingCancelError
from app.infrastructure.db.dynamo import deserialize, get_table


class BookingRepository:
    def __init__(self, table) -> None:
        self._table = table

    def get_by_id(self, booking_id: str) -> dict | None:
        result = self._table.get_item(Key={"id": booking_id})
        item = result.get("Item")
        return deserialize(item) if item else None

    def list_all(self) -> list[dict]:
        result = self._table.scan()
        return [deserialize(i) for i in result.get("Items", [])]

    def list_by_user(self, user_id: int) -> list[dict]:
        result = self._table.query(
            IndexName="user_id-index",
            KeyConditionExpression="user_id = :uid",
            ExpressionAttributeValues={":uid": user_id},
        )
        return [deserialize(i) for i in result.get("Items", [])]

    def list_by_concert(self, concert_id: str) -> list[dict]:
        result = self._table.query(
            IndexName="concert_id-index",
            KeyConditionExpression="concert_id = :cid",
            ExpressionAttributeValues={":cid": concert_id},
        )
        return [deserialize(i) for i in result.get("Items", [])]

    def create(self, booking: dict) -> dict:
        self._table.put_item(Item=booking)
        return booking

    def cancel(self, booking_id: str, user_id: int) -> dict:
        try:
            response = self._table.update_item(
                Key={"id": booking_id},
                UpdateExpression="SET #s = :cancelled",
                ConditionExpression="#s = :confirmed AND user_id = :uid",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={
                    ":cancelled": "cancelled",
                    ":confirmed": "confirmed",
                    ":uid": user_id,
                },
                ReturnValues="ALL_NEW",
            )
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code == "ConditionalCheckFailedException":
                raise BookingCancelError()
            raise
        return deserialize(response["Attributes"])


def get_booking_repo() -> BookingRepository:
    return BookingRepository(get_table("Bookings"))
