
from database import create_database
from migration import migrate_data
from validation import validate_data
from sync import synchronize_data
from config import get_database_config


def main():
    print("\n===================================")
    print(" DATABASE MIGRATION & SYNC TOOL")
    print("===================================")

    while True:
        print("\nChoose an Operation:")
        print("1. Create Sample Source Database")
        print("2. Migrate Data")
        print("3. Validate Data")
        print("4. Synchronize Databases")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ")

        try:
            if choice == "1":
                create_database()

            elif choice == "2":
                config = get_database_config()
                if config:
                    migrate_data(config)

            elif choice == "3":
                config = get_database_config()
                if config:
                    validate_data(config)

            elif choice == "4":
                config = get_database_config()
                if config:
                    synchronize_data(config)

            elif choice == "5":
                print("Thank you for using our tool!")
                break

            else:
                print("Invalid choice! Try again.")

        except Exception as error:
            print("\nOperation failed:", error)


if __name__ == "__main__":
    main()
