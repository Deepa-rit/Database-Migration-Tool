
import sqlite3
from pymongo import MongoClient


def quote_identifier(name):
    return '"' + name.replace('"', '""') + '"'


def migrate_data(config, table_name):
    sqlite_path = config["source_path"]
    mongo_uri = config["mongo_uri"]
    mongo_database = config["mongo_database"]
    mongo_collection = config["mongo_collection"]

    source_conn = sqlite3.connect(sqlite_path)
    source_conn.row_factory = sqlite3.Row

    cursor = source_conn.cursor()

    # Check whether the selected table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type = 'table' AND name = ?
    """, (table_name,))

    if not cursor.fetchone():
        source_conn.close()
        raise ValueError("Selected table does not exist.")

    # Discover primary keys
    cursor.execute(
        f"PRAGMA table_info({quote_identifier(table_name)})"
    )
    columns = cursor.fetchall()

    primary_keys = [
        column["name"]
        for column in sorted(columns, key=lambda col: col["pk"])
        if column["pk"] > 0
    ]

    if not primary_keys:
        source_conn.close()
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

        for record in records:
            document = dict(record)

            filter_query = {
                key: document[key] for key in primary_keys
            }

            collection.update_one(
                filter_query,
                {"$set": document},
                upsert=True
            )

        return len(records)

    finally:
        source_conn.close()
        client.close()
