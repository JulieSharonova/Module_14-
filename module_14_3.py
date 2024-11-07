from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKENURBAN

api = TOKENURBAN
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
kb.add(button)
kb.add(button2)
kb.add(button3)

kb2 = InlineKeyboardMarkup()
but = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
but2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb2.add(but)
kb2.add(but2)

kb3 = InlineKeyboardMarkup()
button = InlineKeyboardButton(text='Продукт 1', callback_data='product_buying')
button2 = InlineKeyboardButton(text='Продукт 2', callback_data='product_buying')
button3 = InlineKeyboardButton(text='Продукт 3', callback_data='product_buying')
button4 = InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')
kb3.add(button)
kb3.add(button2)
kb3.add(button3)
kb3.add(button4)

list_photo = ['pill1.jpg', 'pill2.jpg', 'pill3.jpg', 'pill4.jpg']
catalog = [
    'Название:Product 1 | Описание:описание 1 | Цена:100',
    'Название:Product 2 | Описание:описание 2 | Цена:200',
    'Название:Product 3 | Описание:описание 3 | Цена:300',
    'Название:Product 4 | Описание:описание 4 | Цена:400'
]


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я - бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Информация')
async def info(message):
    await message.answer('Я - бот, рассчитывающий норму ккалорий по упрощенной формуле Миффлина-Сан Жеора.')


@dp.message_handler(text=['Купить'])
async def get_buying_list(message: types.Message):
    for i in range(4):
        await message.answer(f'{catalog[i]}')
        await bot.send_photo(chat_id=message.from_user.id, photo=InputFile(list_photo[i]))
    await  message.answer('Выберите продукт для покупки: ', reply_markup=kb3)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await call.answer()


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer(f'Выберите опцию:', reply_markup=kb2)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    try:
        age = float(data['age'])
        growth = float(data['growth'])
        weight = float(data['weight'])
    except:
        await message.answer('Не могу конвертировать введенные значения в числа.')
        await state.finish()
        return

    calories = 10 * weight + 6.25 * growth - 5 * age - 161
    await message.answer(f'Ваша норма калорий: {calories} ккал в день')
    await state.finish()


@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
