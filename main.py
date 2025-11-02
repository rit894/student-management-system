import mysql.connector
from db_connect import get_connection

def list_tables(conn):
    """Fetch and display all tables."""
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    return tables

def create_new_table(conn):
    """Create a new table with custom columns."""
    cursor = conn.cursor()
    table_name = input("\nEnter a name for your new table: ").strip()

    print("\nNOTE: Every table automatically gets an 'id' column.")
    print("      This 'id' is a unique number for each record and increases automatically.")
    print("      So you do NOT need to create an 'id' column yourself.\n")

    columns = []
    while True:
        col_name = input("Enter column name (press Enter to stop): ").strip()
        if not col_name:
            break

        print("Select data type:")
        print("1. VARCHAR(255)")
        print("2. INT")
        print("3. FLOAT")
        print("4. DATE")
        dtype_choice = input("Enter your choice (1-4): ").strip()

        dtype_map = {"1": "VARCHAR(255)", "2": "INT", "3": "FLOAT", "4": "DATE"}
        col_type = dtype_map.get(dtype_choice, "VARCHAR(255)")

        columns.append(f"{col_name} {col_type}")

    if not columns:
        print("No columns provided. Table creation cancelled.")
        return None

    columns_sql = ", ".join(columns)
    sql = f"CREATE TABLE {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, {columns_sql})"

    try:
        cursor.execute(sql)
        conn.commit()
        print(f"\nTable '{table_name}' created successfully!")
        print(f"Structure: id (auto), {', '.join(columns)}")
        return table_name
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")
        return None

def show_records(table_name):
    """Display all records of the selected table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    if not rows:
        print("\nNo records found.")
    else:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = [desc[0] for desc in cursor.fetchall()]
        print("\n" + "-" * 70)
        print(" | ".join(columns))
        print("-" * 70)
        for row in rows:
            print(" | ".join(str(value) for value in row))
        print("-" * 70 + "\n")
    conn.close()

def add_record(table_name):
    """Add a new record to the selected table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    columns = [col[0] for col in cursor.fetchall() if col[0] != "id"]

    print("\nEnter values for the following fields:")
    values = []
    for col in columns:
        values.append(input(f"{col}: "))

    placeholders = ", ".join(["%s"] * len(values))
    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    cursor.execute(sql, tuple(values))
    conn.commit()
    print("Record added successfully!")
    conn.close()

def update_record(table_name):
    """Update any field in a record."""
    conn = get_connection()
    cursor = conn.cursor()

    show_records(table_name)
    record_id = input("Enter the ID of the record to update: ").strip()

    cursor.execute(f"DESCRIBE {table_name}")
    columns = [col[0] for col in cursor.fetchall() if col[0] != "id"]

    print("\nAvailable columns to update:")
    for col in columns:
        print(f"- {col}")

    column = input("Enter column name to update: ").strip()
    if column not in columns:
        print("Invalid column name.")
        conn.close()
        return

    new_value = input("Enter new value: ")
    try:
        cursor.execute(f"UPDATE {table_name} SET {column} = %s WHERE id = %s", (new_value, record_id))
        conn.commit()
        print("Record updated successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

    conn.close()

def delete_record(table_name):
    """Delete a record by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    show_records(table_name)
    record_id = input("Enter ID of record to delete: ").strip()

    cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (record_id,))
    conn.commit()
    print("Record deleted successfully!")

    # Reorder IDs
    cursor.execute("SET @count = 0")
    cursor.execute(f"UPDATE {table_name} SET id = @count:=@count+1")
    cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1")
    conn.commit()
    conn.close()

def delete_table():
    """Delete a table from the database."""
    conn = get_connection()
    tables = list_tables(conn)
    if not tables:
        print("No tables available to delete.")
        conn.close()
        return

    print("\nAvailable tables:")
    for i, t in enumerate(tables, start=1):
        print(f"{i}. {t}")

    try:
        index = int(input("Enter table number to delete: "))
        table_name = tables[index - 1]
    except (ValueError, IndexError):
        print("Invalid choice.")
        conn.close()
        return

    confirm = input(f"Are you sure you want to delete '{table_name}'? This action cannot be undone. (y/n): ").strip().lower()
    if confirm == "y":
        cursor = conn.cursor()
        try:
            cursor.execute(f"DROP TABLE {table_name}")
            conn.commit()
            print(f"Table '{table_name}' deleted successfully.")
        except mysql.connector.Error as err:
            print(f"Error deleting table: {err}")
    else:
        print("Table deletion cancelled.")

    conn.close()

def main():
    print("=== STUDENT MANAGEMENT SYSTEM (AWS RDS + MySQL) ===")

    conn = get_connection()
    tables = list_tables(conn)

    if not tables:
        print("\nNo tables found in your database.")
        choice = input("Do you want to create a new table? (y/n): ").lower().strip()
        if choice == "y":
            table_name = create_new_table(conn)
            if not table_name:
                print("Table creation failed. Exiting.")
                return
        else:
            print("Exiting since no tables exist.")
            return
    else:
        print("\nAvailable tables:")
        for i, t in enumerate(tables, start=1):
            print(f"{i}. {t}")

        while True:
            choice = input("\nDo you want to (u)se existing or (c)reate new table? ").lower().strip()
            if choice == "u":
                try:
                    index = int(input("Enter table number to use: "))
                    table_name = tables[index - 1]
                    break
                except (ValueError, IndexError):
                    print("Invalid choice. Try again.")
            elif choice == "c":
                table_name = create_new_table(conn)
                break
            else:
                print("Please enter 'u' or 'c'.")

    conn.close()

    # --- Main menu ---
    while True:
        print("\n--- Main Menu ---")
        print("1. Add Record")
        print("2. View Records")
        print("3. Update Record")
        print("4. Delete Record")
        print("5. Delete Table")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            add_record(table_name)
        elif choice == "2":
            show_records(table_name)
        elif choice == "3":
            update_record(table_name)
        elif choice == "4":
            delete_record(table_name)
        elif choice == "5":
            delete_table()
        elif choice == "6":
            print("Exiting program... Goodbye!")
            break
        else:
            print("Invalid choice! Try again.")

if __name__ == "__main__":
    main()
