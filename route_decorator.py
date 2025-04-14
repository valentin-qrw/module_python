# route_decorator.py
route_registry = {}

def route(path):
    """Декоратор для реєстрації маршрутів."""
    def decorator(func):
        route_registry[path] = func
        return func
    return decorator

def handle_request(path, **kwargs):
    """Обробляє запити до зареєстрованих маршрутів."""
    if path in route_registry:
        return route_registry[path](**kwargs)
    return {"error": "Route not found"}
