
import sqlite3
from pymongo import MongoClient


def quote_identifier(name):
    return '"' + name.replace('"', '""') + '"'


def synchronize_data(config, table_name):
    sqlite_path = config["source_path"]
    mongo_uri = config["mongo_uri"]
    mongo_database = config["mongo_database"]
    mongo_collection = config["mongo_collection"]

    source_conn = sqlite3.connect(sqlite_path)
    source_conn.row_factory = sqlite3.Row
    cursor = source_conn.cursor()

    try:
        cursor.execute(
            f"PRAGMA table_info({quote_identifier(table_name)})"
        )
        columns = cursor.fetchall()

        if not columns:
            raise ValueError("Selected table does not exist.")

        primary_keys = [
            column["name"]
            for column in sorted(columns, key=lambda col: col["pk"])
            if column["pk"] > 0
        ]

        if not primary_keys:
            raise ValueError("Selected table requires a primary key.")

        cursor.execute(
            f"SELECT * FROM {quote_identifier(table_name)}"
        )
        records = cursor.fetchall()

        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000
        )

        try:
            client.admin.command("ping")

            collection = client[mongo_database][mongo_collection]

            inserted = 0
            updated = 0
            unchanged = 0

            for record in records:
                document = dict(record)

                filter_query = {
                    key: document[key] for key in primary_keys
                }

                result = collection.update_one(
                    filter_query,
                    {"$set": document},
                    upsert=True
                )

                if result.upserted_id is not None:
                    inserted += 1
                elif result.modified_count > 0:
                    updated += 1
                else:
                    unchanged += 1

            return {
                "inserted": inserted,
                "updated": updated,
                "unchanged": unchanged,
                "total": len(records)
            }

        finally:
            client.close()

    finally:
        source_conn.close()
