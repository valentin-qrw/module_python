from controllers.user_controller import create_user, get_user, update_user, delete_user
from controllers.database_controller import switch_database
from route_decorator import handle_request, route

from database.database import Database
from database.registry import DatabaseRegistry


# === Ініціалізація баз даних ===

default_db = Database("default")
DatabaseRegistry.register("default", default_db)

test_db = Database("test")
DatabaseRegistry.register("test", test_db)


# === Роутинги ===

@route("/users/create")
def route_create_user(data):
    return create_user(data)


@route("/users/get")
def route_get_user(user_id):
    return get_user(user_id)


@route("/users/update")
def route_update_user(user_id, data):
    return update_user(user_id, data)


@route("/users/delete")
def route_delete_user(user_id):
    return delete_user(user_id)


@route("/database/switch")
def route_switch_database(model_name, db_name):
    return switch_database(model_name, db_name)


# === Основна логіка ===

def main():
    from models.base_model import User

    # --- Робота з default базою ---
    User.use_db("default")
    print("=== Default Database ===")
    print(handle_request("/users/create", data={"name": "Alice", "email": "alice@example.com"}))
    print(handle_request("/users/create", data={"name": "Bob", "email": "bob@example.com"}))
    print(handle_request("/users/get", user_id=1))

    # --- Перехід на test базу ---
    print("\n=== Switching to test database ===")
    print(handle_request("/database/switch", model_name="User", db_name="test"))

    print("\n=== Creating user in test database ===")
    print(handle_request("/users/create", data={"name": "Charlie", "email": "charlie@example.com"}))

    # --- Перевірка читання з різних БД ---
    print("\n=== Getting users from different databases ===")
    User.use_db("default")
    print("Default DB:", handle_request("/users/get", user_id=1))
    User.use_db("test")
    print("Test DB:", handle_request("/users/get", user_id=1))

    # --- Оновлення / Видалення у test ---
    print("\n=== Updating user in test DB ===")
    print(handle_request("/users/update", user_id=1, data={"name": "Charlie Updated"}))

    print("\n=== Deleting user in test DB ===")
    print(handle_request("/users/delete", user_id=1))

    # --- One-to-many: Director → Movies ---
    print("\n=== One-to-Many: Director -> Movies ===")
    default_db = DatabaseRegistry.get("default")
    director = default_db.create("Director", {"name": "Christopher Nolan"})
    default_db.create("Movie", {"title": "Inception", "director_id": director["id"]})
    default_db.create("Movie", {"title": "Interstellar", "director_id": director["id"]})
    movies = default_db.get_related_many("Director", "Movie", "director_id", director["id"])
    print(f"Movies by {director['name']}:", movies)

    # --- Many-to-many: Students <-> Courses ---
    print("\n=== Many-to-Many: Student <-> Course ===")
    student1 = default_db.create("Student", {"name": "Anna"})
    student2 = default_db.create("Student", {"name": "Mark"})
    course1 = default_db.create("Course", {"title": "Math"})
    course2 = default_db.create("Course", {"title": "Physics"})

    # Створимо зв’язки
    default_db.add_many_to_many_relation("Enrollment", student1["id"], course1["id"])
    default_db.add_many_to_many_relation("Enrollment", student1["id"], course2["id"])
    default_db.add_many_to_many_relation("Enrollment", student2["id"], course1["id"])

    # Отримаємо курси для Anna
    anna_courses = default_db.get_many_to_many_related("Enrollment", "from_id", "to_id", student1["id"], "Course")
    print(f"{student1['name']} is enrolled in:", anna_courses)

    # --- Транзакції: commit і rollback ---
    print("\n=== Transactions ===")
    try:
        with default_db:
            default_db.create("Log", {"message": "Start critical operation"})
            raise Exception("Something went wrong")
            default_db.create("Log", {"message": "Operation succeeded"})
    except:
        print("Error caught!")

    print("Logs after rollback:", default_db.tables.get("Log", []).rows if "Log" in default_db.tables else [])

    print("\nTrying again with successful transaction:")
    with default_db:
        default_db.create("Log", {"message": "All good now!"})
    print("Logs after commit:", [r.data for r in default_db.tables["Log"].rows])


if __name__ == "__main__":
    main()
