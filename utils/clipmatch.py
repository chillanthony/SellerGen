from enum import Enum
from config import *
from text import *

class clip_type(Enum):
    Video = 1
    Photo = 2
    Default = 3

class VideoClip:

    def __init__(self, index, text, offset, duration, type = None, hotword = None, url = None, path = None):
        self.index = index
        self.text = text
        self.offset = offset
        self.duration = duration
        self.type = type
        self.hotword = hotword
        self.url = url
        self.path = path

def hotword_generation(sentence_list):
    hotword_list = []
    for i in range(len(sentence_list)):
        hotwordconfig = TextConfig(message_system_hotword_prompt, sentence_list[i].text)
        hotword = one_round_chat(hotwordconfig.message_system, hotwordconfig.message_user, hotwordconfig.max_tokens,
                    hotwordconfig.temperature, hotwordconfig.frequency_penalty, hotwordconfig.max_retries)
        print(i+1, '/', len(sentence_list), ':', hotword)
        hotword_list.append(hotword)