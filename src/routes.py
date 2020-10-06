from src import app, socketio, mongo
from flask import render_template
from flask_socketio import join_room, emit, send
from random import choices
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz
from uuid import uuid4

ROOMS = {}
DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
THRESHOLD = timedelta(seconds=60)
HINT_THRESHOLD = timedelta(seconds=2)

@app.route("/")
def index():
    return render_template('index.html')

def get_random_expression():
    return next(mongo.db.expressions.aggregate([{ "$sample": { "size": 1 } }]))

def get_random_word(sentence):
    words = sentence.split(' ')
    words_weights = []
    for word in words:
        score = 0
        if word[-1] in [',', ':', ';']:
            score += 10
        if word == words[-1]:
            score += 10
        if len(word) > 3:
            score += 100
        if len(word) == 1:
            score = 0
        words_weights.append(score)
    return choices(words, weights=words_weights, k=1)[0]

def obfuscate_in_sentence(sentence, word_to_obfuscate):
    words = sentence.split(' ')
    output = []
    for word in words:
        if word == word_to_obfuscate:
            output += ['_' if letter not in [',', ':', ';', '-', "'", '’'] else letter for letter in word] + [' ']
        else:
            output += list(f'{word} ')
    return ''.join(output[:-1])

def reconstruct_sentence(sentence, answer, correct_answer):
    output = []
    words = sentence.split(' ')
    for word in words:
        if word == correct_answer:
            output.append({"text": f'{answer} ({correct_answer}) ', "style": 'answer' })
        else:
            output.append({"text": f'{word} ', "style": 'normal' })
    return output

def generate_user_game_state(game_state):
    user_game_state = game_state.copy()
    del user_game_state['correct_answer']
    del user_game_state['original_sentence']
    return user_game_state

@socketio.on('create')
def on_create(data):
    user_id = data.get('user_id')
    if not user_id:
        # emit("join_room", {'error': 'no user id provided', 'status':'error'})
        user_id = str(uuid4())
    expression = get_random_expression()
    sentence = expression.get('text')
    random_word = get_random_word(sentence)
    user_sentence = obfuscate_in_sentence(sentence, random_word)
    correct_answer = random_word if random_word[-1] not in [',', ':', ';'] else random_word[:-1]
    game_state = {
        'user_id': user_id,
        'score': 0,
        'answers': [],
        'user_sentence': user_sentence,
        'correct_answer': correct_answer,
        'original_sentence': sentence,
        'started_on': datetime.utcnow().strftime(DATE_FORMAT),
    }
    user_game_state = generate_user_game_state(game_state)
    room = game_state['user_id']
    ROOMS[room] = game_state
    join_room(room)
    emit("join_room", {'game_state': user_game_state, 'status': 'ok'})

@socketio.on('solve')
def on_solve(data):
    user_id = data.get('user_id')
    answer = data.get('answer')
    if not user_id:
        emit("update", {'error': 'no user id provided', 'status': 'error'})
    if not answer:
        emit("update", {'error': 'no answer provided', 'status': 'error'})

    game_state = ROOMS.get(user_id)
    if not game_state:
        emit("update", {'error': 'user doesnt have a game_state started', 'status': 'error'})
    if datetime.utcnow() - datetime.strptime(game_state['started_on'], DATE_FORMAT) > THRESHOLD:
        emit("update", {'error': 'game finished', 'status': 'finished'})
    
    correct_answer = game_state['correct_answer']
    original_sentence = game_state['original_sentence']
    is_correct_answer = fuzz.WRatio(answer, correct_answer) > 90

    game_state['answers'].append({'answer': answer, 'sentence': reconstruct_sentence(original_sentence, answer, correct_answer), 'is_correct': is_correct_answer})
    if is_correct_answer:
        game_state['score'] = game_state['score'] + 1
    
    next_expression = get_random_expression()
    next_sentence = next_expression.get('text')
    next_random_word = get_random_word(next_sentence)
    next_user_sentence = obfuscate_in_sentence(next_sentence, next_random_word)
    next_correct_answer = next_random_word if next_random_word[-1] not in [',', ':', ';'] else next_random_word[:-1]
    game_state['user_sentence'] = next_user_sentence
    game_state['correct_answer'] = next_correct_answer
    game_state['original_sentence'] = next_sentence
    game_state['last_time_answered'] = datetime.utcnow().strftime(DATE_FORMAT)
    
    ROOMS[user_id] = game_state
    user_game_state = generate_user_game_state(game_state)
    emit("update", {'game_state': user_game_state, 'status': 'ok'})

@socketio.on('check')
def on_check(data):
    user_id = data.get('user_id')
    if not user_id:
        emit("update", {'error': 'no user id provided', 'status': 'error'})
    game_state = ROOMS.get(user_id)
    if not game_state:
        emit("update", {'error': 'user doesnt have a game_state started', 'status': 'error'})
    if datetime.utcnow() - datetime.strptime(game_state['started_on'], DATE_FORMAT) > THRESHOLD:
        emit("update", {'error': 'game finished', 'status': 'finished'})
    user_game_state = generate_user_game_state(game_state)
    emit("update", {'game_state': user_game_state, 'status': 'ok'})