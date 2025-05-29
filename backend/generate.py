# import random
# import numpy as np
# import tensorflow as tf
# import pyttsx3

# model = tf.keras.models.load_model('model/textgenerator.keras')

# with open('model/meta.txt', 'r') as f:
#     characters = list(f.read())

# char_to_index = dict((c, i) for i, c in enumerate(characters))
# index_to_char = dict((i, c) for i, c in enumerate(characters))

# SEQ_LENGTH = 40

# filepath = tf.keras.utils.get_file('shakespeare.txt', 'https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt')
# text = open(filepath, 'rb').read().decode(encoding='utf-8')[300000:400000]

# def sample(preds, temperature=1.0):
#     preds = np.asarray(preds).astype('float64')
#     preds = np.log(preds + 1e-8) / temperature
#     exp_preds = np.exp(preds)
#     preds = exp_preds / np.sum(exp_preds)
#     probas = np.random.multinomial(1, preds, 1)
#     return np.argmax(probas)

# def generate_poem(length, temperature=0.5):
#     start_index = random.randint(0, len(text) - SEQ_LENGTH - 1)
#     sentence = text[start_index: start_index + SEQ_LENGTH]
#     generated = sentence
#     for _ in range(length):
#         x_pred = np.zeros((1, SEQ_LENGTH, len(characters)))
#         for t, char in enumerate(sentence):
#             x_pred[0, t, char_to_index.get(char, 0)] = 1
#         preds = model.predict(x_pred, verbose=0)[0]
#         next_index = sample(preds, temperature)
#         next_char = index_to_char[next_index]
#         generated += next_char
#         sentence = sentence[1:] + next_char
#     return generated

# def fitness(text):
#     words = text.split()
#     unique = len(set(words))
#     avg_len = sum(len(line) for line in text.split('\n')) / (len(text.split('\n')) + 1)
#     return unique / len(words) + 1 / (abs(avg_len - 40) + 1)

# def mutate(text, rate=0.1):
#     chars = list(text)
#     for i in range(len(chars)):
#         if random.random() < rate:
#             chars[i] = random.choice(characters)
#     return ''.join(chars)

# def crossover(p1, p2):
#     idx = random.randint(0, len(p1))
#     return p1[:idx] + p2[idx:]

# def evolve(poems, generations=5):
#     for _ in range(generations):
#         scored = sorted(poems, key=lambda t: -fitness(t))
#         next_gen = scored[:5]
#         while len(next_gen) < len(poems):
#             p1, p2 = random.sample(scored[:5], 2)
#             child = mutate(crossover(p1, p2))
#             next_gen.append(child)
#         poems = next_gen
#     return max(poems, key=fitness)

# def speak(text, save=False):
#     engine = pyttsx3.init()
#     engine.setProperty('rate', 150)
#     if save:
#         engine.save_to_file(text, 'static/output_audio.mp3')
#     else:
#         engine.say(text)
#     engine.runAndWait()


import random
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import os
import uuid
from gtts import gTTS
import pyttsx3

# FastAPI app setup
origins = [
    "*",
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# CORS(app, allow_methods=["*"], allow_headers=["*"])

# Ensure static directory exists
STATIC_DIR = "static"  # Relative path
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Load TensorFlow model and character mappings
model = tf.keras.models.load_model('model/textgenerator.keras')
with open('model/meta.txt', 'r') as f:
    characters = list(f.read())
char_to_index = dict((c, i) for i, c in enumerate(characters))
index_to_char = dict((i, c) for i, c in enumerate(characters))
SEQ_LENGTH = 40

# Load Shakespeare text
filepath = tf.keras.utils.get_file('shakespeare.txt', 'https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt')
text = open(filepath, 'rb').read().decode(encoding='utf-8')[300000:400000]

# Pydantic model for request validation
class PoemRequest(BaseModel):
    length: int = 100  # Reduced default from 300
    temperature: float = 0.7

# Generator functions
def sample(preds, temperature=1.0):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds + 1e-8) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

async def generate_poem(length: int, temperature: float):
    start_index = random.randint(0, len(text) - SEQ_LENGTH - 1)
    sentence = text[start_index: start_index + SEQ_LENGTH]
    generated = sentence
    for _ in range(length):
        x_pred = np.zeros((1, SEQ_LENGTH, len(characters)))
        for t, char in enumerate(sentence):
            x_pred[0, t, char_to_index.get(char, 0)] = 1
        preds = model.predict(x_pred, verbose=0)[0]
        next_index = sample(preds, temperature)
        next_char = index_to_char[next_index]
        generated += next_char
        sentence = sentence[1:] + next_char
    return generated

def fitness(text: str) -> float:
    words = text.split()
    unique = len(set(words))
    return unique / (len(words) + 1)  # Simplified fitness

def mutate(text: str, rate: float = 0.1) -> str:
    chars = list(text)
    for i in range(len(chars)):
        if random.random() < rate:
            chars[i] = random.choice(characters)
    return ''.join(chars)

def crossover(p1: str, p2: str) -> str:
    idx = random.randint(0, len(p1))
    return p1[:idx] + p2[idx:]

async def evolve(poems: list, generations: int = 2) -> str:
    for _ in range(generations):  # Reduced from 5
        scored = sorted(poems, key=lambda t: -fitness(t))
        next_gen = scored[:5]
        while len(next_gen) < len(poems):
            p1, p2 = random.sample(scored[:5], 2)
            child = mutate(crossover(p1, p2))
            next_gen.append(child)
        poems = next_gen
    return max(poems, key=fitness)

async def speak(text: str, save: bool = False, filename: str = None):
    if save:
        tts = gTTS(text=text, lang='en')
        tts.save(filename)
    else:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

# API routes
@app.post("/generate")
async def generate(request: PoemRequest):
    try:
        # Validate inputs
        if request.length <= 0:
            raise HTTPException(status_code=400, detail="Length must be positive")
        if not 0 <= request.temperature <= 2:
            raise HTTPException(status_code=400, detail="Temperature must be between 0 and 2")

        # Generate poems asynchronously
        tasks = [generate_poem(request.length, request.temperature) for _ in range(3)]
        candidates = await asyncio.gather(*tasks)

        if not candidates:
            raise HTTPException(status_code=500, detail="Failed to generate poems")

        # Evolve poems
        best = await evolve(candidates, generations=2)

        # Generate audio synchronously with complete relative path
        audio_filename = f"output_{uuid.uuid4().hex}.mp3"
        audio_path = f"static/{audio_filename}"  # Complete relative path
        await speak(best, save=True, filename=audio_path)

        # Verify audio file exists
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="Failed to generate audio file")

        # Calculate metrics
        word_diversity = round(fitness(best), 3)

        return {
            "poem": best,
            "metrics": {
                "word_diversity": word_diversity,
                "audio": f"/static/{audio_filename}"
            }
        }
    except Exception as e:
        app.logger.error(f"Error in /generate: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/test")
async def test():
    try:
        sample_poem = """
        The moon doth rise with silver glow,
        In night's embrace, soft shadows flow.
        Through whispered winds, the stars align,
        A fleeting dream in cosmic rhyme.
        """
        sample_metrics = {
            "word_diversity": 0.85,
            "audio": "/static/sample_audio.mp3"
        }
        return {
            "poem": sample_poem.strip(),
            "metrics": sample_metrics
        }
    except Exception as e:
        app.logger.error(f"Error in /test: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Run the app (for development; use uvicorn for production)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)