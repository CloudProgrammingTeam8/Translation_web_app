from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render ,render_to_response
from .GTAPI import GTTS   # Google Translate Text To Speech
from .speechrecogition_example import SpeechRecogition  # SpeechRecogition
from .models import *
import boto3
import time

# Create your views here.
def translate(request):
    return render(request, 'trans/index.html')

def TextInput(request):

    if 'username' in request.GET:
        source_lan = request.GET['source_lan']
        target_lan = request.GET['target_lan']
        username = request.GET['username']

        SRtext,input_url = SpeechRecogition(source_lan)
        
        time = str(datetime.now().replace(microsecond=0))

        Totaltime , Filename , TranslateInput, TranslateResult , output_url = GTTS(SRtext,target_lan,source_lan)
        # your response
        response = {
                    'TranslateText':SRtext,
                    'Totaltime':Totaltime,
                    'Filename':Filename ,
                    'Speech':TranslateInput,
                    'TranslateResult':TranslateResult,
                    'flag' : 2,
                    'Mp3url':output_url,
                    'Srcurl':input_url
                   }
        #send a message in SQS
        
        message = {
                    'Username':{'DataType': 'String','StringValue':username},
                    'Time':{'DataType': 'String','StringValue':time},
                    'SourceLan':{'DataType': 'String','StringValue':source_lan},                    
                    'InputWord':{'DataType': 'String','StringValue':SRtext}, 
                    'TargetLan':{'DataType': 'String','StringValue':target_lan}, 
                    'TranslateResult':{'DataType': 'String','StringValue':TranslateResult}, 

        }  

        queue = boto3.client('sqs')
        queue_url = 'https://queue.amazonaws.com/977546219141/ForDjangoRecord'
        # Put Message
        response = queue.send_message(QueueUrl=queue_url,DelaySeconds=10,MessageAttributes = message , MessageBody=(SRtext))
        
        # print(response)
        # print (message)
        return render_to_response('trans/index.html',response)
    else:
        return render_to_response('trans/index.html',locals())

