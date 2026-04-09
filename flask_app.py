import os
from flask import Flask, request, jsonify
import logging
from waitress import serve

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/')
def health_check():
    return ''


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            'stage': 'elephant'
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    stage = sessionStorage[user_id]['stage']

    if stage == 'elephant':
        if any(word in req['request']['original_utterance'].lower() for word in ['ладно', 'куплю', 'покупаю', 'хорошо']):
            res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
            res['response']['stage'] = 'rabbit'
            return
    elif stage == 'rabbit':
        if any(word in req['request']['original_utterance'].lower() for word in ['ладно', 'куплю', 'покупаю', 'хорошо']):
            res['response']['text'] = 'Кролика тоже можно найти на Яндекс.Маркете!'
            res['response']['end_session'] = True

    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]
    stage = session['stage']

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session
    if len(suggests) < 2:
        if stage == 'elephant':
            suggests.append({
                "title": "Ладно",
                "url": "https://market.yandex.ru/search?text=слон",
                "hide": True
            })
        elif stage == 'rabbit':
            suggests.append({
                "title": "Ладно",
                "url": "https://market.yandex.ru/search?text=кролик",
                "hide": True
            })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    serve(app, host='0.0.0.0', port=port)
