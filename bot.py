#start - Starts the bot
#help - Shows how to use bot
#get - Gives you screenshot of webpage with given URL
#grafana - Gets current dashbord state

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from pyppeteer import launch
from pyppeteer.errors import PyppeteerError, TimeoutError
from tempfile import NamedTemporaryFile
import socket
import socks
import time

# Configure bot here
API_TOKEN = 'PUT_HERE_TELEGRAM_API_TOKEN'
PROXY_URL='socks5://145.239.93.148:1080'
bot = Bot(token=API_TOKEN, proxy=PROXY_URL)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class ScreenshotForm(StatesGroup):
    url = State()

@dp.message_handler(commands=['get'])
async def send_site_screenshot(message: types.Message):
    await ScreenshotForm.url.set()
    await message.reply('Введите url адрес нужной страницы:')
@dp.message_handler(state=ScreenshotForm.url)
async def process_url(message: types.Message, state: FSMContext):
    await message.reply('Минутку...')
    browser = await launch()
    try:
        page = await browser.newPage()
        url = message.text  # TODO Сделать проверку адреса
        await page.goto(url)
        await page.setViewport(viewport=dict(width=1860, height=1085))
        with NamedTemporaryFile() as fp:
            await page.screenshot(path=fp.name, type='jpeg', quality=100, fullPage=False)
            await message.reply_photo(fp.file)
    except (PyppeteerError, TimeoutError) as e:
        await message.reply('Ой, что-то пошло не так!\n' + str(e))
    finally:
        await state.finish()
        await browser.close()

@dp.message_handler(commands=['start'])
async def process_start(message: types.Message):
    await message.reply('Привет, ' + message.from_user.username + "!")

@dp.message_handler(commands=['help'])
async def process_help(message: types.Message):
    await message.reply('Для получения скриншота веб-страницы, используйте команду /get\nДля получения текущего состояния дашборда, используйте команду /grafana')

@dp.message_handler(commands=['grafana'])
async def process_grafana(message: types.Message, state: FSMContext):
    browser = await launch()
    try:
        page = await browser.newPage()
        await page.goto('http://localhost:3000/d/t7mCH_sik/monitoring-os?orgId=1&var-job=node&var-node=localhost&var-port=9100&kiosk=tv')
        time.sleep(1)
        await page.setViewport(viewport=dict(width=1860, height=1085))
        with NamedTemporaryFile() as fp:
            await page.screenshot(path=fp.name, type='jpeg', quality=100, fullPage=False)
            await message.reply_photo(fp.file)
    except (PyppeteerError, TimeoutError) as e:
        await message.reply('Ой, что-то пошло не так!\n' + str(e))
    finally:
        await state.finish()
        await browser.close()    

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)