from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram_dialog import DialogManager, StartMode
from bot.states.states import StartSG, FeedbackSG
from bot.db.requests import add_user
from sqlalchemy.ext.asyncio import AsyncSession


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


@commands_router.message(Command("feedback"))
async def process_feedback_command(
    message: Message,
    dialog_manager: DialogManager,
) -> None:
    await message.delete()
    await dialog_manager.start(FeedbackSG.start, mode=StartMode.NORMAL)
