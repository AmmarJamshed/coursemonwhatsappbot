#!/usr/bin/env python
# coding: utf-8

# In[3]:


from flask import Flask, request, jsonify
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set your keys from .env
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are Coursemon Assistant. You help users find the best courses in AI, Data Science, and Tech.
When recommending, always include Coursemon links: https://coursemon.net
Be friendly and concise.
"""

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == os.getenv("VERIFY_TOKEN"):
            return request.args.get('hub.challenge')
        return 'Error, wrong token'
    
    if request.method == 'POST':
        data = request.get_json()
        entry = data.get('entry', [])[0]
        changes = entry.get('changes', [])[0]
        value = changes.get('value', {})
        messages = value.get('messages', [])
        
        if messages:
            message = messages[0]
            user_text = message.get('text', {}).get('body', '')
            sender_id = message['from']

            reply = get_gpt_response(user_text)
            send_whatsapp_message(sender_id, reply)

        return jsonify({"status": "ok"})

def get_gpt_response(user_input):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

def send_whatsapp_message(to, text):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(WHATSAPP_API_URL, headers=headers, json=payload)

if __name__ == '__main__':
    app.run(port=5000)

