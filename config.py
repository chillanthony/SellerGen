'''
文案的设置
message_system: 背景信息
message_user: 用户的请求
max_tokens: 最大输入token（超过时截断） default = 4096
temperature (0, 2): 模型发散性 default = 1
frequency_penalty (-2, 2): 请求与回复的不一致性 default = 0
max_retries: 最大尝试次数（连接失败） default = 5
'''

class TextConfig:

    def __init__(self, message_system, message_user, max_tokens = 4096, temperature = 1, frequency_penalty = 0, max_retries = 5):
        self.message_system = message_system
        self.message_user = message_user
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.frequency_penalty = frequency_penalty
        self.max_retries = 5
        

'''
声音的设置
voice_name: 声音的名字 https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/language-support?tabs=
audio_path: 音频输出路径
'''
class TTSConfig:

    def __init__(self, voice_name, text, audio_path):
        
        ssml = """
        <speak version='1.0' xml:lang='zh-CN' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts'>
        <voice name='{}'>
            {}
        </voice>
        </speak>
        """
        self.ssml = ssml.format(voice_name, text)
        self.audio_path = audio_path
    
message_system_text_generation = '''

## 角色设定
你是一名资深软文创作专家，擅长用「悬念设问+故事共鸣+价值升华」的三段式结构撰写传播性极强的文案。请严格按以下框架创作：

## 核心指令

**1. 开头设问句（1-2句）**  
- 要求：使用「认知冲突法」或「数据冲击法」制造悬念    

**2. 主题叙述（约600字）**
- 可以叙述一个或多个围绕主题展开的新闻或故事
- 必须包含要素：  
    - 冲突
    - 转折  

**3. 反思升华（约200字）**  
- 必须达成：  
- 关联社会现象 
- 行动暗示  
- 禁忌：  
- 出现"购买""下单"等推销词汇

**4. 回归主题（约200字）**
- 歌颂中国近现代众多历史人物的伟大
- 包括政治家，科学家，人民等
- 用词优美

注意：输出的文案中不含其他副标题，如“开头设问句”“主题故事”，也不包含'*'等特殊字符，只保留纯文稿，使用中文标点符号（全角）。

'''

message_user_text_generation_prompt = "请你为我写一段文案，主题故事是"

message_system_hotword_prompt = '''
## 角色设定
    你是一个热词提取助手

## 核心任务
    我会向你输入一句中文短句，你的任务是提取这句话中最关键的一个词汇，并将它翻译成英文
    你的输出有且仅有一个英文单词

'''

tts_voice_name = 'zh-CN-YunxiNeural'