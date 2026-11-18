
import os
import sqlite3
import streamlit as st
from pymongo import MongoClient

from migration import migrate_data
from sync import synchronize_data
from validation import validate_data


# ---------------------------------
# PAGE CONFIGURATION
# ---------------------------------

st.set_page_config(
    page_title="Database Migration Tool",
    page_icon="🗄️",
    layout="wide"
)

st.title("🗄️ Database Migration & Synchronization Tool")
st.caption("Transfer, synchronize and validate data between databases.")

st.divider()


# ---------------------------------
# HELPER: DISCOVER SQLITE TABLES
# ---------------------------------

def get_tables(database_path):
    if not os.path.isfile(database_path):
        return []

    conn = sqlite3.connect(database_path)

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)

        return [row[0] for row in cursor.fetchall()]

    finally:
        conn.close()


# ---------------------------------
# SIDEBAR: DATABASE CONFIGURATION
# ---------------------------------

st.sidebar.header("⚙️ Database Configuration")

source_path = st.sidebar.text_input(
    "SQLite Source Database Path",
    value="data/employees.db",
    help="Example: data/employees.db"
)

mongo_uri = st.sidebar.text_input(
    "MongoDB Connection URI",
    value="mongodb://localhost:27017"
)

mongo_database = st.sidebar.text_input(
    "MongoDB Database Name",
    value="migration_project"
)

config = {
    "source_type": "sqlite",
    "source_path": source_path.strip(),
    "mongo_uri": mongo_uri.strip(),
    "mongo_database": mongo_database.strip(),
    "mongo_collection": ""
}


# ---------------------------------
# CONNECTION TESTING
# ---------------------------------

if st.sidebar.button("Test Connections", use_container_width=True):

    if not source_path.strip() or not os.path.isfile(source_path.strip()):
        st.sidebar.error("SQLite database file not found.")

    else:
        try:
            conn = sqlite3.connect(source_path.strip())
            conn.execute("SELECT 1")
            conn.close()

            st.sidebar.success("SQLite connection successful!")

        except Exception as error:
            st.sidebar.error(f"SQLite error: {error}")

        try:
            client = MongoClient(
                mongo_uri.strip(),
                serverSelectionTimeoutMS=5000
            )

            client.admin.command("ping")
            client.close()

            st.sidebar.success("MongoDB connection successful!")

        except Exception as error:
            st.sidebar.error(f"MongoDB error: {error}")


st.sidebar.divider()

st.sidebar.info(
    "Current version supports SQLite as the source "
    "and MongoDB as the destination."
)


# ---------------------------------
# DISCOVER SOURCE TABLES
# ---------------------------------

tables = get_tables(source_path.strip())

if not tables:

    st.warning(
        "No SQLite tables found. Check your database file path."
    )

    st.info(
        "For testing, enter data/employees.db "
        "if you have already created the employee database."
    )

    st.stop()


# ---------------------------------
# TABLE AND COLLECTION SELECTION
# ---------------------------------

st.subheader("📂 Source and Destination")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Source: SQLite**")

    selected_table = st.selectbox(
        "Select Source Table",
        tables
    )

with col2:
    st.markdown("**Destination: MongoDB**")

    collection_name = st.text_input(
        "Destination Collection",
        value=selected_table
    )

config["mongo_collection"] = collection_name.strip()


if not config["mongo_database"] or not config["mongo_collection"]:
    st.warning("Enter a MongoDB database and collection name.")
    st.stop()


st.divider()


# ---------------------------------
# DASHBOARD METRICS
# ---------------------------------

try:
    conn = sqlite3.connect(source_path.strip())

    source_count = conn.execute(
        f'SELECT COUNT(*) FROM "{selected_table.replace(chr(34), chr(34)*2)}"'
    ).fetchone()[0]

    conn.close()

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric("Available Tables", len(tables))
    metric2.metric("Selected Table", selected_table)
    metric3.metric("Source Records", source_count)

except Exception as error:
    st.error(f"Unable to read source records: {error}")
    st.stop()


st.divider()


# ---------------------------------
# DATABASE OPERATIONS
# ---------------------------------

st.subheader("🚀 Database Operations")

col1, col2, col3 = st.columns(3)


# MIGRATION

with col1:

    st.markdown("### 📤 Migration")

    st.write("Transfer source records to MongoDB.")

    if st.button("Start Migration", use_container_width=True):

        try:
            with st.spinner("Migrating records..."):

                count = migrate_data(config, selected_table)

            st.success("Migration completed!")
            st.metric("Records Migrated", count)

        except Exception as error:
            st.error(f"Migration failed: {error}")


# SYNCHRONIZATION

with col2:

    st.markdown("### 🔄 Synchronization")

    st.write("Insert new records and update changed records.")

    if st.button("Start Synchronization", use_container_width=True):

        try:
            with st.spinner("Synchronizing records..."):

                result = synchronize_data(
                    config,
                    selected_table
                )

            st.success("Synchronization completed!")

            st.write("**Synchronization Report**")

            st.metric("New Records", result["inserted"])
            st.metric("Updated Records", result["updated"])
            st.metric("Unchanged Records", result["unchanged"])

        except Exception as error:
            st.error(f"Synchronization failed: {error}")


# VALIDATION

with col3:

    st.markdown("### 🛡️ Validation")

    st.write("Compare source and destination records.")

    if st.button("Validate Data", use_container_width=True):

        try:
            with st.spinner("Validating records..."):

                result = validate_data(
                    config,
                    selected_table
                )

            st.write("**Validation Report**")

            st.metric("SQLite Records", result["source_count"])
            st.metric("MongoDB Records", result["destination_count"])
            st.metric("Matched Records", result["matched"])
            st.metric("Missing Records", result["missing"])
            st.metric("Mismatched Records", result["mismatched"])
            st.metric("Extra Records", result["extra"])

            if result["success"]:
                st.success("All records match!")
            else:
                st.warning("Data differences detected.")

        except Exception as error:
            st.error(f"Validation failed: {error}")


st.divider()


# ---------------------------------
# FOOTER
# ---------------------------------

st.caption(
    "Database Migration Tool | SQLite → MongoDB | "
    "Built with Python and Streamlit"
)
