import jieba.analyse
import subprocess
import json
import os
import requests
from tqdm import tqdm
from deep_translator import GoogleTranslator
from moviepy.editor import VideoFileClip, concatenate_videoclips
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
        print(i+1, '/', len(clip_list))
        # 提取热词
        hotword = hotword_generation(clip_list[i])
        clip_list[i].hotword = hotword

        # 获取资源
        url, tp = call_pexels(clip_list[i])
        clip_list[i].url = url
        clip_list[i].type = tp
        clip_list[i].path = os.path.join(src_folder, str(i+1) + '.mp4')

        # 下载视频
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
    else:
        hotword = 'NaN'
    
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

        # 假如没有结果，就用默认关键词
        if data['total_results'] == 0:
            result = subprocess.run(
                ['node', 'js/video.js', 'crowd'],
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout.strip()
            data = json.loads(output)         
        
        # 选择时长最短的视频
        duration_list = []
        for j in data['videos']:
            duration_list.append(j['duration'])
        id = duration_list.index(min(duration_list))
        i = data['videos'][id]["video_files"][0]
        print("duration:", data['videos'][id]["duration"], 'file_type:', i['file_type'], 'width:', i['width'], 'height:', i['height'], 'link', i['link'])
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

'''
prepare_clip()
调整素材大小，加黑边，调节帧率
clip:moviepy的subclip类
'''
def prepare_clip(clip):
    # 调整宽度到720，保持纵横比例
    clip = clip.resize(width=720)
    
    # 创建一个720x1280的黑色背景，并把clip放到中间
    clip = clip.on_color(
        size=(720, 1280),     # 画布尺寸
        color=(0, 0, 0),      # 背景颜色（黑色）
        pos=("center", "center")  # 居中
    )
    
    # 可选：统一帧率
    clip = clip.set_fps(30)
    
    return clip

'''
get_video_duration()
获取视频时长
video_path: 视频路径
'''
def get_video_duration(video_path):

    # 载入视频
    clip = VideoFileClip(video_path)

    # 获取时长（单位：秒）
    return clip.duration

'''
video_generation()
输入片段列表，输出路径，拼接视频
clip_list: 视频片段列表
video_path: 视频输出路径
'''
def video_generation(clip_list, video_path):

    vid_list = []
    for i in range(len(clip_list)):
        duration = clip_list[i].duration/1000
        duration_content = get_video_duration(clip_list[i].path)

        # 素材太短时循环素材
        while duration_content < duration:
            clip = VideoFileClip(clip_list[i].path).subclip(0, duration_content)
            clip = prepare_clip(clip)
            vid_list.append(clip)
            duration -= duration_content
        
        # 调整片段，加入时间线
        clip = VideoFileClip(clip_list[i].path).subclip(0, duration)
        clip = prepare_clip(clip)
        vid_list.append(clip)
    
    # 拼接 导出
    final_clip = concatenate_videoclips(vid_list)
    final_clip.write_videofile(video_path)

