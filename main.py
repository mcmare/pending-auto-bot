import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatJoinRequest
from aiogram.exceptions import TelegramForbiddenError, TelegramUnauthorizedError, TelegramAPIError
import logging

# Настройка логирования с сообщениями на русском языке
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Инициализация бота
API_TOKEN = 'TOKEN'  # Замените на ваш токен
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Словарь для хранения времени поступления заявок
pending_requests = {}


@dp.chat_join_request()
async def handle_join_request(join_request: ChatJoinRequest):
    user_id = join_request.from_user.id
    chat_id = join_request.chat.id

    # Сохраняем время поступления заявки
    pending_requests[(user_id, chat_id)] = asyncio.get_event_loop().time()

    # Запускаем задачу с задержкой
    await asyncio.sleep(600)  # 10 минут = 600 секунд

    # Проверяем, что заявка все еще в ожидании
    if (user_id, chat_id) in pending_requests:
        try:
            # Подтверждаем заявку
            await join_request.approve()
            logger.info(f"Заявка на вступление одобрена для пользователя {user_id} в чате {chat_id}")

            # Удаляем заявку из списка ожидающих
            del pending_requests[(user_id, chat_id)]

            # Проверяем возможность отправки сообщения пользователю
            try:
                # Проверка, доступен ли пользователь
                await bot.get_chat(user_id)
                # Отправляем личное приветственное сообщение
                await bot.send_message(
                    chat_id=user_id,
                    text="Добро пожаловать в канал! Ваша заявка одобрена."
                )
                logger.info(f"Отправлено приветственное сообщение пользователю {user_id}")
            except (TelegramForbiddenError, TelegramUnauthorizedError, TelegramAPIError) as e:
                logger.warning(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

        except Exception as e:
            logger.error(f"Ошибка при одобрении заявки: {e}")
            # Удаляем заявку в случае ошибки
            if (user_id, chat_id) in pending_requests:
                del pending_requests[(user_id, chat_id)]


async def on_startup():
    logger.info("Бот запускается...")


async def main():
    # Регистрируем обработчики
    dp.startup.register(on_startup)
    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
