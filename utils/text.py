from openai import OpenAI
import time

''' 
one_round_chat()
向deepseek发出请求并返回
message_system: 背景信息
message_user: 用户的请求
max_tokens: 最大输入token（超过时截断） default = 4096
temperature (0, 2): 模型发散性 default = 1
frequency_penalty (-2, 2): 请求与回复的不一致性 default = 0
max_retries: 最大尝试次数（连接失败） default = 5
'''
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