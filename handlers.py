import asyncio
import aioschedule
import datetime
from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from aiogram import F
from aiogram.utils.media_group import MediaGroupBuilder
import pytz

from base import check_sub, add_free_post, check_free, check_and_delete_free, add_post, add_subscribe, \
    check_and_publicate, edit_text_post, edit_media_post, del_subscribe, get_groups, \
    get_chats, get_chat, get_post, add_user, get_region, get_all_id, get_subs, check_truck, get_post_info, check_post
from buttons import regions, actions_with, actions_without, back, create_buttons, oper_accept, \
    order, edit_post, operator, download, added_free_post, i_pay, truck_pay, create_oper_but
from config import OPERATOR, truck
from main import bot, dp
from middlewares.album_middleware import AlbumMiddleware

router = Router()
router.message.middleware(AlbumMiddleware())


class UserInfo(StatesGroup):
    region = State()
    action = State()
    free_post_group = State()
    post_group = State()
    wait_verify = State()
    get_link = State()
    FIO = State()
    photo = State()


class Operator(StatesGroup):
    verify = State()
    menu = State()
    set_sub = State()
    rem_sub = State()
    text_message = State()
    achive_message = State()
    truck = State()


class Post(StatesGroup):
    achive = State()
    check_achive = State()
    text = State()
    username = State()
    select = State()
    view = State()
    edit_text = State()
    edit_media = State()


class verification(StatesGroup):
    no_sub = State()
    get_info = State()
    get_username = State()


class Order(StatesGroup):
    accept = State()


@router.message(Command('start'))
async def get_start(message: Message, state: FSMContext):
    if message.from_user.id == OPERATOR:
        await message.answer('Вы авторизованы как Оператор:', reply_markup=operator.as_markup())
        await state.set_state(Operator.menu)
    else:
        if await get_region(message.from_user.id):
            await state.update_data(region=await get_region(message.from_user.id),
                                    groups=await get_groups(await get_region(message.from_user.id)))
            await bot.send_photo(chat_id=message.from_user.id,
                                 photo='AgACAgIAAxkBAAIIqGXPLaRmFaXMIvChCbgbmO0BhSUiAAL60zEbkkh4SmBWQa'
                                       '-zsWZqAQADAgADeQADNAQ',
                                 caption='<b>🔥 Сейчас действует АКЦИЯ!</b>\n\n'
                                         'Скачивай приложение OURS, бесплатно размещай свои услуги'
                                         'или вакансию, '
                                         'и дальше откроется возможность оплаты рекламы <b>во всех телеграм '
                                         'группах</b> '
                                         'по твоему штату <b>3 раза в день</b> автоматически <b>со скидкой 70%</b>, '
                                         'как итог $63 за '
                                         'МЕСЯЦ.\n\n'
                                         '🤫 Да-да, одна оплата за рекламу во всех телеграм группах!',
                                 reply_markup=download.as_markup(), parse_mode='HTML')
            await bot.send_message(chat_id=message.from_user.id,
                                   text='Если у тебя Андроид 🤖 или просто предпочитаешь '
                                        'платить через Zelle БЕЗ скидки 70%, то свяжись с '
                                        'поддержкой, кнопка находится снизу.\n\n'
                                        'Эти ребята помогут тебе 🧑‍🚀',
                                   reply_markup=actions_with if await check_sub(
                                       message.from_user.username) else actions_without)
            await bot.send_message(chat_id=message.from_user.id, text='Есть возможность опубликовать рекламу '
                                                                      'бесплатно, правда 1 раз за 24 часа и только в '
                                                                      'одной телеграм группе 🙂\n\n'
                                                                      '➡️ Кстати в <a href = "https://oursusa.com/?utm_campaign=bot_ads&utm_medium=social&utm_source=ads_bot_services">OURS</a> можно добавить свои услуги бесплатно!',
                                   reply_markup=added_free_post.as_markup(), parse_mode='HTML',
                                   disable_web_page_preview=True)

        else:
            await message.bot.send_photo(chat_id=message.from_user.id,
                                         photo='AgACAgIAAxkBAAIIbGXPGjDgHSi71VsCPQWtIrTSwC53AAKg0zEbkkh4St6NB5Z5xIPFAQADAgADeQADNAQ',
                                         caption='Привет 👋\n'
                                                 'Размести свое объявление через бота OURS.\n'
                                                 'Выбери свой штат, и мы подберем для тебя лучшие телеграм группы!\n\n'
                                                 'Либо напиши в поддержку, если интересна реклама по всему США 🙌',
                                         reply_markup=regions.as_markup())
            await state.set_state(UserInfo.region)


