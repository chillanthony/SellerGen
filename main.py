import os
import sys
import argparse
from datetime import datetime
from config import *
from utils.text import *
from utils.tts import *
from utils.clipmatch import *
from utils.fusevideo import *

# 读取主题参数
parser = argparse.ArgumentParser(description='读取 -t 参数并打印其值')
parser.add_argument('-t', type=str, help='主题参数')
args = parser.parse_args()

if args.t is None:
    print("错误：没有主题参数")
    sys.exit(1)
else:
    theme = args.t
message_user_text_generation = message_user_text_generation_prompt + theme

# 创建路径变量
now = datetime.now()
datetime_str = now.strftime("%Y-%m-%d_%H-%M")
output_folder = os.path.join(output_folder_root, datetime_str + theme)
src_folder = os.path.join(output_folder, "src")
audio_path = os.path.join(output_folder, theme + ".wav")
video_path = os.path.join(output_folder, theme + ".mp4")
video_final_path = os.path.join(output_folder, theme + "_final.mp4")
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

# 匹配片段并下载
clip_list = clip_match(sentence_list, src_folder)

# 生成视频
video_generation(clip_list, video_path)
replace_video_audio(video_path, audio_path, video_final_path)