
import sqlite3
from pymongo import MongoClient


def quote_identifier(name):
    return '"' + name.replace('"', '""') + '"'


def validate_data(config, table_name):
    sqlite_path = config["source_path"]
    mongo_uri = config["mongo_uri"]
    mongo_database = config["mongo_database"]
    mongo_collection = config["mongo_collection"]

    source_conn = sqlite3.connect(sqlite_path)
    source_conn.row_factory = sqlite3.Row

    try:
        cursor = source_conn.cursor()

        # Check table and discover its columns
        cursor.execute(
            f"PRAGMA table_info({quote_identifier(table_name)})"
        )
        columns = cursor.fetchall()

        if not columns:
            raise ValueError("Selected table does not exist.")

        column_names = [column["name"] for column in columns]

        primary_keys = [
            column["name"]
            for column in sorted(columns, key=lambda col: col["pk"])
            if column["pk"] > 0
        ]

        if not primary_keys:
            raise ValueError("Selected table requires a primary key.")

        # Read source records
        cursor.execute(
            f"SELECT * FROM {quote_identifier(table_name)}"
        )
        source_records = [
            dict(row) for row in cursor.fetchall()
        ]

        # Connect to MongoDB
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000
        )

        try:
            client.admin.command("ping")

            collection = client[mongo_database][mongo_collection]

            destination_records = list(
                collection.find({}, {"_id": 0})
            )

            # Index MongoDB documents by primary key
            destination_map = {}

            for document in destination_records:
                key = tuple(
                    document.get(pk) for pk in primary_keys
                )
                destination_map[key] = document

            matched = 0
            missing = 0
            mismatched = 0

            source_keys = set()

            for source in source_records:
                key = tuple(
                    source.get(pk) for pk in primary_keys
                )
                source_keys.add(key)

                destination = destination_map.get(key)

                if destination is None:
                    missing += 1
                    continue

                if all(
                    source[column] == destination.get(column)
                    for column in column_names
                ):
                    matched += 1
                else:
                    mismatched += 1

            extra = sum(
                1 for key in destination_map
                if key not in source_keys
            )

            return {
                "source_count": len(source_records),
                "destination_count": len(destination_records),
                "matched": matched,
                "missing": missing,
                "mismatched": mismatched,
                "extra": extra,
                "success": (
                    missing == 0
                    and mismatched == 0
                    and extra == 0
                )
            }

        finally:
            client.close()

    finally:
        source_conn.close()