@router.callback_query(Operator.menu)
async def work_callback(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    if call.data == 'set_sub':
        await call.bot.send_message(chat_id=call.from_user.id, text='Введите username для выдачи подписки:')
        await state.set_state(Operator.set_sub)
    elif call.data == 'rem_sub':
        await call.bot.send_message(chat_id=call.from_user.id, text='Введите username для удаления подписки:')
        await state.set_state(Operator.rem_sub)
    elif call.data == 'message_for':
        await call.bot.send_message(chat_id=call.from_user.id, text='Напишите сообщение для пользователей')
        await state.set_state(Operator.text_message)
    elif call.data == 'ok_verify':
        await call.answer('Одобрено')
        new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
        state_with: FSMContext = FSMContext(
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=new_user_storage_key)
        data = await state_with.get_data()
        await add_subscribe([data['user_ver'], data["name"]])
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=data['user_ver'], text='Ваша заявка на верификацию одобрена.\n'
                                                                   '<b>Начало создания поста:</b>\n\n'
                                                                   'Отправьте изображения или видео к вашему '
                                                                   'рекламному объявлению - до 5 штук',
                                    parse_mode='HTML')
    elif call.data == 'no_verify':
        await call.answer('Отклонено')
        new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
        state_with: FSMContext = FSMContext(
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=new_user_storage_key)
        data = await state_with.get_data()
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=data['user_ver'], text='Ваша заявка на верификацию отклонена.',
                                    reply_markup=actions_with if await check_sub(
                                        call.from_user.username) else actions_without)
    elif 'ok_pay' in str(call.data):
        chat = call.data.split('_')[2]
        await call.answer('Одобрено')
        new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
        state_with: FSMContext = FSMContext(
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=new_user_storage_key)
        data = await state_with.get_data()
        await call.bot.send_message(chat_id=call.from_user.id, text='Добавить траковый бизнес?',
                                    reply_markup=truck_pay.as_markup())
        await state.update_data(user=chat, name=data['name'], message=call.message.message_id)
        await state.set_state(Operator.truck)

    elif 'no_pay' in call.data:
        chat = call.data.split('_')[2]
        await call.answer('Отклонено')
        new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
        state_with: FSMContext = FSMContext(
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=new_user_storage_key)
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=chat, text='Упс, не смогли найти вашу Premium '
                                                       'подписку.\n\nПопробуйте ещё раз!',
                                    reply_markup=i_pay.as_markup())
        await state.set_state(Operator.menu)


@router.callback_query(Operator.truck)
async def oprator_call(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'ok_truck':
        await call.answer('Одобрено')
        await state.update_data(truck='yes')
        data = await state.get_data()
        await add_subscribe([data['user'], data["name"], data['truck']])
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        try:
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=data['message'])
        except:
            pass
        await call.bot.send_message(chat_id=data['user'], text='Проверка оплаты прошла успешно 🥳\n\n')
        await call.bot.send_message(chat_id=data['user'], text='<b>Начало создания поста:</b>\n\n'
                                                               'Отправьте изображения или видео к вашему рекламному '
                                                               'объявлению - до 5 штук', parse_mode='HTML',
                                    reply_markup=actions_with if await check_sub(
                                        call.from_user.username) else actions_without)
        await state.set_state(Operator.menu)
    elif call.data == 'no_truck':
        await state.update_data(truck='no')
        data = await state.get_data()
        await add_subscribe([data['user'], data["name"], data['truck']])
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=data['user'], text='Проверка оплаты прошла успешно 🥳\n\n')
        await call.bot.send_message(chat_id=data['user'], text='<b>Начало создания поста:</b>\n\n'
                                                               'Отправьте изображения или видео к вашему рекламному '
                                                               'объвлению - до 5 штук', parse_mode='HTML',
                                    reply_markup=actions_with if await check_sub(
                                        call.from_user.username) else actions_without)
        await state.set_state(Operator.menu)


@router.callback_query(Operator.text_message, Operator.achive_message, Operator.menu)
async def oprator_call(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'ok_verify':
        await call.answer('Одобрено')
        new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
        state_with: FSMContext = FSMContext(
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=new_user_storage_key)
        data = await state_with.get_data()
        await add_subscribe([data['user_ver'], data["name"]])
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=data['user_ver'], text='Ваша заявка на верификацию одобрена.\n'
                                                                   '<b>Начало создания поста:</b>\n\n'
                                                                   'Отправьте изображения или видео к вашему рекламному объявлению - до 5 штук',
                                    parse_mode='HTML')
        await state.set_state(Operator.menu)
    elif call.data == 'no_verify':
        await call.answer('Отклонено')
        new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
        state_with: FSMContext = FSMContext(
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=new_user_storage_key)
        data = await state_with.get_data()
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=data['user_ver'], text='Ваша заявка на верификацию отклонена.',
                                    reply_markup=actions_with if await check_sub(
                                        call.from_user.username) else actions_without)
        await state.set_state(Operator.menu)
    elif 'ok_pay' in str(call.data):
        chat = call.data.split('_')[2]
        await call.answer('Одобрено')
        new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
        state_with: FSMContext = FSMContext(
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=new_user_storage_key)
        data = await state_with.get_data()
        await call.bot.send_message(chat_id=call.from_user.id, text='Добавить траковый бизнес?',
                                    reply_markup=truck_pay.as_markup())
        await state.update_data(user=chat, name=data['name'])
        await state.set_state(Operator.truck)
    elif 'no_pay' in str(call.data):
        chat = call.data.split('_')[2]
        await call.answer('Отклонено')
        new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
        state_with: FSMContext = FSMContext(
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=new_user_storage_key)
        data = await state_with.get_data()
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=chat, text='Упс, не смогли найти вашу Premium '
                                                       'подписку.\n\nПопробуйте ещё раз!',
                                    reply_markup=i_pay.as_markup())
        await state.set_state(Operator.menu)


@router.message(Operator.text_message)
async def operator_text(message: types.Message, state: FSMContext):
    await state.update_data(message_text=message.html_text)
    await message.answer('Хорошо, теперь прикрепите вложения:')
    await state.set_state(Operator.achive_message)


