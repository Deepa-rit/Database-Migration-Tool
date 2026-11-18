
def get_database_config():
    print("\n===== DATABASE CONFIGURATION =====")

    print("\nSOURCE DATABASE")
    print("1. SQLite")

    source_choice = input("Choose source database (1): ")

    if source_choice != "1":
        print("Currently, only SQLite is supported.")
        return None

    sqlite_path = input(
        "Enter SQLite database file path (example: data/source.db): "
    ).strip()

    if not sqlite_path:
        print("Source database path cannot be empty.")
        return None

    print("\nDESTINATION DATABASE")
    mongo_uri = input(
        "Enter MongoDB URI (press Enter for local MongoDB): "
    ).strip()

    if not mongo_uri:
        mongo_uri = "mongodb://localhost:27017"

    mongo_database = input(
        "Enter MongoDB database name (default: migration_project): "
    ).strip()

    if not mongo_database:
        mongo_database = "migration_project"

    mongo_collection = input(
        "Enter collection name (default: students): "
    ).strip()

    if not mongo_collection:
        mongo_collection = "students"

    return {
        "source_type": "sqlite",
        "source_path": sqlite_path,
        "mongo_uri": mongo_uri,
        "mongo_database": mongo_database,
        "mongo_collection": mongo_collection
    }
