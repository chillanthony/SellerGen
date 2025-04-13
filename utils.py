import requests
import json
import os
import cv2
import time
import random
import subprocess
import numpy as np
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
from moviepy.editor import *
from openai import OpenAI
from config import *

# 生成文案的类
def text_gen_patriot():
    text = ""

    # 起因
    prompt = "请你为我写一段话，讲述中国在历史上因为实力不够而在外交上受到不公正待遇的事件，不需要描述现在中国的情况，要求长度两百字左右，生动形象，细节丰富"
    result = baidu_call(prompt)
    text += result
    text += '\n\n'

    # 经过
    prompt = "请你为我写一段话，介绍钱学森为两弹一星作出贡献的事迹，要求长度四百字左右，生动形象，细节丰富"
    result = baidu_call(prompt)
    text += result
    text += '\n\n'

    # 其他
    prompt = "请你为我写一段话，讲述两个具体人物（如航母设计师罗宁等人物）为国家做贡献的事迹，要求长度四百字左右，生动形象，细节丰富"
    result = baidu_call(prompt)
    text += result
    text += '\n\n'

    # 点题
    prompt = "请你为我写一段话，阐述中国当前的安定与和谐是由于国家脊梁的贡献，而现在的孩子却并不懂得向这些伟大人物学习这一观点，并在最后阐述国家脊梁对于国家的重要性，要求有理有据，二百字左右"
    result = baidu_call(prompt)
    text += result
    text += '\n\n'

    return text

def baidu_call(prompt):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token=" + get_access_token()
    
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    return response.json().get('result')

# 获得文心一言token
def get_access_token():
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
    api_key = setting.api_key
    secret_key = setting.secret_key
        
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
    
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

# 输入clip和输出路径 保存文件
def text_to_speech(text, output_path):

    # 创建语音配置
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))

    # 设置声音 速率 文案
    speech_synthesis_voice_name='zh-CN-YunxiNeural'

    # 创建合成器
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    # 创建ssml
    ssml = SSML.get_ssml(language="CN").format(speech_synthesis_voice_name, text)
    # print("SSML to synthesize: \r\n{}".format(ssml))

    # 合成音频
    speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml).get()

    # 保存至文档
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        # print("Speech synthesized for text [{}]".format(text))
        stream = speechsdk.AudioDataStream(speech_synthesis_result)
        stream.save_to_wav_file(output_path)
        # print('audio saved to:', output_path)
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

    print("音频生成成功")

