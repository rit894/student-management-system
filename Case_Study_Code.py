import os, math

STUDENTS = []
DEPT_GRAPH = {
    "CSE": ["AIML", "ECE"],
    "ECE": ["EEE"],
    "EEE": ["CSE"],
    "MECH": ["CIVIL"],
    "CIVIL": [],
    "AIML": []
}
VALID_DEPTS = set(DEPT_GRAPH.keys())
DATA_FILE = "students_data.txt"

# -------------------------------
# Validation & Core Flow
# -------------------------------
def format_student_id(roll):
    return roll.strip().upper()

def clean_input_text(s):
    return "".join(ch for ch in s if ch.isalnum() or ch in (" ", "-", "_")).strip()

def validate_student_record(name, roll, dept, year):
    if not (name and roll and dept and year):
        return "All fields required."
    if not year.isdigit() or not (1 <= int(year) <= 5):
        return "Year must be 1-5."
    if dept not in VALID_DEPTS:
        return "Unknown department."
    if len(roll) < 6 or not any(ch.isdigit() for ch in roll):
        return "Invalid roll."
    return None

def show_main_menu():
    print("\n===== Campus Resource Management System =====")
    print("1. Add Student")
    print("2. View Students")
    print("3. Search Student")
    print("4. Sort Students")
    print("5. Update Student")
    print("6. Delete Student")
    print("7. Summaries")
    print("8. Recursion Demos")
    print("9. Save/Load")
    print("10. Exit")

# -------------------------------
# Data Abstraction & Summaries
# -------------------------------
def generate_student_statistics(records):
    return {
        "total": len(records),
        "unique_departments": {s["dept"] for s in records},
        "year_count": {
            s["year"]: sum(1 for x in records if x["year"] == s["year"])
            for s in records
        }
    }

def display_statistics(summary):
    print("\n--- Summaries ---")
    print("Total:", summary["total"])
    print("Departments:", summary["unique_departments"])
    print("Year-wise count:", summary["year_count"])

# -------------------------------
# Algorithms (Search, Sort, Recursion)
# -------------------------------
def find_student_linear(records, roll):
    roll = format_student_id(roll)
    for s in records:
        if s["roll"] == roll:
            return s
    return None

def sort_students_merge(records, key):
    if len(records) <= 1:
        return records
    mid = len(records) // 2
    left = sort_students_merge(records[:mid], key)
    right = sort_students_merge(records[mid:], key)
    return merge_sorted_lists(left, right, key)

def merge_sorted_lists(left, right, key):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i][key] <= right[j][key]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result + left[i:] + right[j:]

def find_student_binary(sorted_records, roll):
    roll = format_student_id(roll)
    low, high = 0, len(sorted_records) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_roll = sorted_records[mid]["roll"]
        if mid_roll == roll:
            return sorted_records[mid]
        elif mid_roll < roll:
            low = mid + 1
        else:
            high = mid - 1
    return None

def calculate_factorial_recursive(n):
    return 1 if n <= 1 else n * calculate_factorial_recursive(n - 1)

