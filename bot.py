import config, simplerow, openweatherapi
import asyncio, logging

from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums.parse_mode import ParseMode


logger = logging.getLogger()
logger.setLevel(logging.INFO)
 
file_handler = logging.FileHandler('logs\log.log', mode='a')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s'))
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s'))
 
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info('Bot has been laucnhed.')


bot = Bot(config.TG_BOT_TOKEN)

dp = Dispatcher()


class GetWeather(StatesGroup):
    choosing_city = State()
    choosing_mode = State()


@dp.message(StateFilter(None), Command('start'))
async def cmd_start(message: types.Message):
    await message.answer('Привет!\nЧтобы подробнее узнать о командах, пропиши /help')

@dp.message(StateFilter(None), Command('help'))
async def cmd_start(message: types.Message):
    await message.answer('/weather <город>  -  получить данные о погоде в конкретном городе')

@dp.message(StateFilter(None), Command('weather'))
async def cmd_calclater(message: types.Message, state: FSMContext):
    cities = []
    lat_lon = []
    
    text = (message.text).replace('/weather', '').strip()
    contents = openweatherapi.get_geo(text)
    if contents and len(text)>0:
        
        for city in contents:
            name = city["name"]
            country = city["country"]
            state_ = ''
            try:
                state_ = city["state"]
            except:
                pass
            cities.append(f'{name}, {state_}, {country}')
            lat_lon.append([city["lat"], city["lon"]])
            

        markup = simplerow.make_inline_keyboard(cities)
        await message.answer('Выберите город:', reply_markup=markup)
        
        await state.set_state(GetWeather.choosing_city)
        await state.update_data(lat_lon=lat_lon)
    
    else:
        await message.reply('ERROR: Некорректное название города')
        logger.error(f'[chat_id: {message.chat.id, message.chat.first_name, message.chat.last_name,}] - [ERROR: invalid country name] - [value: {text}]')
        
    logger.info(f'[chat_id: {message.chat.id, message.chat.first_name, message.chat.last_name,}] - [action: choosing_city] - [value: {text}]')


@dp.callback_query(GetWeather.choosing_city) 
async def weather_query(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    modes = ['Текущая погода']
    
    markup = simplerow.make_inline_keyboard(modes)
    await call.message.answer('Выберите режим:', reply_markup=markup)
    
    index = int(call.data)
    lat_lon = (await state.get_data())["lat_lon"]
    lat, lon = lat_lon[index][0], lat_lon[index][1]
    
    await state.clear()
    await state.set_state(GetWeather.choosing_mode)
    await state.update_data(lat=lat, lon=lon)


@dp.callback_query(GetWeather.choosing_mode) 
async def weather_query(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    time = datetime.now()
    BASE_ICON_URL = 'https://openweathermap.org/img/wn/'
    MM_HG = 1.33322
    
    data = await state.get_data()
    index_mode = int(call.data)
    lat = data["lat"]
    lon = data["lon"]
    
    if index_mode == 0:
        contents = openweatherapi.get_current_weather(lat, lon)
        
        await call.message.answer_photo(photo=f'{BASE_ICON_URL}{contents["weather"][0]["icon"]}@2x.png',
                                        caption=f'<b><u>Данные о погоде {time.strftime("%Y.%m.%d %H:%M")}</u></b>\
                                        \n\n\U0001F3D9 <b>Населённый пункт</b>:\t\t\t{contents["name"]}, {contents["sys"]["country"]}\
                                        \n\n\U00002601 <b>Погода</b>:\t\t\t{contents["weather"][0]["main"]}, {contents["weather"][0]["description"]}\
                                        \n\n\U0001F321 <b>Температура</b>:\t\t\t{contents["main"]["temp"]} \U00002103, ощущается как {contents["main"]["feels_like"]} \U00002103\
                                        \n\n\U0001F525 <b>Макс. температура</b>:\t\t\t{contents["main"]["temp_max"]} \U00002103\
                                        \n\n\U0001F9CA <b>Мин. температура</b>:\t\t\t{contents["main"]["temp_min"]} \U00002103\
                                        \n\n\U0001F32B <b>Влажность</b>:\t\t\t{contents["main"]["humidity"]} %\
                                        \n\n\U0001F300 <b>Атм. давление</b>:\t\t\t{round(contents["main"]["pressure"] / MM_HG, 2)} мм рт. ст\
                                        \n\n\U0001F305 <b>Восход</b>:\t\t\t{datetime.fromtimestamp(contents["sys"]["sunrise"]).strftime("%Y.%m.%d %H:%M")}\
                                        \n\n\U0001F307 <b>Закат</b>:\t\t\t{datetime.fromtimestamp(contents["sys"]["sunset"]).strftime("%Y.%m.%d %H:%M")}\
                                        \n\n\U0001F4A8 <b>Ветер</b>:\t\t\t{contents["wind"]["speed"]} м/с\
                                        \n\n\U0001F9EDНаправление ветра:\t\t\t{contents["wind"]["deg"]}\U000000B0',
                                        parse_mode=ParseMode.HTML)

        # print(contents)
        
        logger.info(f'[chat_id: {call.message.chat.id, call.message.chat.first_name, call.message.chat.last_name,}] - [action: choosing_mode] - [mode: current] - [city: {contents["name"]}, {contents["sys"]["country"]}]')
        
    elif index_mode == 1:
        pass
    
    await state.clear()


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())