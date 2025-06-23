import httpx
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import Config

# Конфигурация
BOT_TOKEN = Config.TOKEN
API_URL = "http://192.168.0.104:8000"
ADMINS = [int(i) for i in Config.ADMINS.split(",")]
NOTIFY_BEFORE = 3  # Уведомлять за 3 позиции до очереди

# Инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class UserStates(StatesGroup):
    waiting_for_queue_id = State()  # Состояние ожидания ввода queue_id


# Хранилище данных
user_data = {}  # {chat_id: {"queue_id": int, "name": str}}


# Клавиатуры
def get_main_keyboard(is_admin=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["/position", "/leave"]
    if is_admin:
        buttons.extend(["/list", "/next"])
    markup.add(*buttons)
    return markup


# API клиент
async def api_request(method: str, endpoint: str, data=None):
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(f"{API_URL}{endpoint}")
            elif method == "POST":
                response = await client.post(f"{API_URL}{endpoint}", json=data)
            return response.json()
        except httpx.RequestError:
            return None


# Обработчики команд
@dp.message_handler(commands=['start'], state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await message.answer(
            "👋 Привет, админ! Доступные команды:\n"
            "/list - вся очередь\n"
            "/next - вызов следующего",
            reply_markup=get_main_keyboard(is_admin=True)
        )
        await state.finish()
        return

    # Проверяем, есть ли у пользователя сохраненный queue_id
    if message.from_user.id in user_data:
        await message.answer(
            "Вы уже находитесь в очереди!\n"
            "Используйте /position для проверки",
            reply_markup=get_main_keyboard()
        )
        return

    # Если пользователь новый, просим ввести queue_id
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Для подключения введите ваш номер (user_id):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await UserStates.waiting_for_queue_id.set()


@dp.message_handler(state=UserStates.waiting_for_queue_id)
async def process_queue_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Номер должен быть числом. Попробуйте еще:")
        return

    queue_id = int(message.text)
    response = await api_request("GET", f"/status/{queue_id}")

    if not response or "position" not in response:
        await message.answer("❌ Номер не найден в очереди. Попробуйте еще:")
        return

    # Сохраняем данные пользователя
    user_data[message.from_user.id] = {"queue_id": queue_id}

    await message.answer(
        f"✅ Вы успешно подключены!\n"
        f"Ваша текущая позиция: {response['position']}",
        reply_markup=get_main_keyboard()
    )
    await state.finish()


@dp.message_handler(commands=['position'])
async def cmd_position(message: types.Message):
    if message.from_user.id not in user_data:
        await message.answer("❌ Сначала введите /start для полключения")
        return

    queue_id = user_data[message.from_user.id]["queue_id"]
    response = await api_request("GET", f"/status/{queue_id}")

    if not response or "position" not in response:
        await message.answer("❌ Ошибка при проверке очереди")
        return

    position = response["position"]
    if position == 1:
        status = "Сейчас ваша очередь!"
    elif position <= NOTIFY_BEFORE:
        status = "Ваша очередь скоро подойдёт!"

    await message.answer(
        f"📍 Ваша позиция: {position}\n"
        f"{status}",
        reply_markup=get_main_keyboard(is_admin=message.from_user.id in ADMINS)
    )


@dp.message_handler(commands=['leave'])
async def cmd_leave(message: types.Message):
    if message.from_user.id not in user_data:
        await message.answer("❌ Вы не в очереди")
        return

    queue_id = user_data[message.from_user.id]["queue_id"]
    response = await api_request("POST", f"/leave/{queue_id}", {})

    if response and "success" in response:
        del user_data[message.from_user.id]
        await message.answer("✅ Вы вышли из очереди", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("❌ Ошибка при выходе из очереди")


@dp.message_handler(commands=['list'])
async def cmd_list(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("❌ Эта команда доступна только администраторам")
        return

    response = await api_request("GET", "/queue")
    if not response or "queue" not in response:
        await message.answer("❌ Ошибка при получении очереди")
        return

    queue_list = []
    for index, user in enumerate(response["queue"]):
        queue_list.append(f"{index + 1}. {user['name']} (ID: {user['user_id']})")

    await message.answer(
        "📋 Текущая очередь:\n" + "\n".join(queue_list))


@dp.message_handler(commands=['next'])
async def cmd_next(message: types.Message):
    # Проверяем права администратора
    if message.from_user.id not in ADMINS:
        await message.answer("❌ Эта команда доступна только администраторам")
        return

    # Получаем следующего пользователя из очереди через API
    response = await api_request("GET", "/next")

    if not response or "user_id" not in response:
        await message.answer("❌ Очередь пуста или произошла ошибка")
        return

    # Формируем сообщение для администратора
    admin_msg = (
        f"✅ Следующий пользователь:\n"
        f"🔢 Номер в очереди: {response['user_id']}\n"
        f"👤 Имя: {response['name']}"
    )

    # Удаляем пользователя из локального хранилища, если он был зарегистрирован в боте
    for chat_id, data in list(user_data.items()):
        if data["queue_id"] == response["user_id"]:
            try:
                # Отправляем уведомление пользователю
                await bot.send_message(
                    chat_id,
                    "🎉 Ваша очередь подошла! Пожалуйста, подойдите к стойке."
                )
                del user_data[chat_id]  # Удаляем из отслеживания
            except:
                # Если пользователь заблокировал бота, просто удаляем
                del user_data[chat_id]
            break

    await message.answer(admin_msg, reply_markup=get_main_keyboard(is_admin=True))

# Периодическая проверка очереди
async def check_queue_and_notify():
    for chat_id, data in user_data.items():
        queue_id = data["queue_id"]
        response = await api_request("GET", f"/status/{queue_id}")

        if not response or "position" not in response:
            continue

        position = response["position"]
        if 1 < position <= NOTIFY_BEFORE + 1:
            try:
                await bot.send_message(
                    chat_id,
                    f"🔔 Ваша очередь приближается! Вы на позиции: {position}.",
                    reply_markup=get_main_keyboard(is_admin=chat_id in ADMINS)
                )
            except:
                del user_data[chat_id]  # Удаляем если пользователь заблокировал бота


async def scheduler():
    while True:
        await check_queue_and_notify()
        await asyncio.sleep(30)  # Проверяем каждые 30 секунд


async def on_startup(dp):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
