from enum import Enum
from config import *
from utils.text import *

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

'''
clip_match()
为分句列表里面的每个句子提取热词，获取视频资源，下载资源
sentence_list: 分句列表
src_folder: 保存素材的文件夹
'''
def clip_match(sentence_list, src_folder): 

    # 转化为videoclip类
    clip_list = []
    for i in range(len(sentence_list)):
        clip_list.append(VideoClip(i, sentence_list[i].text, sentence_list[i].audio_offset, sentence_list[i].duration))

    # 提取热词
    for i in range(1, 6):
        hotword = hotword_generation(clip_list[i])
        clip_list[i].hotword = hotword
        print(i, hotword)

    # 
    
    return clip_list


'''
hotword_generation()
输入文本，提取热词
text: 需要提取热词的文本
'''
def hotword_generation(clip):

    hotwordconfig = TextConfig(message_system_hotword_prompt, clip.text)
    hotword = one_round_chat(hotwordconfig.message_system, hotwordconfig.message_user, hotwordconfig.max_tokens,
                hotwordconfig.temperature, hotwordconfig.frequency_penalty, hotwordconfig.max_retries)
    
    return hotword