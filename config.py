class SSML:
    cn_ssml = """<speak version='1.0' xml:lang='zh-CN' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts'>
        <voice name='{}'>
            {}
        </voice>
    </speak>"""

    @staticmethod
    def get_ssml(language):
        if language == 'CN':
            return SSML.cn_ssml

class setting:
    api_key = 'sMRVov2H54O4QhQ73JDqC9Fv' # 大模型 
    secret_key = 'II9aR0bALfmm49TBaPvx4hlCAOIXcTYP' # 大模型 