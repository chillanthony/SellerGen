import os
import azure.cognitiveservices.speech as speechsdk

'''
WordBoundaryData
分字数据结构
boundary_type: word, punctuation, sentence 类型enum
audio_offset: 该文本开始时的时间偏移 类型float 单位ms
duration: 该文本的持续时长 类型float 单位ms
text: 文本内容 类型str
text_offset: 文本开始时的偏移量（相对位置） 类型int
word_length: 文本长度 类型int
'''
class WordBoundaryData:
    
    def __init__(self, boundary_type, audio_offset, duration, text, text_offset, word_length):
        self.boundary_type = boundary_type
        self.audio_offset = audio_offset
        self.duration = duration
        self.text = text
        self.text_offset = text_offset
        self.word_length = word_length
    
    def __str__(self):
        return f"Boundary type:{self.boundary_type}\nAudio offset:{self.audio_offset}\nDuration:{self.duration}\nText:{self.text}\nText offset:{self.text_offset}\nWord length:{self.word_length}\n"

'''
SentenceBoundaryData
分句数据结构
audio_offset: 句子开始时的时间偏移
text: 句子内容
'''
class SentenceBoundaryData:

    def __init__(self, audio_offset, text):
        self.audio_offset = audio_offset
        self.text = text
    
    def __str__(self):
        return f"Audio offset:{self.audio_offset}\nText:{self.text}"

'''
text_to_speech()
将文字转化为语音，保存在某一路径中
返回值word_boundary_list分字列表
ssml: 格式化字符串
output_path: 输出路径
'''
def text_to_speech(ssml, output_path):

    # Define global data structure
    word_boundary_list = []

    # Define event function
    def speech_synthesizer_synthesis_canceled_cb(evt: speechsdk.SessionEventArgs):
        print('SynthesisCanceled event')

    def speech_synthesizer_synthesis_completed_cb(evt: speechsdk.SessionEventArgs):
        print('SynthesisCompleted event:')
        print('\tAudioData: {} bytes'.format(len(evt.result.audio_data)))
        print('\tAudioDuration: {}'.format(evt.result.audio_duration))

    def speech_synthesizer_synthesis_started_cb(evt: speechsdk.SessionEventArgs):
        print('SynthesisStarted event')

    def speech_synthesizer_word_boundary_cb(evt: speechsdk.SessionEventArgs):
        # print('WordBoundary event:')
        # print('\tBoundaryType: {}'.format(evt.boundary_type))
        # print('\tAudioOffset: {}ms'.format((evt.audio_offset + 5000) / 10000))
        # print('\tDuration: {}'.format(evt.duration))
        # print('\tText: {}'.format(evt.text))
        # print('\tTextOffset: {}'.format(evt.text_offset))
        # print('\tWordLength: {}'.format(evt.word_length))
        word_boundary_list.append(WordBoundaryData(evt.boundary_type, (evt.audio_offset + 5000) / 10000, evt.duration.microseconds / 1000, evt.text, evt.text_offset, evt.word_length))


    # Set speech config
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceResponse_RequestSentenceBoundary, value='true')
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    # Subscribe to events
    speech_synthesizer.synthesis_canceled.connect(speech_synthesizer_synthesis_canceled_cb)
    speech_synthesizer.synthesis_completed.connect(speech_synthesizer_synthesis_completed_cb)
    speech_synthesizer.synthesis_started.connect(speech_synthesizer_synthesis_started_cb)
    speech_synthesizer.synthesis_word_boundary.connect(speech_synthesizer_word_boundary_cb)

    speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        stream = speechsdk.AudioDataStream(speech_synthesis_result)
        stream.save_to_wav_file(output_path)
        print('audio saved to:', output_path)
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
    
    return word_boundary_list

'''
to_separated_sentence()
输入这个音轨的分字列表
返回这个音轨的分句列表（按标点）
word_boundary_list: 这个音轨的分字列表
'''
def to_separated_sentence(word_boundary_list):

    sentence_list = []

    sentence = ''
    offset_list = []
    for i in word_boundary_list:
        if i.boundary_type == speechsdk.SpeechSynthesisBoundaryType.Word:
            sentence += i.text
            offset_list.append(i.audio_offset)
        if i.boundary_type == speechsdk.SpeechSynthesisBoundaryType.Punctuation:
            sentence_list.append(SentenceBoundaryData(min(offset_list), sentence))
            sentence = ''
            offset_list.clear()
    
    return sentence_list

'''
to_subtitle()
输入这个音轨的分字列表
返回这个音轨的字幕列表（按长度）
word_boundary_list: 这个音轨的分字列表
'''
def to_subtitle(word_boundary_list):

    subtitle_list = []

    sentence = ''
    offset_list = []
    for i in word_boundary_list:
        if i.boundary_type == speechsdk.SpeechSynthesisBoundaryType.Word or i.boundary_type == speechsdk.SpeechSynthesisBoundaryType.Punctuation:
            if len(sentence + i.text) > 12 and i.boundary_type == speechsdk.SpeechSynthesisBoundaryType.Word:
                subtitle_list.append(SentenceBoundaryData(min(offset_list), sentence))
                sentence = ''
                offset_list.clear()
            sentence += i.text
            offset_list.append(i.audio_offset)
    
    if len(offset_list) > 0:
        subtitle_list.append(SentenceBoundaryData(min(offset_list), sentence))
    
    return subtitle_list

