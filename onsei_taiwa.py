# -*- coding: utf-8 -*-

import requests
import json
from pydub import AudioSegment
from pydub.playback import play
import os


# APIのKEY
APIKEY = 'YOUR API KEY'

# 音声ファイルを保存するための一時ファイル
tmp_filename = "tmp.aac"


# 自然対話のappIdの取得
def getappId():
    # ユーザー情報を登録するためのエンドポイントの設定
    endpoint = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/registration'

    # 登録リクエストのヘッダとリクエストボディの設定
    payload = {"APIKEY" : APIKEY}
    headers = {"Content-type": "application/json;charset=UTF-8"}
    payload_json = {"botId" : "Chatting", "appKind": "0"}

    # 登録リクエストの送信
    r = requests.post(endpoint, headers=headers, params=payload, data=json.dumps(payload_json))
    data = r.json()
    return data["appId"]


# 対話テキストの取得
def requests_dialogtext(appId, text):
    # 自然対話appId登録のエンドポイント
    endpoint = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/dialogue'

    # リクエストのヘッダとパラメータとリクエストボディの設定
    headers = {"Content-type": "application/json;charset=UTF-8"}
    payload = {"APIKEY" : APIKEY}
    payload_json = {"language" : "ja-JP", \
                    "botId" : "Chatting", \
                    "appId" : appId, \
                    "voiceText" : text,\
                    "appRecvTime":"YYYY-MM-DD hh:mm:ss", \
                    "appSendTime":"YYYY-MM-DD hh:mm:ss"}

    # リクエストの送信
    r = requests.post(endpoint, headers=headers, params=payload, data=json.dumps(payload_json))
    data = r.json()

    return data["systemText"]["expression"]


# 音声の取得
def requests_voicedata(text):
    # 音声APIのエンドポイント
    endpoint = 'https://api.apigw.smt.docomo.ne.jp/crayon/v1/textToSpeech'

    # リクエストのヘッダとパラメータとリクエストボディの設定
    headers = {"Content-type": "application/json;charset=UTF-8"}
    payload = {"APIKEY" : APIKEY}
    payload_json = {"Command" : "AP_Synth", \
                    "SpeakerID" : "1", \
                    "StyleID" : "1", \
                    "PowerRate" : "5.00", \
                    "AudioFileFormat":"0", \
                    "TextData" : text}

    # リクエストの送信
    r = requests.post(endpoint, headers=headers, params=payload, data=json.dumps(payload_json))

    return r


if __name__ == '__main__':

    appId = getappId()

    while True:
        text = input(">>")

        response_text = requests_dialogtext(appId, text)

        r = requests_voicedata(response_text)

        # 一時ファイルへ書き込み
        if r.status_code == 200:
            with open(tmp_filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=256):
                    fd.write(chunk)

        # 応答のテキスト表示
        print("AIちゃん: {0}".format(response_text))

        # 一時ファイルから再生
        aac_version = AudioSegment.from_file(tmp_filename, "aac")
        play(aac_version)

        # 一時ファイルの削除
        os.remove(tmp_filename)