@router.message(Operator.achive_message)
async def operator_achive(message: types.Message, state: FSMContext, album: list = None):
    await state.update_data(photo_message=[], video_message=[])
    data = await state.get_data()
    if album:
        if len(album) > 5:
            await message.answer('Нельзя прикрепить больше 5 вложений\n'
                                 'Попробуйте снова.')
        else:
            for i in album:
                if 'Video' in str(i):
                    pre = str(i).split('Video')[1]
                    pre = pre.split('file_unique_id')[0]
                    pre = pre.replace('(', '').replace('file_id=', '').replace(',', '')
                    pre = pre[1:len(pre) - 2]
                    data['video_message'].append(pre)
                elif 'photo=[PhotoSize(' in str(i):
                    pre = str(i).split('photo=[PhotoSize(')[1]
                    pre = pre.split('file_unique_id')[0]
                    pre = pre.replace('(', '').replace('file_id=', '').replace(',', '')
                    pre = pre[1:len(pre) - 2]
                    data['photo_message'].append(pre)
            else:
                data = await state.get_data()
                await send_messages(data)
                await message.answer('Ваше сообщение отправлено!', reply_markup=operator.as_markup())
                await state.set_state(Operator.menu)
    else:
        if message.photo:
            data['photo_message'].append(message.photo[-1].file_id)
        elif message.video:
            data['video_message'].append(message.video.file_id)
        data = await state.get_data()
        await send_messages(data)
        await message.answer('Ваше сообщение отправлено!', reply_markup=operator.as_markup())
        await state.set_state(Operator.menu)


@router.message(Operator.set_sub)
async def new_sub(message: types.Message, state: FSMContext):
    answer = message.text
    data = ['-', answer]
    await add_subscribe(data)
    await message.answer('По введенному вами username была выдана подписка.', reply_markup=operator.as_markup())
    await state.set_state(Operator.menu)


@router.message(Operator.rem_sub)
async def del_sub(message: types.Message, state: FSMContext):
    answer = message.text
    await del_subscribe(answer)
    await message.answer('По введенному вами username была удалена подписка.', reply_markup=operator.as_markup())
    await state.set_state(Operator.menu)