def calculate_factorial_iterative(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def find_department_path_recursive(graph, start, target, visited=None):
    if visited is None:
        visited = set()
    if start == target:
        return [start]
    visited.add(start)
    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            path = find_department_path_recursive(graph, neighbor, target, visited)
            if path:
                return [start] + path
    return None

# -------------------------------
# File I/O
# -------------------------------
def export_students_to_file(filename=DATA_FILE):
    with open(filename, "w") as f:
        for s in STUDENTS:
            f.write(f"{s['name']},{s['roll']},{s['dept']},{s['year']}\n")
    print("Saved", len(STUDENTS), "records.")

def import_students_from_file(filename=DATA_FILE):
    if not os.path.exists(filename):
        print("No file found to load.")
        return
    loaded = 0
    with open(filename) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 4:
                n, r, d, y = parts
                rid = format_student_id(r)
                if not any(s["roll"] == rid for s in STUDENTS):
                    STUDENTS.append({
                        "name": n,
                        "roll": rid,
                        "dept": d.upper(),
                        "year": y
                    })
                    loaded += 1
    print("Loaded", loaded, "new records. Total:", len(STUDENTS))

# -------------------------------
# CRUD Flows
# -------------------------------
def add_student_record():
    n = clean_input_text(input("Name: "))
    r = format_student_id(input("Roll: "))
    d = clean_input_text(input("Dept: ")).upper()
    y = input("Year (1-5): ").strip()
    e = validate_student_record(n, r, d, y)
    if e:
        print("Error:", e); return
    if any(s["roll"] == r for s in STUDENTS):
        print("Duplicate roll."); return
    STUDENTS.append({"name": n, "roll": r, "dept": d, "year": y})
    print("Added.")

def list_all_students():
    if not STUDENTS:
        print("No records."); return
    for i, s in enumerate(sort_students_merge(STUDENTS, "roll"), 1):
        print(f"{i}. {s['name']} | {s['roll']} | {s['dept']} | Year {s['year']}")

def search_student_record():
    r = input("Roll: ")
    m = input("Method (linear/binary): ").strip().lower()
    if m == "linear":
        print(find_student_linear(STUDENTS, r))
    else:
        print(find_student_binary(sort_students_merge(STUDENTS, "roll"), r))

def update_student_record():
    r = format_student_id(input("Existing roll: "))
    s = next((x for x in STUDENTS if x["roll"] == r), None)
    if not s:
        print("Not found."); return
    new_name = clean_input_text(input("New name (blank=keep): "))
    new_dept = clean_input_text(input("New dept (blank=keep): ")).upper()
    new_year = input("New year (blank=keep): ").strip()
    s["name"] = s["name"] if new_name == "" else new_name
    s["dept"] = s["dept"] if new_dept == "" else new_dept
    s["year"] = s["year"] if new_year == "" else new_year
    e = validate_student_record(s["name"], s["roll"], s["dept"], s["year"])
    if e:
        print("Error:", e); return
    print("Updated.")

def delete_student_record():
    r = format_student_id(input("Roll to delete: "))
    for i, s in enumerate(STUDENTS):
        if s["roll"] == r:
            STUDENTS.pop(i)
            print("Deleted."); return
    print("Not found.")

# -------------------------------
# Recursion Demo
# -------------------------------
def recursion_demos():
    try:
        n = int(input("Enter n for factorial: "))
        print("Recursive:", calculate_factorial_recursive(n),
              "Iterative:", calculate_factorial_iterative(n))
    except Exception as e:
        print("Factorial error:", e)
    s = input("DFS start dept: ").strip().upper()
    t = input("DFS target dept: ").strip().upper()
    path = find_department_path_recursive(DEPT_GRAPH, s, t)
    print("DFS recursive path:", path)

# -------------------------------
# Main loop
# -------------------------------
def initialize_demo_records():
    STUDENTS.extend([
        {"name": "Keerthi", "roll": "21CSE001", "dept": "CSE", "year": "3"},
        {"name": "Rahul", "roll": "21ECE105", "dept": "ECE", "year": "2"},
        {"name": "Divya", "roll": "21EEE210", "dept": "EEE", "year": "4"}
    ])

def run_student_management_system():
    if not STUDENTS:
        initialize_demo_records()
    while True:
        show_main_menu()
        c = input("Choice: ").strip()
        if c == "1":
            add_student_record()
        elif c == "2":
            list_all_students()
        elif c == "3":
            search_student_record()
        elif c == "4":
            list_all_students()  # reuse merge sort for display
        elif c == "5":
            update_student_record()
        elif c == "6":
            delete_student_record()
        elif c == "7":
            display_statistics(generate_student_statistics(STUDENTS))
        elif c == "8":
            recursion_demos()
        elif c == "9":
            opt = input("save/load: ").strip().lower()
            if opt == "save":
                export_students_to_file()
            elif opt == "load":
                import_students_from_file()
            else:
                print("Unknown option.")
        elif c == "10":
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    run_student_management_system()