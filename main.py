from config import *
from utils.text import *

# 生成文案
result = one_round_chat(TextConfig.message_system, TextConfig.message_user, TextConfig.max_tokens,
               TextConfig.temperature, TextConfig.frequency_penalty, TextConfig.max_retries)

print(result)