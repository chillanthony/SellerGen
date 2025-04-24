import os
from config import *
from utils.text import *
from utils.tts import *
from utils.clipmatch import *

# 创建路径变量
theme = "美国人民不愿意再支持特朗普的胡闹政策"
message_user_text_generation = message_user_text_generation_prompt + theme
output_folder = os.path.join("output", theme)
src_folder = os.path.join(output_folder, "src")
audio_path = os.path.join(output_folder, theme + ".wav")
video_path = os.path.join(output_folder, theme + ".mp4")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
if not os.path.exists(src_folder):
    os.makedirs(src_folder)

# 生成文案
textconfig = TextConfig(message_system_text_generation, message_user_text_generation)
text = one_round_chat(textconfig.message_system, textconfig.message_user, textconfig.max_tokens,
               textconfig.temperature, textconfig.frequency_penalty, textconfig.max_retries)
text = text_strip(text)
print(text)

# Synthesize the SSML
ttsconfig = TTSConfig(tts_voice_name, text, audio_path)

# Text to speech 
word_boundary_list = text_to_speech(ttsconfig.ssml, audio_path)
sentence_list = to_separated_sentence(word_boundary_list, audio_path)
subtitle_list = to_subtitle(word_boundary_list, audio_path)

clip_list = clip_match(sentence_list, src_folder)
for i in clip_list:
    print(i.index, i.offset, i.duration, i.text)