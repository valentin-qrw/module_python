from models.base_model import BaseModelMeta

def switch_database(model_name, db_name):
    """
    Переключає базу даних для заданої моделі.
    :param model_name: Назва моделі.
    :param db_name: Назва цільової бази даних.
    :return: Повідомлення про успішне переключення або помилку.
    """
    model_class = BaseModelMeta.registry.get(model_name)

    if not model_class:
        return {"error": f"Model '{model_name}' not found"}

    try:
        model_class.use_db(db_name)
        return {"switched": True, "model": model_name, "db": db_name}
    except ValueError as e:
        return {"error": str(e)}