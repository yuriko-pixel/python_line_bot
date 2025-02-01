import os
from flask import Flask, request, abort
from linebot.v3.webhook import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
import google.generativeai as genai

app = Flask(__name__)

line_handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
configuration = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/callback", methods=['POST'])
def callback():
    app.logger.info(os.environ["API_TEST"])
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_message = event.message.text
        ai_response = model.start_chat().send_message(user_message)
        ai_reply_text = ai_response.text

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=ai_reply_text)]
            )
        )
