from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from base import get_link

download = InlineKeyboardBuilder().row(
    types.InlineKeyboardButton(text='✅ СКАЧАТЬ OURS', callback_data='download')
)
regions = InlineKeyboardBuilder().row(
    types.InlineKeyboardButton(text='Калифорния', callback_data='Калифорния'),
    types.InlineKeyboardButton(text='Флорида', callback_data='Флорида'),
    types.InlineKeyboardButton(text='Нью-Йорк', callback_data='Нью-Йорк'),
    types.InlineKeyboardButton(text='Иллинойс', callback_data='Иллинойс'),
    types.InlineKeyboardButton(text='Нью-Джерси', callback_data='Нью-Джерси'),
    width=1
)

without_b = [
    [types.KeyboardButton(text='🔥 Платная публикация поста')],
    [types.KeyboardButton(text='👩‍🚀 Поддержка'),
     types.KeyboardButton(text='Опубликовать пост бесплатно')]
]
with_b = [
    [types.KeyboardButton(text='Редактирование поста')],
    [types.KeyboardButton(text='👩‍🚀 Поддержка'),
     types.KeyboardButton(text='Опубликовать пост бесплатно')],
]
actions_with = types.ReplyKeyboardMarkup(keyboard=with_b, resize_keyboard=True)
actions_without = types.ReplyKeyboardMarkup(keyboard=without_b, resize_keyboard=True)
back = InlineKeyboardBuilder().row(
    types.InlineKeyboardButton(text='Назад', callback_data='go_back')
)

i_pay = InlineKeyboardBuilder().row(
    types.InlineKeyboardButton(text='Я ОПЛАТИЛ', callback_data='i_pay')
)

added_free_post = InlineKeyboardBuilder().row(
    types.InlineKeyboardButton(text='Опубликовать бесплатно', callback_data='free_post')
)
order = InlineKeyboardBuilder().row(
    types.InlineKeyboardButton(text='Подписка оформлена!', callback_data='ok_order'),
)
verify = InlineKeyboardBuilder().row(
    types.InlineKeyboardButton(text='Пройти верификацию', callback_data='go_verify'),
    types.InlineKeyboardButton(text='Оформить подписку', callback_data='order'),
    width=1
)
oper_accept = InlineKeyboardBuilder().row(
    types.InlineKeyboardButton(text='Одобрить', callback_data='ok_verify'),
    types.InlineKeyboardButton(text='Отклонить', callback_data='no_verify'),
    width=1
)
truck_pay = InlineKeyboardBuilder().row(
    types.InlineKeyboardButton(text='Добавить траковый бизнес', callback_data='ok_truck'),
    types.InlineKeyboardButton(text='Без тракового бизнеса', callback_data='no_truck'),
    width=1
)

edit_post = InlineKeyboardBuilder().row(
    types.InlineKeyboardButton(text='Изменить текст', callback_data='edit_text'),
    types.InlineKeyboardButton(text='Изменить изображение', callback_data='edit_media'),
    types.InlineKeyboardButton(text='Назад', callback_data='back'),
    width=1
)
operator = InlineKeyboardBuilder().row(
    types.InlineKeyboardButton(text='Выдать подписку', callback_data='set_sub'),
    types.InlineKeyboardButton(text='Забрать подписку', callback_data='rem_sub'),
    types.InlineKeyboardButton(text='Сообщение подписчикам', callback_data='message_for'),
    width=1
)

kb = [
    [types.KeyboardButton(text="Закрыть чат")]
]
close_chat = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)


async def create_buttons(names):
    buttons = InlineKeyboardBuilder()
    for name in names:
        buttons.row(types.InlineKeyboardButton(text=name, callback_data=f'{await get_link(name)}'))
    else:
        buttons.row(types.InlineKeyboardButton(text='Дальнобойщики в США 🚛', callback_data='@ours_group_trucks'))
        return buttons.as_markup()


async def create_oper_but(chat):
    oper_pay = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text='Одобрить', callback_data=f'ok_pay_{chat}'),
        types.InlineKeyboardButton(text='Отклонить', callback_data=f'no_pay_{chat}'),
        width=1
    )
    return oper_pay.as_markup()
