from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips
from moviepy.audio.AudioClip import AudioClip
import numpy as np

def replace_video_audio(video_path, audio_path, output_path):
    # 加载视频
    video = VideoFileClip(video_path).without_audio()
    
    # 加载音频
    audio = AudioFileClip(audio_path)
    
    # 如果音频比视频长，截断音频
    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)
    else:
        # 如果音频短，创建静音clip
        silence_duration = video.duration - audio.duration
        
        # 创建一个静音的AudioClip
        silence = AudioClip(
            make_frame=lambda t: np.zeros((1,)), 
            duration=silence_duration
        ).set_fps(audio.fps)
        
        # 拼接原音频 + 静音
        audio = concatenate_audioclips([audio, silence])
    
    # 把新音频设置到视频上
    final_video = video.set_audio(audio)
    
    # 输出文件
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
