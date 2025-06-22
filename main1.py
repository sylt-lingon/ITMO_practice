from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from queue_manager import QueueManager  # Импорт класса очереди

app = FastAPI(title="Queue API for Robot")
queue = QueueManager()  # Инициализация менеджера очереди


# Модели запросов/ответов
class UserRequest(BaseModel):
    name: str  # Пользователь вводит имя на экране робота


class UserResponse(BaseModel):
    user_id: int
    position: int


# Эндпоинты
@app.post("/join", response_model=UserResponse, summary="Добавить пользователя в очередь")
async def join_queue(request: UserRequest):
    """Добавляет пользователя в очередь и возвращает его номер"""
    try:
        user = queue.add_user(request.name)
        position = queue.get_position(user.id)
        return {
            "user_id": user.id,
            "position": position
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/leave/{user_id}", summary="Покинуть очередь")
async def leave_queue(user_id: int):
    """Удаление из очереди"""
    success = queue.remove_user(user_id)
    return {"success": success}


@app.get("/status/{user_id}", summary="Проверить позицию в очереди")
async def get_status(user_id: int):
    """Возвращает текущую позицию пользователя"""
    position = queue.get_position(user_id)
    if not position:
        raise HTTPException(status_code=404, detail="User not found")
    return {"position": position}


@app.get("/next", summary="Получить следующего пользователя")
async def get_next():
    """Удаляет первого в очереди и возвращает его данные"""
    user = queue.get_next()
    if not user:
        raise HTTPException(status_code=404, detail="Queue is empty")
    return {"user_id": user.id, "name": user.name}


@app.get("/queue", summary="Получить всю очередь")
async def get_queue():
    """Возвращает список всех user_id"""
    return {"queue": queue.get_all_users()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
