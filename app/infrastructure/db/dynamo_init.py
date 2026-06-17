from app.infrastructure.db.dynamo import get_dynamo_client


def init_dynamo_tables() -> None:
    client = get_dynamo_client()
    existing = client.list_tables()["TableNames"]

    if "Concerts" not in existing:
        client.create_table(
            TableName="Concerts",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

    if "Bookings" not in existing:
        client.create_table(
            TableName="Bookings",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "concert_id", "AttributeType": "S"},
                {"AttributeName": "user_id", "AttributeType": "N"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "concert_id-index",
                    "KeySchema": [{"AttributeName": "concert_id", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "user_id-index",
                    "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