@router.callback_query(UserInfo.region)
async def work_callback(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    if call.data in ['Калифорния', 'Флорида', 'Нью-Йорк', 'Иллинойс', 'Нью-Джерси']:
        await add_user([call.from_user.id, call.from_user.username, 'no', call.data, '-', '-'])
        await state.set_state(None)
        groups = await get_groups(str(call.data))
        stroke = ''
        i = 1
        for reg in groups:
            stroke += f'<b>{i}.{reg}</b>\n\n'
            i += 1
        else:
            stroke += f'<b>{i}.Дальнобойщики в США 🚛*</b>\n\n' \
                      '*только для тракового бизнеса'
        await state.update_data(region=call.data, groups=groups)
        await call.bot.send_message(chat_id=call.from_user.id,
                                    text=f'Спасибо, остался последний шаг. У нас есть разная подборка групп для тебя '
                                         f'👇\n\n'
                                         f'{stroke}', parse_mode='HTML', reply_markup=actions_with if await check_sub(
                call.from_user.username) else actions_without)
        await asyncio.sleep(1)
        await call.bot.send_photo(chat_id=call.from_user.id,
                                  photo='AgACAgIAAxkBAAIIqGXPLaRmFaXMIvChCbgbmO0BhSUiAAL60zEbkkh4SmBWQa'
                                        '-zsWZqAQADAgADeQADNAQ',
                                  caption='<b>🔥 Сейчас действует АКЦИЯ!</b>\n\n'
                                          'Скачивай приложение OURS, бесплатно размещай свои услуги'
                                          'или вакансию, '
                                          'и дальше откроется возможность оплаты рекламы <b>во всех телеграм '
                                          'группах</b> '
                                          'по твоему штату <b>3 раза в день</b> автоматически <b>со скидкой 70%</b>, '
                                          'как итог $63 за '
                                          'МЕСЯЦ.\n\n'
                                          '🤫 Да-да, одна оплата за рекламу во всех телеграм группах!',
                                  reply_markup=download.as_markup(), parse_mode='HTML')
        await call.bot.send_message(chat_id=call.from_user.id, text='Если у тебя Андроид 🤖 или просто предпочитаешь '
                                                                    'платить через Zelle БЕЗ скидки 70%, то свяжись с '
                                                                    'поддержкой, кнопка находится снизу.\n\n'
                                                                    'Эти ребята помогут тебе 🧑‍🚀',
                                    reply_markup=actions_with if await check_sub(
                                        call.from_user.username) else actions_without)
        await call.bot.send_message(chat_id=call.from_user.id, text='Есть возможность опубликовать рекламу бесплатно, '
                                                                    'правда 1 раз за 24 часа и только в одной '
                                                                    'телеграм группе 🙂',
                                    reply_markup=added_free_post.as_markup())


@router.callback_query(StateFilter(None))
@router.callback_query(StateFilter(Operator.menu))
@router.callback_query(StateFilter(verification.no_sub))
async def work_callback(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'download':
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id + 1)
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id + 2)
        await bot.send_message(chat_id=call.from_user.id,
                               text='<b>Вот ссылка для скачивания:</b>\n\n<a '
                                    'href="https://OURSUSA.COM?utm_campaign=bot_ads&utm_medium=social&utm_source'
                                    '=ads_bot"><b>👉OURSUSA.COM</b></a>\n<a '
                                    'href="https://OURSUSA.COM?utm_campaign=bot_ads&utm_medium=social&utm_source'
                                    '=ads_bot"><b>👉OURSUSA.COM</b></a>\n<a '
                                    'href="https://OURSUSA.COM?utm_campaign=bot_ads&utm_medium=social&utm_source'
                                    '=ads_bot"><b>👉OURSUSA.COM</b></a>', parse_mode='HTML',
                               disable_web_page_preview=True)
        await asyncio.sleep(2)
        await bot.send_message(chat_id=call.from_user.id,
                               text='Нажми кнопку «<b>Я ОПЛАТИЛ</b>», если ты купил подписку Premium.',
                               reply_markup=i_pay.as_markup(), parse_mode='HTML')
        await bot.send_video(chat_id=call.from_user.id,
                             video='BAACAgIAAxkBAAILnmXRA2pYGHsSmgWr1lao5LmSRY-QAAK5RAACZKCJSjGvIDSX9DcwNAQ',
                             caption='Кстати, ты можешь посмотреть видео инструкцию на '
                                     '40 секунд, как вытащить максимум из OURS',
                             reply_markup=actions_with if await check_sub(
                                 call.from_user.username) else actions_without)
    elif call.data == 'i_pay':
        await call.answer()
        try:
            await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id + 1)
        except:
            pass
        await call.bot.send_photo(chat_id=call.from_user.id,
                                  photo='AgACAgIAAxkBAAIR6GXXX4M4pIcmONBz2WMH-232yGIKAAKd1jEbNt-5SgyMiakYnn8uAQADAgADeQADNAQ',
                                  caption='Напиши, пожалуйста, свое имя, которое ты указал в профиле OURS')
        await state.set_state(UserInfo.FIO)
    elif call.data == 'free_post':
        await call.answer()
        data = await state.get_data()
        access = await check_free((str(call.from_user.id),))
        if access is False:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id, text='Выберите группу для публикации:',
                                   reply_markup=await create_buttons(data["groups"]))
            await state.update_data(type='free')
            await state.set_state(UserInfo.free_post_group)
        else:
            await bot.send_message(chat_id=call.from_user.id, text=f'Бесплатно вы можете публиковать только один пост '
                                                                   f'за 24 часа.\n\n '
                                                                   f'Следующий бесплатный пост будет доступен через {access}\n\n'
                                                                   f'🫶 Либо опубликуйте платный пост, чтобы '
                                                                   f'реклама была запущена постоянно!',
                                   reply_markup=actions_with if await check_sub(
                                       call.from_user.username) else actions_without)
    elif '@' in call.data:
        await state.update_data(link=call.data)
        await state.update_data(photo=[], video=[])
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text='<b>Начало создания поста:</b>\n\n'
                                                               'Отправьте изображения или видео к вашему рекламному '
                                                               'объявлению - до 5 штук', parse_mode='HTML',
                               reply_markup=back.as_markup())
        await state.set_state(Post.achive)
    elif call.data == 'ok_verify':
        await call.answer('Одобрено')
        new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
        state_with: FSMContext = FSMContext(
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=new_user_storage_key)
        data = await state_with.get_data()
        await add_subscribe([data['user_ver'], data["name"]])
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=data['user_ver'], text='Ваша заявка на верификацию одобрена.\n'
                                                                   '<b>Начало создания поста:</b>\n\n'
                                                                   'Отправьте изображения или видео к вашему '
                                                                   'рекламному объвлению - до 5 штук',
                                    parse_mode='HTML')
    elif call.data == 'no_verify':
        await call.answer('Отклонено')
        new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
        state_with: FSMContext = FSMContext(
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=new_user_storage_key)
        data = await state_with.get_data()
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=data['user_ver'], text='Ваша заявка на верификацию отклонена.',
                                    reply_markup=actions_with if await check_sub(
                                        call.from_user.username) else actions_without)
    elif 'ok_pay' in str(call.data):
        chat = call.data.split('_')[2]
        await call.answer('Одобрено')
        new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
        state_with: FSMContext = FSMContext(
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=new_user_storage_key)
        data = await state_with.get_data()
        await call.bot.send_message(chat_id=call.from_user.id, text='Добавить траковый бизнес?',
                                    reply_markup=truck_pay.as_markup())
        await state.update_data(user=chat, name=data['name'])
        await state.set_state(Operator.truck)
    elif call.data == 'no_pay':
        chat = call.data.split('_')[2]
        await call.answer('Отклонено')
        new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
        state_with: FSMContext = FSMContext(
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=new_user_storage_key)
        data = await state_with.get_data()
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=chat, text='Упс, не смогли найти вашу Premium '
                                                       'подписку.\n\nПопробуйте ещё раз!',
                                    reply_markup=i_pay.as_markup())
    await call.answer()
    if call.data == 'go_verify':
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=call.from_user.id, text='Пожалуйста пришлите фото или название своей '
                                                                    'компании:', reply_markup=back.as_markup())
        await state.set_state(verification.get_info)
    elif call.data == "order":
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text='Оформите подписку и нажмите кнопку ниже.',
                               reply_markup=order.as_markup())
        await state.set_state(Order.accept)
    elif call.data == "go_back":
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=call.from_user.id,
                                    text=f'Вы выбрали регион: {await get_region(call.from_user.id)}',
                                    reply_markup=actions_with if await check_sub(
                                        call.from_user.username) else actions_without)
        await state.clear()


