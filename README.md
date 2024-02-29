# Haircut Suggestion using Stable Diffusion
This project is aimed at creating haircut suggestions by image and prompt, and showing this suggestion in an image form, with face from original image.
## Table of Contents

## Setup
1. Install AUTOMATIC1111 folowing instructions [here](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
2. Install RealisticVision from [here](https://civitai.com/models/4201/realistic-vision-v60-b1), and put it in the stable-diffusion-webui/models/Stable-diffusion/
3. Install ControlNet model from [here](https://huggingface.co/lllyasviel/ControlNet-v1-1/blob/main/control_v11p_sd15_openpose.pth), 
and put it in the stable-diffusion-webui/extensions/sd-webui-controlnet/models
4. Install Inswapper_128 from [here](https://drive.google.com/file/d/1krOLgjW2tAPaqV-Bw4YALz0xT5zlb5HF/view), put it somewhere you can find it
5. Install requirements
6. Enable AUTOMATIC1111 API by folowing [this guide](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API)
7. Create .env file and put your telegram bot token there in the following form: `export BOT_TOKEN=12345abcde`
## Resources
Main paper: [Haircut Styles for Women – A Cheatsheet via /r/StableDiffusion](https://daslikes.wordpress.com/2023/05/05/haircut-styles-for-women-a-cheatsheet-via-r-stablediffusion/)
Face swapper tutorial: [Unbelievable Face Swapping with 5 Lines Code](https://youtu.be/a8vFMaH2aDw?si=wOD3AWWYeV3Upy7w)
## Execution Pipline
To use the telegram bot:
1. Run AUTOMATIC1111 webui with API
2. Run telegram bot
3. Use telegram bot by typing `/start` command, and folowing it's instructions. It's important to provide captions for images
## Research suggestions
Freely use `research.ipynb` for research puproses, but make sure to run webui with api prior. It is also advised to experiment with prompts and models directly through AUTOMATIC1111 webui, rather than through API. 