# 获取音频文件的时长参数 duration ms
def get_audio_duration(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        duration = len(audio)
        return duration
    except Exception as e:
        print(f"获取音频时长失败: {e}")
        return None
    
def add_bgm(audio_path, bgm_begin_path, bgm_loop_path, output_path):

    # 读取音频
    audio = AudioSegment.from_file(audio_path)
    bgm_begin_audio = AudioSegment.from_file(bgm_begin_path)
    bgm_loop_audio = AudioSegment.from_file(bgm_loop_path)
    audio = audio
    bgm_begin_audio = bgm_begin_audio - 20
    bgm_loop_audio = bgm_loop_audio - 20

    # 裁剪音频
    start_ms = int(147 * 1000)
    end_ms = int(263 * 1000)
    bgm_audio = bgm_begin_audio[start_ms:end_ms]

    while len(bgm_audio) < len(audio):
        bgm_audio += bgm_loop_audio
    bgm_audio = bgm_audio[:len(audio)]

    audio = audio.overlay(bgm_audio)
    audio.export(output_path, format="mp3")

# 裁剪素材
def source_crop(video_path):
       
    video = cv2.VideoCapture(video_path)
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    video.release()

    if (width * 3/4 < height):
        x = 0
        y = (height - (width*3/4))/2
        width = width
        height = width * 3/4
    else:
        x = (width - (height*4/3))/2
        y = 0
        width = height*4/3
        height = height

    output_path = video_path[:-4] + "_cropped.mp4"

    clip = VideoFileClip(video_path)
    cropped_clip = clip.crop(x1 = x, y1 = y, width = width, height = height)
    resized_clip = cropped_clip.resize(width = 960, height = 720)

    resized_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

# 探究片段切换的时间点 输入视频路径 输出一个所有切片点时间戳的列表
def fragment_detection(video_path):

    fragment_list = [] 
    # 打开视频 每帧一个点 计算与上一帧图像的平均差值 输出视频总帧数
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # print('素材视频共有', total_frames, '帧')

    # 读取第一帧
    ret, frame = cap.read() 

    # 将图像数组改成16位以便进行处理
    frame = frame.astype(np.int16) 
    last_frame = frame

    # 遍历视频的每一帧
    frame_index = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 将图像数组改成16位以便进行处理
        frame = frame.astype(np.int16)

        # 计算相似度
        similarity = -np.mean(np.abs(frame - last_frame))

        if similarity < -40:
            fragment_list.append(frame_index)
        
        last_frame = frame
        frame_index += 1
    
    fragment_list.append(frame_index)


    # 去掉过于相近的时间戳 增加起始0
    new_lst = [0]
    for i in range(0, len(fragment_list)):
        if i == len(fragment_list) - 1:
            if abs(fragment_list[i] - new_lst[-1]) < 24:
                new_lst[-1] = fragment_list[i]
                continue
        if abs(fragment_list[i] - new_lst[-1]) >= 24:
            new_lst.append(fragment_list[i])

    return new_lst

# 找到视频某一帧的时间戳，输入视频路径和帧序号，返回时间戳
def get_frame_timestamp(video_path, frame_number):

    # 打开视频
    cap = cv2.VideoCapture(video_path)

    # 异常处理
    if not cap.isOpened():
        print("无法打开视频文件:", video_path)
        return None

    # 总帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    clip = VideoFileClip(video_path)
    duration = clip.duration
    timestamp = (frame_number/total_frames)*duration

    # 关闭窗口，返回时间戳
    cap.release()
    return round(timestamp, 3)

def save_list_to_txt(file_path, data_list):
    """
    将列表内容逐行写入 txt 文件。

    参数:
        file_path (str): 保存的 txt 文件路径。
        data_list (list): 要保存的列表。
    """
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            for item in data_list:
                file.write(f"{item}\n")
        print(f"列表已成功保存到 {file_path}")
    except Exception as e:
        print(f"保存列表时出错: {e}")

def read_numbers_from_txt(file_path):
    numbers_list = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                numbers_list.append(int(line.strip()))
        return numbers_list
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None

# 剪辑视频 时间戳单位ms
def video_clip(video_path, output_path, start_timestamp, end_timestamp):

    video = VideoFileClip(video_path)

    # 剪辑视频 并保存
    videoclip = video.subclip(start_timestamp/1000, end_timestamp/1000)
    videoclip.write_videofile(output_path, codec="libx264", audio_codec="aac")

def concatenate_videos(input_paths, output_path):
    # 创建一个包含所有视频剪辑的列表
    clips = [VideoFileClip(path) for path in input_paths]
    
    # 将所有视频剪辑按顺序连接在一起
    final_clip = concatenate_videoclips(clips)
    
    # 将结果写入输出文件
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    # 释放资源
    for clip in clips:
        clip.close()
    final_clip.close()

def add_black_bars_to_9_16(input_file, output_file):
    
    try:
        # 加载视频
        clip = VideoFileClip(input_file)

        # 获取原始视频的宽高
        original_width, original_height = clip.size

        # 目标高度按 9:16 计算
        target_height = int(original_width * 16 / 9)

        # 计算需要添加的黑边高度
        if target_height > original_height:
            padding = (target_height - original_height) // 2
        else:
            raise ValueError("输入视频比例不符合 4:3，或分辨率已为 9:16")

        # 添加黑边
        clip_with_bars = clip.margin(top=padding, bottom=padding, color=(0, 0, 0))

        # 导出新视频
        clip_with_bars.write_videofile(output_file, codec="libx264", audio_codec="aac")
        print(f"视频成功保存至: {output_file}")
    except Exception as e:
        print(f"处理视频时出错: {e}")

def add_audio_to_video(video_file, new_audio_file, output_file, video_volume=0.5):
    """
    将新的音轨添加到视频中，并降低原视频的音量。

    参数:
        video_file (str): 输入视频文件路径。
        new_audio_file (str): 新的音频文件路径。
        output_file (str): 输出合成后的视频文件路径。
        video_volume (float): 原视频音量的比例（0.0-1.0）。
    """
    try:
        # 加载视频和新音频
        video_clip = VideoFileClip(video_file)
        new_audio = AudioFileClip(new_audio_file)

        # 设置新音频为视频音频
        video_with_audio = video_clip.set_audio(new_audio)

        # 导出最终视频
        video_with_audio.write_videofile(output_file, codec="libx264", audio_codec="aac")
        print(f"视频与音频合成成功！输出文件保存至: {output_file}")
    except Exception as e:
        print(f"合成时出错: {e}")

# 指定源视频路径，提取帧序号，输出路径，将视频帧提取到输出路径
def extract_frame(video_path, frame_number, output_path):

    ffmpeg_cmd = f'ffmpeg -i {video_path} -vf "select=gte(n\,{frame_number})" -color_range pc -vframes 1 {output_path} -loglevel quiet'
    subprocess.call(ffmpeg_cmd, shell=True)

    # print('提取了视频', video_path, '的第', frame_number, '帧')
    # print('图像输出路径为', output_path)


def extract_audio_from_video(video_file, output_audio_file):
    """
    提取视频的音轨并保存为音频文件。

    参数:
        video_file (str): 输入视频文件路径。
        output_audio_file (str): 输出音频文件路径。
    """
    try:
        # 加载视频
        video_clip = VideoFileClip(video_file)

        # 检查视频是否包含音频
        if video_clip.audio is None:
            print("输入视频中不包含音频轨道。")
            return

        # 提取音频并保存
        video_clip.audio.write_audiofile(output_audio_file)
        print(f"音轨提取成功！音频文件保存至: {output_audio_file}")
    except Exception as e:
        print(f"提取音轨时出错: {e}")


def replace_audio_in_video(video_file, new_audio_file, output_file):
    """
    替换视频的音轨为新的音轨。

    参数:
        video_file (str): 输入视频文件路径。
        new_audio_file (str): 新的音频文件路径。
        output_file (str): 输出替换音轨后的视频文件路径。
    """
    try:
        # 加载视频文件
        video_clip = VideoFileClip(video_file)

        # 加载新的音频文件
        new_audio = AudioFileClip(new_audio_file)

        # 将新的音频设置到视频上
        video_with_new_audio = video_clip.set_audio(new_audio)

        # 导出最终视频
        video_with_new_audio.write_videofile(output_file, codec="libx264", audio_codec="aac")
        print(f"音轨替换成功！输出文件保存至: {output_file}")
    except Exception as e:
        print(f"替换音轨时出错: {e}")

def replace_video_segment(original_video, replacement_video, start_time, end_time, output_file):
    """
    将原视频的指定时间段替换为另一个视频。

    参数:
        original_video (str): 原视频文件路径。
        replacement_video (str): 替换视频文件路径。
        start_time (float): 替换开始时间（秒）。
        end_time (float): 替换结束时间（秒）。
        output_file (str): 输出视频文件路径。
    """
    try:
        # 加载原视频和替换视频
        original_clip = VideoFileClip(original_video)
        replacement_clip = VideoFileClip(replacement_video)

        # 截取原视频的两部分
        before_clip = original_clip.subclip(0, start_time)  # 开头部分
        after_clip = original_clip.subclip(end_time, original_clip.duration)  # 结尾部分

        # 截取替换视频的所需时长（若替换视频时间不足，按其完整时长替换）
        replacement_clip = replacement_clip.subclip(start_time, end_time)

        # 拼接视频片段
        final_clip = concatenate_videoclips([before_clip, replacement_clip, after_clip])

        # 导出最终视频
        final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")
        print(f"视频片段替换成功！输出文件保存至: {output_file}")
    except Exception as e:
        print(f"替换视频片段时出错: {e}")

def find_cyberhuman(video_path):

    # 读取数字人帧
    video = cv2.VideoCapture(video_path)
    video.set(cv2.CAP_PROP_POS_FRAMES, 1)
    ret, template = video.read()
    video.release()

    # 打开视频 获取视频的size 然后resize
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    template = cv2.resize(template,(width, height))

    # 将模板存储数据的格式从8位改成16位 以便进行计算
    template = template.astype(np.int16)  

    # 遍历视频的每一帧 获取数字人出现的时间列表
    frame_index = 0
    result_list = []
    ctr = False
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 将图像数组改成16位以便进行处理
        frame = frame.astype(np.int16)

        similarity = -np.mean(np.abs(frame - template))
        # print(frame_index, similarity)

        if similarity > -20 and not ctr:
            start = frame_index
            ctr = True
        
        if similarity < -20 and ctr:
            end = frame_index
            ctr = False
            result_list.append((start, end))

        frame_index += 1

    # 释放视频捕获
    cap.release()

    if ctr:
        result_list.append((start, frame_index-1))


    return result_list

def merge_list(fragment_list, cyberhuman_list):
    
    cyber_list = []
    for i in cyberhuman_list:
        fragment_list.append(i[0])
        fragment_list.append(i[1])
        cyber_list.append(i[0])
        cyber_list.append(i[1])
    fragment_list.sort()

    unique_list = []
    [unique_list.append(item) for item in fragment_list if item not in unique_list]

    for i in unique_list:
        for j in cyberhuman_list:
            if i < j[1] and i > j[0]:
                unique_list.remove(i)
    
    new_lst = []
    for i in range(0,len(unique_list)):
        if i == 0 or i == len(unique_list)-1 or unique_list[i] in cyber_list:
            new_lst.append(unique_list[i])
            continue
        elif unique_list[i+1] - unique_list[i] >= 24 and unique_list[i] - unique_list[i-1] >= 24:
            new_lst.append(unique_list[i])

    result_list = []
    for i in range(0, len(new_lst)-1):
        result_list.append((new_lst[i], new_lst[i+1])) 

    return result_list

def find_similarity(raw_video_path, frame_number, material_list):
    
    similarity_list = []
    # 读取需要匹配帧
    video = cv2.VideoCapture(raw_video_path)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, template = video.read()
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    template = cv2.resize(template,(width, height))
    template = template.astype(np.int16)  
    video.release()

    for i in material_list:
        video = cv2.VideoCapture(i[0])
        video.set(cv2.CAP_PROP_POS_FRAMES, i[1][0])
        ret, frame= video.read()
        frame = cv2.resize(frame,(width, height))       
        frame = frame.astype(np.int16)
        similarity = -np.mean(np.abs(frame - template))
        similarity_list.append(similarity)
        video.release() 
    return similarity_list
                          
def make_video(clip_list, output_path):
    clips = []
    for i in clip_list:
        videoclip = VideoFileClip(i[0])
        clip = videoclip.subclip(i[1][0], i[1][1])
        clips.append(clip)

    final_clip = concatenate_videoclips(clips)
    
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

def replace_audio(raw_video_path, input_path, output_path):
    videoclip = VideoFileClip(raw_video_path)
    audio_path = "a.mp3"
    videoclip.audio.write_audiofile(audio_path)

    outclip = VideoFileClip(input_path)
    audio = AudioFileClip(audio_path)
    if audio.duration > outclip.duration:
        # 如果音频比视频长，则裁剪音频
        audio = audio.subclip(0, outclip.duration)
    else:
        # 如果音频比视频短，则补齐静音
        silence_duration = outclip.duration - audio.duration
        silence = AudioFileClip.silent(duration=silence_duration)
        audio = audio.set_duration(audio.duration + silence_duration).fx(
            lambda gf, t: gf(t) if t < audio.duration else 0
        )

    # 替换视频的音轨
    video_with_new_audio = outclip.set_audio(audio)
    video_with_new_audio.write_videofile(output_path, codec="libx264", audio_codec="aac") 

    os.remove(audio_path)

def generate_clip(result_list, cyberhuman_list, material_list, raw_video_path, cyberhuman_path):    

    # 获取需要替换为数字人的片段的索引
    index_list = []
    for i in cyberhuman_list:
        index_list.append(result_list.index(i))
    print("一共有", len(result_list), "个片段")
    print("需要替换为数字人的片段索引", index_list)

    # 获取要替换为素材的片段的索引
    replace_list = []
    replace_list.append((0, index_list[0]))
    for i in range(0, len(index_list)-1):
        replace_list.append((index_list[i]+1, index_list[i+1]-index_list[i]-1))
    replace_list.append((index_list[len(index_list)-1]+1, len(result_list) - index_list[len(index_list)-1]-1))
    
    acc_time = 0
    # 获取最终视频的所有片段列表
    clip_list = []
    for i in range(len(replace_list)):

        # 片尾
        if i == len(replace_list)-1 and replace_list[i][1] == 0:
            continue

        # 获取匹配时间长度
        if i == len(replace_list)-1:
            start_time = get_frame_timestamp(raw_video_path, result_list[replace_list[i][0]][0])
            end_time = get_frame_timestamp(raw_video_path, result_list[len(result_list)-1][1])      
        else:
            start_time = get_frame_timestamp(raw_video_path, result_list[replace_list[i][0]][0])
            end_time = get_frame_timestamp(raw_video_path, result_list[replace_list[i][0]+replace_list[i][1]][0])
        total_time = end_time - start_time
        print(i, "从第", replace_list[i][0],"个片段开始的", replace_list[i][1], "个片段，总时长为", total_time)

        # 匹配中间片段
        time = 0
        for j in range(replace_list[i][0], replace_list[i][0] + replace_list[i][1]):

            # 找到相似的片段 准备数据
            similarity_list = find_similarity(raw_video_path, result_list[j][0], material_list)
            sorted_indices = sorted(range(len(similarity_list)), key=lambda i: similarity_list[i], reverse=True)
            top_10_indices = sorted_indices[:10]
            integer_number = random.randint(1, 9)
            float_number = random.uniform(0, 1)

            # 有概率穿插数字人片段
            if float_number > 0.8:
                print("cyber")
                clip_start_time = get_frame_timestamp(raw_video_path, result_list[j][0])
                clip_end_time = get_frame_timestamp(raw_video_path, result_list[j][1])
                clip_time = clip_end_time - clip_start_time
                if time + clip_time > total_time:
                    clip_start_time = get_frame_timestamp(raw_video_path, result_list[replace_list[i][0]][0]) + time
                    if i == len(index_list):
                        clip_end_time = get_frame_timestamp(raw_video_path, result_list[-1][1])
                    else:
                        clip_end_time = get_frame_timestamp(raw_video_path, result_list[index_list[i]][0])
                    time += clip_end_time - clip_start_time
                    acc_time += clip_end_time - clip_start_time
                    print(cyberhuman_path, clip_start_time, clip_end_time, clip_end_time - clip_start_time, time, acc_time)                    
                    clip_list.append((cyberhuman_path, (clip_start_time, clip_end_time)))
                    break
                time += clip_end_time - clip_start_time
                acc_time += clip_end_time - clip_start_time
                print(cyberhuman_path, clip_start_time, clip_end_time, clip_end_time - clip_start_time, time, acc_time)
                clip_list.append((cyberhuman_path, (clip_start_time, clip_end_time)))
            # 有概率穿插素材片段
            else:
                print("material")
                clip_start_time = get_frame_timestamp(material_list[top_10_indices[integer_number]][0], material_list[top_10_indices[integer_number]][1][0])
                clip_end_time = get_frame_timestamp(material_list[top_10_indices[integer_number]][0], material_list[top_10_indices[integer_number]][1][1])
                clip_time = clip_end_time - clip_start_time
                if time + clip_time > total_time:                  
                    clip_start_time = get_frame_timestamp(raw_video_path, result_list[replace_list[i][0]][0]) + time
                    if i == len(index_list):
                        clip_end_time = get_frame_timestamp(raw_video_path, result_list[-1][1])
                    else:
                        clip_end_time = get_frame_timestamp(raw_video_path, result_list[index_list[i]][0])
                    time += clip_end_time - clip_start_time
                    acc_time += clip_end_time - clip_start_time
                    print(cyberhuman_path, clip_start_time, clip_end_time, clip_end_time - clip_start_time, time, acc_time)
                    clip_list.append((cyberhuman_path, (clip_start_time, clip_end_time)))
                    break
                time += clip_end_time - clip_start_time
                acc_time += clip_end_time - clip_start_time
                print(material_list[top_10_indices[integer_number]][0], clip_start_time, clip_end_time, clip_end_time - clip_start_time, time, acc_time)
                clip_list.append((material_list[top_10_indices[integer_number]][0], (clip_start_time, clip_end_time)))
        
        # 将要替换的数字人片段加入总片段列表
        if i < len(replace_list) - 1:
            clip_start_time = start_time + time
            clip_end_time = get_frame_timestamp(raw_video_path, result_list[index_list[i]][1])
            acc_time += clip_end_time - clip_start_time
            print(cyberhuman_path, clip_start_time, clip_end_time, clip_end_time - clip_start_time, acc_time)
            clip_list.append((cyberhuman_path, (clip_start_time, clip_end_time)))
    return clip_list   

# 沿边缘顺时针滚动
def clockwise_border(frame_width, frame_height, window_width, window_height, speed):
    positions = []
    for x in range(0, frame_width - window_width + 1, speed):
        positions.append((x, 0))
    for y in range(speed, frame_height - window_height + 1, speed):
        positions.append((frame_width - window_width, y))
    for x in range(frame_width - window_width - speed, -1, -speed):
        positions.append((x, frame_height - window_height))
    for y in range(frame_height - window_height - speed, 0, -speed):
        positions.append((0, y))
    return positions

# 沿边缘顺时针滚动
def counter_clockwise_border(frame_width, frame_height, window_width, window_height, speed):
    positions = []
    for y in range(0, frame_height - window_height + 1, speed):
        positions.append((0, y))
    for x in range(speed, frame_width - window_width + 1, speed):
        positions.append((x, frame_height - window_height))
    for y in range(frame_height - window_height - speed, -1, -speed):
        positions.append((frame_width - window_width, y))
    for x in range(frame_width - window_width - speed, 0, -speed):
        positions.append((x, 0))
    return positions

# 顺时针旋转滚动
def clockwise_rotation(frame_width, frame_height, window_width, window_height, speed):

    def generate_ellipse_points(a, b, num_points):
        angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)  # 生成均匀分布的角度
        points = [(a * np.cos(theta), b * np.sin(theta)) for theta in angles]
        return points
    
    a = max(frame_width - window_width, frame_height - window_height) / 2
    b = min(frame_width - window_width, frame_height - window_height) / 2
    l = 2 * np.pi * a + 4 * (a - b)
    num_points = int(l / speed)

    points = generate_ellipse_points(a, b, num_points)
    positions = [(int(x[1] + (frame_width - window_width)/2), int(x[0] + (frame_height - window_height)/2)) for x in points]
    return positions

