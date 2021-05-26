import json
import requests
from flask import Flask, request, abort, make_response, jsonify

import os
import jieba
import jieba.analyse
from gensim.models import Word2Vec
import gensim
import numpy as np
from scipy.linalg import norm
import heapq
import csv

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
SECRET = os.environ.get('SECRET')

line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)




model = Word2Vec.load('20180309wiki_model.bin')

s = []

questiontext=[]
answertext=[]
with open('qa_set.csv', newline='',encoding='utf-8') as csvfile:

  # 讀取 CSV 檔案內容
    rows = csv.reader(csvfile)

  # 以迴圈輸出每一列
    for row in rows:

        questiontext.append(row[0])
        answertext.append(row[1])

def input_button1(question):
    max_score=0
    answer_history=[]
    for i in questiontext:
        temp=vector_similarity(question,i)
        answer_history.append(temp)
        #if temp>max_score:
        #    max_score=temp
        #    answer_output=answertext[questiontext.index(i)]
        #print(i)

    
    
    score_5=heapq.nlargest(5,answer_history)
    print(score_5)
    for i in range(len(score_5)):

        for j in range(len(answer_history)):
            if answer_history[j]==score_5[i]:
                if score_5[i]<0.3:  #這裡可以更改信心分數下限
                    answer_output="沒有找到匹配的答案"
                    break
                else:
                    answer_output=answertext[j]
                    print(questiontext[j])
                    print(answer_output)
        
        
        return answer_output

def vector_similarity(s1, s2):
    def sentence_vector(s):
        words = jieba.lcut(s)
        v = np.zeros(250)
        for word in words:
            if word in model.wv.vocab:
                v += model[word]
            else:
                word= np.zeros((model.vector_size), dtype=np.float32)
        v /= len(words)
        return v


    v1, v2 = sentence_vector(s1), sentence_vector(s2)
    return np.dot(v1, v2) / (norm(v1) * norm(v2))

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=(ImageMessage, TextMessage))
def handle_message(event):
    #get取的訊息
    get = event.message.text
    ans=input_button1(get)
    line_bot_api.reply_message(event.reply_token,ans)



if __name__ == "__main__":
    app.run(port=8000)