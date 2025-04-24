import jieba.analyse
import subprocess
import json
import os
import requests
from tqdm import tqdm
from deep_translator import GoogleTranslator
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

    for i in range(len(clip_list)):
        print(i, ':')
        # 提取热词
        hotword = hotword_generation(clip_list[i])
        clip_list[i].hotword = hotword

        # 获取资源
        url, tp = call_pexels(clip_list[i])
        clip_list[i].url = url
        clip_list[i].type = tp
        clip_list[i].path = os.path.join(src_folder, str(i) + '.mp4')

        if clip_list[i].type == clip_type.Video:
            download_video(clip_list[i].url, clip_list[i].path)
    
    return clip_list


'''
hotword_generation()
输入文本，提取热词，翻译为英文（匹配视频的需要）
clip: 需要提取热词的片段
'''
def hotword_generation(clip):

    keywords = jieba.analyse.extract_tags(clip.text, topK=1)
    if len(keywords) == 1:
        hotword = GoogleTranslator(source='zh-CN', target='en').translate(keywords[0])
        print(keywords[0], hotword)
    else:
        hotword = 'NaN'
        print(hotword)
    
    return hotword

'''
call_pexels()
为每个clip获取pexels视频链接
clip: 需要匹配视频的片段
'''
def call_pexels(clip):

    try:
        # 调用 Node.js 脚本
        result = subprocess.run(
            ['node', 'js/video.js', clip.hotword],
            capture_output=True,
            text=True,
            check=True
        )

        # 输出内容 解析为json
        output = result.stdout.strip()
        data = json.loads(output)

        if data['total_results'] == 0:
            return None, clip_type.Default
        else:
            i = data['videos'][0]["video_files"][0]
            print("duration:", data['videos'][0]["duration"], 'file_type:', i['file_type'], 'width:', i['width'], 'height:', i['height'], 'link', i['link'])
            return i['link'], clip_type.Video

    except subprocess.CalledProcessError as e:
        print("Node.js 脚本运行出错：", e.stderr)
        return None, clip_type.Default        
    except json.JSONDecodeError:
        print("JSON 解析失败，输出内容为：", output)
        return None, clip_type.Default
    


"""
download_video()
从一个可直接下载的视频 URL 下载视频到本地路径

:param video_url: 视频的直接下载链接（如 https://example.com/video.mp4）
:param save_path: 本地完整保存路径（包括文件名，如 D:/Videos/myvideo.mp4）
"""
def download_video(video_url: str, save_path: str):

    try:
        # 发起请求，开启流式下载
        with requests.get(video_url, stream=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get('Content-Length', 0))  # 获取总大小

            # 设置进度条
            progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(save_path))

            # 写入文件
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))

            progress_bar.close()
            print(f"视频下载完成：{save_path}")

    except Exception as e:
        print(f"视频下载失败：{e}")