# 逆时针旋转滚动
def counter_clockwise_rotation(frame_width, frame_height, window_width, window_height, speed):

    def generate_ellipse_points(a, b, num_points):
        angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)  # 生成均匀分布的角度
        points = [(a * np.cos(theta), b * np.sin(theta)) for theta in angles]
        return points
    
    a = max(frame_width - window_width, frame_height - window_height) / 2
    b = min(frame_width - window_width, frame_height - window_height) / 2
    l = 2 * np.pi * a + 4 * (a - b)
    num_points = int(l / speed)

    points = generate_ellipse_points(a, b, num_points)
    positions = [(int(x[1] + (frame_width - window_width)/2), int(x[0] + (frame_height - window_height)/2)) for x in points]
    return positions[::-1]

def video_movement(input_path, output_path, scale = (0.8, 0.8), rotation = clockwise_border, speed = 10):

    # 读入视频
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return
    
    # 读入长宽帧率
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # 设置window大小
    window_width = int(frame_width * scale[0])
    window_height = int(frame_height * scale[1])
    
    # 输出视频的设置
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (window_width, window_height))
    
    # 生成位置列表 窗口左上角所在位置(x, y)
    positions = rotation(frame_width, frame_height, window_width, window_height, speed)
    
    # 生成运镜视频
    frame_count = 0
    while cap.isOpened():

        # 读入帧
        ret, frame = cap.read()
        if not ret:
            break
        
        # 设置帧内容为窗口内容
        position = positions[frame_count % len(positions)]
        x, y = position
        window = frame[y:y+window_height, x:x+window_width]
    
        # 输出到新视频
        out.write(window)
        frame_count += 1
    
    # 释放资源 打印信息
    cap.release()
    out.release()
    print("运镜后的视频已经生成，输出路径为：", output_path)


def one_round_chat(message_system, message_user, max_tokens_ = 4096, temperature_ = 1, frequency_penalty_ = 0, max_retries = 5):

    api_key = "sk-10a792d19e6d4027b4be140a202674e8"
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    for i in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": message_system},
                    {"role": "user", "content": message_user},
                ],
                max_tokens = max_tokens_,
                temperature = temperature_,
                frequency_penalty = frequency_penalty_,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"请求失败 ({i+1}/{max_retries}): {e}")
            time.sleep(2)
    return "请求失败"