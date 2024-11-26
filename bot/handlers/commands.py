from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.filters import CommandStart, Command
from aiogram_dialog import DialogManager, StartMode
from bot.states.states import StartSG, FeedbackSG, NoticeEditSG
from bot.db.requests import add_user, add_user_timezone, get_task_info, get_task_notice
from sqlalchemy.ext.asyncio import AsyncSession
from timezonefinder import TimezoneFinder
from bot.db.models import Task
from bot.service.delay_services.publisher import publish_delay
from datetime import datetime, timedelta
from nats.js.client import JetStreamContext


commands_router: Router = Router()


@commands_router.message(CommandStart())
async def process_start_command(
    message: Message,
    dialog_manager: DialogManager,
    session: AsyncSession,
) -> None:
    await add_user(
        session,
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username,
        message.from_user.last_name,
    )
    await dialog_manager.start(StartSG.start, mode=StartMode.RESET_STACK)


@commands_router.callback_query(F.data.startswith("notice:edit:"))
async def process_edit_notice(callback: CallbackQuery, dialog_manager: DialogManager):
    session: AsyncSession = dialog_manager.middleware_data.get("session")
    task_id = int(callback.data.split(":")[-1])
    task: Task = await get_task_info(session, task_id)
    task: dict = task.to_dict()
    task["notice"] = None
    await dialog_manager.start(
        NoticeEditSG.start,
        data={**task, "task_id": task_id},
        mode=StartMode.NORMAL,
    )


@commands_router.message(F.data.startswith("notice:tomorrow:"))
async def process_tomorrow_notice(
    callback: CallbackQuery, dialog_manager: DialogManager
):
    session: AsyncSession = dialog_manager.middleware_data.get("session")
    js: JetStreamContext = dialog_manager.middleware_data.get("js")
    subject: str = dialog_manager.middleware_data.get("delay_del_subject")

    task_id = int(callback.data.split(":")[-1])
    notice_time = await get_task_notice(session, task_id)
    user_id = callback.from_user.id
    delay: datetime = notice_time + timedelta(days=1)
    await publish_delay(
        js=js,
        session=session,
        user_id=user_id,
        task_id=task_id,
        subject=subject,
        delay=delay,
    )

    await callback.message.delete()
    await callback.answer("Перенесено на завтра")


@commands_router.message(F.data.startswith("notice:delete:"))
async def process_delete_notice(callback: CallbackQuery, dialog_manager: DialogManager):
    await callback.message.delete()


@commands_router.message(Command("feedback"))
async def process_feedback_command(
    message: Message,
    dialog_manager: DialogManager,
) -> None:
    await message.delete()
    await dialog_manager.start(FeedbackSG.start, mode=StartMode.NORMAL)


@commands_router.message(Command("timezone"))
async def process_location_command(message: Message) -> None:
    location_btn = KeyboardButton(text="📍 Указать часовой пояс", request_location=True)
    cancel_btn = KeyboardButton(text="❌ Отмена")
    keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=[[location_btn], [cancel_btn]], resize_keyboard=True
    )
    await message.answer(
        "Нажмите на кнопку 📍. Бот не хранит ваше местоположение и "
        "использует его один раз только для определения часового пояса",
        reply_markup=keyboard,
    )


@commands_router.message(F.location)
async def process_location(message: Message, session: AsyncSession) -> None:
    # TODO: Refactor this
    await message.delete()
    tf = TimezoneFinder()
    timezone = tf.timezone_at(
        lng=message.location.longitude, lat=message.location.latitude
    )
    await add_user_timezone(session, message.from_user.id, timezone)
    await message.answer(
        f"📍 Ваш часовой пояс: {timezone}",
        reply_markup=ReplyKeyboardRemove(),
    )


@commands_router.message(F.text == "Отмена")
async def process_cancel(message: Message, dialog_manager: DialogManager) -> None:
    # TODO: Refactor this
    await message.delete()
    await message.answer(
        "📍 Вы сможете установить /timezone в следующий раз",
        reply_markup=ReplyKeyboardRemove(),
    )
    await dialog_manager.start(StartSG.start, mode=StartMode.RESET_STACK)
