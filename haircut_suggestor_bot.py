# Bot Imports
import os
import requests
import math
import telebot
from telebot import types
from dotenv import load_dotenv

# Model Imports
import webuiapi
import PIL
import insightface
from insightface.app import FaceAnalysis
from insightface.data import get_image as ins_get_image
import numpy as np

# Load environment variables from .env file. Your BOT_TOKEN should be there.
load_dotenv()

# Model preparation
api = webuiapi.WebUIApi(host='127.0.0.1', port=7860)
app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0, det_size=(640, 640))
swapper = insightface.model_zoo.get_model('inswapper_128.onnx', # Make sure to download this model and povide the path
                                          download=False,
                                          download_zip=False)

# Bot preparation
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

welcome_prompt = '''Welcome to Haircut Suggestor Bot!'''

male_button = types.InlineKeyboardButton('Male', callback_data='male')
female_button = types.InlineKeyboardButton('Female', callback_data='female')
other_button = types.InlineKeyboardButton('Other', callback_data='other')

keyboard = types.InlineKeyboardMarkup()
keyboard.add(female_button)
keyboard.add(male_button)
keyboard.add(other_button)

gender_statuses = {}

# Caption example: 'Faux Hawk Haircut' or 'Slicked Back Haircut'
def prompt_generation(gender, caption):
    if gender == 'female':
        return f'photo of a woman, ({caption}:1.2), wearing a white t-shirt, neutral light gray background, detailed (wrinkles, blemishes, folds, moles, veins, pores, skin imperfections:1.1), highly detailed glossy eyes, (looking at the camera), specular lighting, dslr, ultra quality, sharp focus, tack sharp, dof, film grain, centered, Fujifilm XT3, crystal clear'
    if gender == 'male':
        return f'photo of a man, ({caption}:1.2), wearing a white t-shirt, neutral light gray background, detailed (wrinkles, blemishes, folds, moles, veins, pores, skin imperfections:1.1), highly detailed glossy eyes, (looking at the camera), specular lighting, dslr, ultra quality, sharp focus, tack sharp, dof, film grain, centered, Fujifilm XT3, crystal clear'
    if gender == 'other':
        return f'photo of a person, ({caption}:1.2), wearing a white t-shirt, neutral light gray background, detailed (wrinkles, blemishes, folds, moles, veins, pores, skin imperfections:1.1), highly detailed glossy eyes, (looking at the camera), specular lighting, dslr, ultra quality, sharp focus, tack sharp, dof, film grain, centered, Fujifilm XT3, crystal clear'



@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    """Give a welcome prompt."""
    bot.reply_to(message, welcome_prompt)
    global gender_statuses
    gender_statuses[message.chat.id] = 'female'
    bot.send_message(message.chat.id, text="Choose photo models' appearance", reply_markup=keyboard)

@bot.message_handler(commands=['mode'])
def send_welcome(message):
    """Gender menu"""
    bot.send_message(message.chat.id, text="Choose photo models' appearance", reply_markup=keyboard)

@bot.message_handler(commands=['current_status'])
def send_welcome(message):
    """View current gender status"""
    global gender_statuses
    bot.send_message(message.chat.id, text=f'Currently in {gender_statuses[message.chat.id]} mode')

@bot.message_handler(func=lambda message: message.chat.type=='private', content_types=['photo']) 
def photo_worker(message): 
    """Create a photo of a person with different haircut"""
    global gender_statuses
    caption = message.caption
    file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    src = 'tmp/input.png'
    with open(src, "wb") as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, 'Received photo, creating haircut...')
    image = PIL.Image.open('tmp/input.png')
    
    unit1 = webuiapi.ControlNetUnit(input_image=image, module='openpose', model='control_v11p_sd15_openpose [cab727d4]', weight=0.6)
    prompt = prompt_generation(gender_statuses[message.chat.id], caption)
    r = api.txt2img(
    prompt = prompt,
    negative_prompt = 'hat, headscarf, naked, nude, out of frame, tattoo, b&w, sepia, (blurry un-sharp fuzzy un-detailed skin:1.4), (twins:1.4), (geminis:1.4), (wrong eyeballs:1.1), (cloned face:1.1), (perfect skin:1.2), (mutated hands and fingers:1.3), disconnected hands, disconnected limbs, amputation, (semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime, doll, overexposed, photoshop, oversaturated:1.4)',
    controlnet_units=[unit1],
    cfg_scale = 3.5,
    steps = 18,
    sampler_name = "DPM++ 2M Karras",
    restore_faces = True,
    override_settings = {
        "sd_model_checkpoint": "realisticVisionV60B1_v51VAE.safetensors [ef76aa2332]",
    },
)
    new_image = r.images[0]

    input_image_array = np.array(image)
    new_image_array = np.array(new_image)

    input_image_face = app.get(input_image_array)[0]
    new_image_face = app.get(new_image_array)[0]

    result = new_image_array.copy()
    result = swapper.get(result, new_image_face, input_image_face, paste_back=True)

    res = PIL.Image.fromarray(np.uint8(result)).convert('RGB')
    res.save('tmp/output.jpg')

    bot.send_photo(message.chat.id, photo=open('tmp/output.jpg', 'rb'))

    bot.send_message(message.chat.id, 'Send another photo with haircut name in the captions to get more suggestions or use /mode to change model\'s appearance')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global gender_statuses
    if call.data == "female":
        gender_statuses[call.from_user.id] = 'female'
        bot.answer_callback_query(call.id, "Showing female suggestions")
        bot.send_message(call.from_user.id, 'Send photo with haircut name in the captions to get suggestion or use /mode to change model\'s appearance')
    elif call.data == "male":
        gender_statuses[call.from_user.id] = 'male'
        bot.answer_callback_query(call.id, "Showing male suggestions")
        bot.send_message(call.from_user.id, 'Send photo with haircut name in the captions to get suggestion or use /mode to change model\'s appearance')
    elif call.data == "other":
        gender_statuses[call.from_user.id] = 'other'
        bot.answer_callback_query(call.id, "Showing other suggestions")
        bot.send_message(call.from_user.id, 'Send photo with haircut name in the captions to get suggestion or use /mode to change model\'s appearance')




bot.infinity_polling()