@router.callback_query(Post.select)
async def pay_post(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'go_back':
        # data = await state.get_data()
        await call.answer()
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await state.clear()


@router.callback_query(Post.view)
async def pay_post(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'edit_text':
        await call.answer()
        await call.bot.send_message(chat_id=call.from_user.id, text='Введите новый текст для поста:',
                                    reply_markup=back.as_markup())
        await state.set_state(Post.edit_text)
    elif call.data == 'edit_media':
        await call.answer()
        await call.bot.send_message(chat_id=call.from_user.id, text='Прикрепите новые фото/видео:',
                                    reply_markup=back.as_markup())
        await state.set_state(Post.edit_media)
    elif call.data == 'back':
        await call.answer()
        message = call.message.message_id
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=message)
        await state.clear()


@router.callback_query(Post.edit_media)
@router.callback_query(Post.edit_text)
async def pay_post(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'go_back':
        await call.answer()
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await state.set_state(Post.view)


@router.message(UserInfo.FIO)
async def edit_text(message: types.Message, state: FSMContext):
    await state.update_data(text_check=message.text)
    new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
    state_with: FSMContext = FSMContext(
        storage=dp.storage,  # dp - экземпляр диспатчера
        key=new_user_storage_key)
    await state_with.update_data(user=message.from_user.id, name=message.from_user.username)
    data = await state.get_data()
    await message.answer('Ваши данные отправлены для проверки.\n\n'
                         '⏰ Время ответа: до 5 минут')
    await bot.send_message(chat_id=OPERATOR, text=f'Запрос проверки оплаты:\n\n'
                                                  f'ФИО: {data["text_check"]}\n'
                                                  f'Username: {message.from_user.username}',
                           reply_markup=await create_oper_but(message.from_user.id))
    await state.set_state(None)


@router.message(Post.edit_text)
async def edit_text(message: types.Message, state: FSMContext):
    answer = message.html_text
    data = await state.get_data()
    if len(answer) <= 400:
        await edit_text_post((answer, message.from_user.username, data['edit_text']))
        await preview([message.from_user.username, await get_region(message.from_user.id), message.from_user.id])
        await bot.send_message(chat_id=message.from_user.id, text=f'Вы успешно изменили текст поста!\n',
                               reply_markup=actions_with if await check_sub(
                                   message.from_user.username) else actions_without)
        await state.clear()
    else:
        await message.answer('Введите текст не более 400 символов.')


@router.message(Post.edit_media)
async def achive_post(message: types.Message, state: FSMContext, album: list = None):
    await state.update_data(photo=[], video=[])
    data = await state.get_data()
    if album:
        if len(album) > 5:
            await message.answer('Нельзя прикрепить больше 5 вложений\n'
                                 'Попробуйте снова.')
        else:
            for i in album:
                if 'Video' in str(i):
                    pre = str(i).split('Video')[1]
                    pre = pre.split('file_unique_id')[0]
                    pre = pre.replace('(', '').replace('file_id=', '').replace(',', '')
                    pre = pre[1:len(pre) - 2]
                    data['video'].append(pre)
                elif 'photo=[PhotoSize(' in str(i):
                    pre = str(i).split('photo=[PhotoSize(')[1]
                    pre = pre.split('file_unique_id')[0]
                    pre = pre.replace('(', '').replace('file_id=', '').replace(',', '')
                    pre = pre[1:len(pre) - 2]
                    data['photo'].append(pre)
            else:
                await edit_media_post(
                    (str(data['photo']), str(data['video']), message.from_user.username, data['edit_text']))
                await get_post(message.from_user.username)
                await preview(
                    [message.from_user.username, await get_region(message.from_user.id), message.from_user.id])
                await message.answer('Вы успешно изменили вложения для поста',
                                     reply_markup=actions_with if await check_sub(
                                         message.from_user.username) else actions_without)
                await state.clear()
    else:
        if message.photo:
            data['photo'].append(message.photo[-1].file_id)
        elif message.video:
            data['video'].append(message.video.file_id)
        await edit_media_post((str(data['photo']), str(data['video']), message.from_user.username, data['edit_text']))
        await message.answer('Вы успешно изменили вложения для поста')
        await state.clear()


@router.callback_query(Order.accept)
async def pay_post(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    if call.data == 'ok_order':
        await call.bot.send_message(chat_id=call.from_user.id, text='Пожалуйста пришлите фото или название своей '
                                                                    'компании:', reply_markup=back.as_markup())
        await state.set_state(verification.get_info)


@router.message(verification.get_info)
async def verifi(message: types.Message, state: FSMContext):
    if message.from_user.username is not None:
        await state.update_data(ver_user=message.from_user.username)
        if message.photo:
            await state.update_data(ver_photo=message.photo[-1].file_id)
            data = await state.get_data()
            await bot.send_photo(chat_id=OPERATOR, photo=data['ver_photo'],
                                 caption=f'Запрос верификации от @{data["ver_user"]}',
                                 reply_markup=oper_accept.as_markup())
        else:
            await state.update_data(ver_text=message.text)
            data = await state.get_data()
            new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
            state_with: FSMContext = FSMContext(
                storage=dp.storage,  # dp - экземпляр диспатчера
                key=new_user_storage_key)
            await state_with.update_data(user_ver=message.from_user.id, name=data["ver_user"])
            await state_with.set_state(Operator.verify)
            await bot.send_message(chat_id=OPERATOR, text=f'Запрос верификации от @{data["ver_user"]}\n\n'
                                                          f'{data["ver_text"]}', reply_markup=oper_accept.as_markup())
        await message.answer('Ваши данные отправлены, ожидайте.')
        await state.set_state(UserInfo.wait_verify)
    else:
        if message.photo:
            await state.update_data(ver_photo=message.photo[-1].file_id)
        else:
            await state.update_data(ver_text=message.text)
        await message.answer('У вас скрыт username!\n'
                             'Пожалуйста введите его:')
        await state.set_state(verification.get_username)


@router.message(verification.get_username)
async def ver_username(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(ver_user=answer)
    data = await state.get_data()
    new_user_storage_key = StorageKey(bot_id=bot.id, chat_id=OPERATOR, user_id=OPERATOR)
    state_with: FSMContext = FSMContext(
        storage=dp.storage,  # dp - экземпляр диспатчера
        key=new_user_storage_key)
    await state_with.update_data(user_ver=message.from_user.id, name={data["ver_user"]})
    await bot.send_message(chat_id=OPERATOR, text=f'Запрос верификации от @{data["ver_user"]}\n\n'
                                                  f'{data["ver_text"]}', reply_markup=oper_accept.as_markup())
    await state_with.set_state(Operator.verify)
    await message.answer('Ваши данные отправлены, ожидайте.')
    await state.set_state(UserInfo.wait_verify)


@router.callback_query(UserInfo.post_group)
async def pay_post(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    if call.data == 'go_back':
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=call.from_user.id,
                                    text=f'Вы выбрали регион: {await get_region(call.from_user.id)}',
                                    reply_markup=actions_with if await check_sub(
                                        call.from_user.username) else actions_without)
        await state.clear()


@router.callback_query(Post.achive)
async def back_achive(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    if call.data == 'go_back':
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=call.from_user.id,
                                    text=f'Вы выбрали регион: {await get_region(call.from_user.id)}',
                                    reply_markup=actions_with if await check_sub(
                                        call.from_user.username) else actions_without)
        await state.clear()


@router.callback_query(UserInfo.free_post_group)
async def free_post(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    if call.data == 'go_back':
        await call.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.bot.send_message(chat_id=call.from_user.id,
                                    text=f'Вы выбрали регион: {await get_region(call.from_user.id)}',
                                    reply_markup=actions_with if await check_sub(
                                        call.from_user.username) else actions_without)
        await state.clear()
    elif '@' in call.data:
        await state.update_data(photo=[], video=[], link=call.data)
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text='<b>Начало создания поста:</b>\n\n'
                                                               'Отправьте изображения или видео к вашему рекламному '
                                                               'объявлению - до 5 штук', parse_mode='HTML',
                               reply_markup=back.as_markup())
        await state.set_state(Post.achive)


@router.message(F.video)
@router.message(F.photo)
@router.message(Post.achive, UserInfo.wait_verify)
async def achive_post(message: types.Message, state: FSMContext, album: list = None):
    await state.update_data(photo=[], video=[])
    data = await state.get_data()
    try:
        typ = data['type']
    except KeyError:
        await state.update_data(type='pay')
        data = await state.get_data()
    if album:
        if len(album) > 5:
            await message.answer('Нельзя прикрепить больше 5 вложений\n'
                                 'Попробуйте снова.')
        else:
            for i in album:
                if 'Video' in str(i):
                    pre = str(i).split('Video')[1]
                    pre = pre.split('file_unique_id')[0]
                    pre = pre.replace('(', '').replace('file_id=', '').replace(',', '')
                    pre = pre[1:len(pre) - 2]
                    data['video'].append(pre)
                elif 'photo=[PhotoSize(' in str(i):
                    pre = str(i).split('photo=[PhotoSize(')[1]
                    pre = pre.split('file_unique_id')[0]
                    pre = pre.replace('(', '').replace('file_id=', '').replace(',', '')
                    pre = pre[1:len(pre) - 2]
                    data['photo'].append(pre)
            else:
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - len(album))
                await message.answer('Спасибо! Теперь напишите текст рекламного объявления:')
                await state.set_state(Post.text)
    else:
        if message.photo:
            data['photo'].append(message.photo[-1].file_id)
        elif message.video:
            data['video'].append(message.video.file_id)
        await message.answer('Спасибо! Теперь напишите текст рекламного объявления:')
        await state.set_state(Post.text)


@router.message(Post.text)
async def text_post(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answer = message.html_text
    await state.update_data(text=answer)
    name = message.from_user.username
    try:
        typ = data['type']
    except KeyError:
        await state.update_data(type='pay')
        data = await state.get_data()
    if name is None:
        await message.answer('У вас скрыт username!\n'
                             'Пожалуйста введите его:')
        await state.set_state(Post.username)
    else:
        await state.update_data(username=name)
        if data['type'] == 'free':
            if len(answer) <= 400:
                data = await state.get_data()
                lst = [message.from_user.id, data['username'], data['link']]
                await add_free_post(lst)
                await publ_free_post(data)
                await message.answer('✅ БЕСПЛАТНЫЙ ПОСТ ОПУБЛИКОВАН!',
                                     reply_markup=actions_with if await check_sub(
                                         message.from_user.username) else actions_without)
                await state.clear()
            else:
                await message.answer('Текст должен быть не более 400 символов')
        else:
            data = await state.get_data()
            lst = [data['username'], await get_region(message.from_user.id), data['text'], str(data['photo']),
                   str(data['video'])]
            if await add_post(lst):
                if len(answer) <= 400:
                    await preview(
                        [message.from_user.username, await get_region(message.from_user.id), message.from_user.id])
                    await message.answer(
                        '✅ <b>РЕКЛАМА ЗАПУЩЕНА!</b>\n\n'
                        'СКОРО ОНА ПОЯВИТСЯ ВО ВСЕХ ТЕЛЕГРАМ ГРУППАХ.', parse_mode='HTML',
                        reply_markup=actions_with if await check_post(
                            message.from_user.username) else actions_without)
                    await state.clear()
                else:
                    await message.answer('Текст должен быть не более 400 символов')
            else:
                await message.answer('Ваше сообщение не прошло модерацию. Попробуйте ещё раз.')


@router.message(Post.username)
async def name_post(message: types.Message, state: FSMContext):
    answer = message.text
    data = await state.get_data()
    await state.update_data(username=answer)
    if data['type'] == 'free':
        lst = [message.from_user.id, data['username'], data['link']]
        if len(data['text']) <= 400:
            await add_free_post(lst)
            await publ_free_post(data)
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await message.answer('✅ БЕСПЛАТНЫЙ ПОСТ ОПУБЛИКОВАН!',
                                 reply_markup=actions_with if await check_sub(
                                     message.from_user.username) else actions_without)
            await state.clear()
        else:
            await message.answer('Текст должен быть не более 400 символов\n'
                                 'Введите текст снова')
            await state.set_state(Post.text)
    else:
        data = await state.get_data()
        lst = [data['username'], data['region'], data['text'], data['photo'], data['video']]
        if len(data['text']) <= 400:
            await add_post(lst)
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await preview([message.from_user.username, await get_region(message.from_user.id), message.from_user.id])
            await message.answer('✅ <b>РЕКЛАМА ЗАПУЩЕНА!</b>\n\n'
                                 'СКОРО ОНА ПОЯВИТСЯ ВО ВСЕХ ТЕЛЕГРАМ ГРУППАХ.', parse_mode='HTML',
                                 reply_markup=actions_with if await check_post(
                                     message.from_user.username) else actions_without)
            await state.clear()
        else:
            await message.answer('Текст должен быть не более 400 символов\n'
                                 'Введите текст снова')
            await state.set_state(Post.text)


@router.message()
async def operatr(message: types.Message, state: FSMContext):
    if message.text == '👩‍🚀 Поддержка':
        await bot.send_message(chat_id=message.from_user.id,
                               text='🧑‍🚀 Макс из OURS всегда на связи и готов помочь!\n\n'
                                    'https://t.me/ours_ads')
    elif message.text == 'Опубликовать пост бесплатно':
        await state.update_data(groups=await get_groups(await get_region(message.from_user.id)))
        data = await state.get_data()
        access = await check_free((str(message.from_user.id),))
        if access is False:
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await bot.send_message(chat_id=message.from_user.id, text='Выберите группу для публикации:',
                                   reply_markup=await create_buttons(data["groups"]))
            await state.update_data(type='free')
            await state.set_state(UserInfo.free_post_group)
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text=f'Бесплатно вы можете публиковать только один пост за 24 часа.\n\n'
                                        f'Следующий бесплатный пост будет доступен через {access}\n\n'
                                        f'🫶 Либо опубликуйте платный пост, чтобы реклама была запущена постоянно!',
                                   reply_markup=actions_with if await check_sub(
                                       message.from_user.username) else actions_without)
            await state.clear()
    elif message.text == '🔥 Платная публикация поста':
        if await check_sub(message.from_user.username):
            await state.update_data(photo=[], video=[], type='pay')
            await bot.send_message(chat_id=message.from_user.id, text='<b>Начало создания поста:</b>\n\n'
                                                                      'Отправьте изображения или видео к вашему '
                                                                      'рекламному объявлению - до 5 штук',
                                   parse_mode='HTML',
                                   reply_markup=back.as_markup())
            await state.set_state(Post.achive)
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text='<b>Вот ссылка для скачивания:</b>\n\n<a '
                                        'href="https://OURSUSA.COM?utm_campaign=bot_ads&utm_medium=social&utm_source'
                                        '=ads_bot"><b>👉OURSUSA.COM</b></a>\n<a '
                                        'href="https://OURSUSA.COM?utm_campaign=bot_ads&utm_medium=social&utm_source'
                                        '=ads_bot"><b>👉OURSUSA.COM</b></a>\n<a '
                                        'href="https://OURSUSA.COM?utm_campaign=bot_ads&utm_medium=social&utm_source'
                                        '=ads_bot"><b>👉OURSUSA.COM</b></a>', parse_mode='HTML',
                                   disable_web_page_preview=True)
            await asyncio.sleep(2)
            await bot.send_message(chat_id=message.from_user.id,
                                   text='Нажми кнопку «<b>Я ОПЛАТИЛ</b>», если ты купил подписку Premium.',
                                   reply_markup=i_pay.as_markup(), parse_mode='HTML')
            await bot.send_video(chat_id=message.from_user.id,
                                 video='BAACAgIAAxkBAAILnmXRA2pYGHsSmgWr1lao5LmSRY-QAAK5RAACZKCJSjGvIDSX9DcwNAQ',
                                 caption='Кстати, ты можешь посмотреть видео инструкцию на '
                                         '40 секунд, как вытащить максимум из OURS')
    elif message.text == 'Редактирование поста':
        try:
            post = await get_post(message.from_user.username)
            await state.update_data(edit_text=post['text'], edit_photo=post["photo"], edit_video=post['video'])
            await view_post(post, message.from_user.id)
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await state.set_state(Post.view)
        except KeyError:
            await message.answer('У вас нет добавленных постов')


async def publ_free_post(data):
    media_group = MediaGroupBuilder(caption=f"{data['text']}\n")
    for photo in data['photo']:
        media_group.add(type='photo', media=photo)
    else:
        for video in data['video']:
            media_group.add(type='video', media=video)
        else:
            await bot.send_media_group(chat_id=await get_chat(data['link']), media=media_group.build())


async def preview(info):
    data = await get_post_info([info[0], info[1]])
    media_group = MediaGroupBuilder(caption=f"{data['text']}")
    if data['photo'] != "[]":
        photos = data['photo'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')
        try:
            photos = photos.split(', ')
            for photo in photos:
                media_group.add(type='photo', media=photo)
        except:
            media_group.add(type='photo', media=photos)
    elif data['video'] != "[]":
        videos = data['video'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')
        try:
            videos = videos.split(', ')
            for video in videos:
                media_group.add(type='video', media=video)
        except:
            media_group.add(type='video', media=videos)
    await bot.send_media_group(chat_id=info[2], media=media_group.build())


async def view_post(data, user):
    media_group = MediaGroupBuilder(caption=f"{data['text']}")
    if data['photo'] != "[]":
        photos = data['photo'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')
        try:
            photos = photos.split(', ')
            for photo in photos:
                media_group.add(type='photo', media=photo)
        except:
            media_group.add(type='photo', media=photos)
    elif data['video'] != "[]":
        videos = data['video'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')
        try:
            videos = videos.split(', ')
            for video in videos:
                media_group.add(type='video', media=video)
        except:
            media_group.add(type='video', media=videos)
    await bot.send_media_group(chat_id=user, media=media_group.build())
    await bot.send_message(chat_id=user, text=f'Ваш пост выше, желаете что-то изменить?',
                           reply_markup=edit_post.as_markup())


async def send_messages(data):
    media_group = MediaGroupBuilder(caption=f"{data['message_text']}\n")
    if str(data['photo_message']) != "[]":
        photos = str(data['photo_message']).replace('"', '').replace("'", '').replace('[', '').replace(']', '')
        try:
            photos = photos.split(', ')
            for photo in photos:
                media_group.add(type='photo', media=photo)
        except:
            media_group.add(type='photo', media=photos)
    elif str(data['video_message']) != "[]":
        videos = str(data['video_message']).replace('"', '').replace("'", '').replace('[', '').replace(']', '')
        try:
            videos = videos.split(', ')
            for video in videos:
                media_group.add(type='video', media=video)
        except:
            media_group.add(type='video', media=videos)
    chats = await get_all_id()
    for chat in chats:
        if int(chat) != OPERATOR:
            try:
                await bot.send_media_group(chat_id=chat, media=media_group.build())
            except:
                pass


async def publ_pay(data):
    media_group = MediaGroupBuilder(caption=f"{data['text']}\n")
    if data['photo'] != "[]":
        photos = data['photo'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')
        try:
            photos = photos.split(', ')
            for photo in photos:
                media_group.add(type='photo', media=photo)
        except:
            media_group.add(type='photo', media=photos)
    elif data['video'] != "[]":
        videos = data['video'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')
        try:
            videos = videos.split(', ')
            for video in videos:
                media_group.add(type='video', media=video)
        except:
            media_group.add(type='video', media=videos)
    region = data['region']
    chats = await get_chats(region)
    if await check_truck(data['username']) == 'yes':
        chats.append((truck,))
    for chat in chats:
        await bot.send_media_group(chat_id=chat[0], media=media_group.build())


async def check_subscribes():
    now = datetime.datetime.now()
    now = now.strftime('%d.%m.%y')
    info = await get_subs(now)
    if info:
        for row in info:
            await bot.send_message(chat_id=OPERATOR, text=f'Нужно проверить подписку у пользователя @{row[0]}')


async def check_time_pay():
    NY = datetime.datetime.now(tz=pytz.timezone('America/New_York'))
    LA = datetime.datetime.now(tz=pytz.timezone('America/Los_Angeles'))
    LA = LA.strftime('%H:%M')
    NY = NY.strftime('%H:%M')
    await check_and_publicate(LA, 'Калифорния')
    await check_and_publicate(NY, 'Флорида')
    await check_and_publicate(NY, 'Нью-Йорк')
    await check_and_publicate(NY, 'Иллинойс')
    await check_and_publicate(NY, 'Нью-Джерси')


async def check_time_free():
    now = datetime.datetime.now()
    now = now.strftime('%d/%m/%y %H:%M')
    await check_and_delete_free(now)


async def scheduler():
    aioschedule.every().day.at('19:35').do(check_subscribes)
    aioschedule.every().minute.do(check_time_pay)
    aioschedule.every().minute.do(check_time_free)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
