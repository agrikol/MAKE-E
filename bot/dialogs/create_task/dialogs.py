from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Row, Cancel, SwitchTo, Calendar, Button
from bot.states.states import CreateTaskSG
from bot.dialogs.create_task.getters import get_name
from bot.dialogs.create_task.handlers import (
    add_desc_handler,
    add_name_handler,
    add_category,
)


create_task_dialog = Dialog(
    Window(
        Format(
            "Создана задача с именем: <code>{name}</code>\
            \nОписание: {desc}\nКатегория: {categ}\nСрок: {due}\
            \nУведомления: {notice}"
        ),
        Row(
            SwitchTo(Const("Имя"), id="name", state=CreateTaskSG.name),
            SwitchTo(Const("Описание"), id="desc", state=CreateTaskSG.desc),
        ),
        Row(
            SwitchTo(Const("Категория"), id="categ", state=CreateTaskSG.categ),
            SwitchTo(Const("Срок"), id="due", state=CreateTaskSG.due),
        ),
        SwitchTo(Const("Напоминание"), id="notice", state=CreateTaskSG.notice),
        SwitchTo(Const("Сохранить задачу"), id="save", state=CreateTaskSG.save),
        Cancel(Const("« Назад"), id="calcel"),
        state=CreateTaskSG.start,
        getter=get_name,
    ),
    Window(
        Const("Введите имя задачи"),
        TextInput(
            id="add_name",
            on_success=add_name_handler,
        ),
        state=CreateTaskSG.name,
    ),
    Window(
        Const("Введите описание задачи"),
        TextInput(id="add_desc", on_success=add_desc_handler),
        state=CreateTaskSG.desc,
    ),
    Window(
        Const("Выберите дату"),
        Calendar(id="date", on_click=lambda x: x),
        state=CreateTaskSG.due,
    ),
    Window(
        Const("Выберите категорию"),
        Row(
            SwitchTo(
                Const("🔴 Красная"),
                id="category_1",
                state=CreateTaskSG.start,
                on_click=add_category,
            ),
            SwitchTo(
                Const("🟡 Желтая"),
                id="category_2",
                state=CreateTaskSG.start,
                on_click=add_category,
            ),
        ),
        Row(
            SwitchTo(
                Const("🟢 Зеленая"),
                id="category_3",
                state=CreateTaskSG.start,
                on_click=add_category,
            ),
            SwitchTo(
                Const("🔵 Синяя"),
                id="category_4",
                state=CreateTaskSG.start,
                on_click=add_category,
            ),
        ),
        SwitchTo(Const("« Назад"), id="cancel", state=CreateTaskSG.start),
        state=CreateTaskSG.categ,
    ),
)
