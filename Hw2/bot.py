from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN
from utils.calculations import *
from utils.weather import get_temperature
from utils.food import get_food_info

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

users = {}


# здесь и далее -- по хорошему распилить на 2 метода (ask + handle)
# но для учебного проекта -- я решил, что сойдет...
@dp.message_handler(commands=["set_profile"]) 
async def set_profile(message):
    users[message.from_user.id] = {}
    await message.answer("Введите ваш вес (в кг):")


@dp.message_handler(lambda m: m.from_user.id in users and "weight" not in users[m.from_user.id])
async def set_weight(message):
    users[message.from_user.id]["weight"] = int(message.text)
    await message.answer("Введите ваш рост (в см):")


@dp.message_handler(lambda m: "height" not in users[m.from_user.id])
async def set_height(message: types.Message):
    users[message.from_user.id]["height"] = int(message.text)
    await message.answer("Введите ваш возраст:")


@dp.message_handler(lambda m: "age" not in users[m.from_user.id])
async def set_age(message: types.Message):
    users[message.from_user.id]["age"] = int(message.text)
    await message.answer("Сколько у вас с вреднем минут активности в день?")


@dp.message_handler(lambda m: "activity" not in users[m.from_user.id])
async def set_activity(message: types.Message):
    users[message.from_user.id]["activity"] = int(message.text)
    await message.answer("В каком городе вы живете?")


@dp.message_handler(lambda m: "city" not in users[m.from_user.id])
async def set_city(message: types.Message):
    uid = message.from_user.id
    users[uid]["city"] = message.text

    temp = get_temperature(message.text)
    water = calculate_water_norm(
        users[uid]["weight"],
        users[uid]["activity"],
        temp
    )
    calories = calculate_calorie_norm(
        users[uid]["weight"],
        users[uid]["height"],
        users[uid]["age"],
        users[uid]["activity"]
    )

    users[uid].update({
        "water_goal": water,
        "calorie_goal": calories,
        "logged_water": 0,
        "logged_calories": 0,
        "burned_calories": 0
    })

    await message.answer(
        f"Профиль сохранён!\n"
        f"Норма воды: {water} мл\n"
        f"Норма калорий: {calories} ккал"
    )


@dp.message_handler(commands=["log_water"])
async def log_water(message: types.Message):
    uid = message.from_user.id
    amount = int(message.text.split()[1])

    users[uid]["logged_water"] += amount
    left = users[uid]["water_goal"] - users[uid]["logged_water"]

    await message.answer(f"Записано {amount} мл. Осталось {max(left, 0)} мл.")


@dp.message_handler(commands=["log_food"])
async def log_food(message: types.Message):
    product = message.text.replace("/log_food", "").strip()
    info = get_food_info(product)

    if not info:
        await message.answer("Продукт не найден")
        return

    users[message.from_user.id]["_food"] = info
    await message.answer(
        f"{info['name']} — {info['calories']} ккал / 100 г\n"
        "Сколько грамм вы съели?"
    )


@dp.message_handler(lambda m: "_food" in users[m.from_user.id])
async def food_grams(message: types.Message):
    grams = int(message.text)
    info = users[message.from_user.id].pop("_food")

    kcal = info["calories"] * grams / 100
    users[message.from_user.id]["logged_calories"] += kcal

    await message.answer(f"Записано {kcal:.1f} ккал")


@dp.message_handler(commands=["log_workout"])
async def log_workout(message: types.Message):
    _, workout, minutes = message.text.split()
    minutes = int(minutes)

    burned = calories_from_workout(workout, minutes)
    users[message.from_user.id]["burned_calories"] += burned

    await message.answer(
        f"{workout} {minutes} мин — {burned} ккал\n"
        f"Дополнительно выпейте {(minutes // 30) * 200} мл воды"
    )


@dp.message_handler(commands=["check_progress"])
async def check_progress(message: types.Message):
    u = users[message.from_user.id]

    await message.answer(
        f"Прогресс:\n\n"
        f"Вода: {u['logged_water']} / {u['water_goal']} мл\n\n"
        f"Калории:\n"
        f"Потреблено: {u['logged_calories']:.0f}\n"
        f"Сожжено: {u['burned_calories']}\n"
        f"Баланс: {u['logged_calories'] - u['burned_calories']:.0f}"
    )


if __name__ == "__main__":
    executor.start_polling(dp)