import numpy as np
import tensorflow as tf
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense
from tensorflow.keras.optimizers import RMSprop

# Download and load a smaller section of Shakespeare's text
filepath = tf.keras.utils.get_file('shakespeare.txt', 'https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt')
text = open(filepath, 'rb').read().decode(encoding='utf-8')[300000:400000]

# Create character mappings
characters = sorted(set(text))
char_to_index = {c: i for i, c in enumerate(characters)}
index_to_char = {i: c for i, c in enumerate(characters)}

SEQ_LENGTH = 40
STEP_SIZE = 3
sentences = []
next_characters = []

for i in range(0, len(text) - SEQ_LENGTH, STEP_SIZE):
    sentences.append(text[i: i + SEQ_LENGTH])
    next_characters.append(text[i + SEQ_LENGTH])

x = np.zeros((len(sentences), SEQ_LENGTH, len(characters)), dtype=np.float32)
y = np.zeros((len(sentences), len(characters)), dtype=np.float32)

for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        x[i, t, char_to_index[char]] = 1.0
    y[i, char_to_index[next_characters[i]]] = 1.0

# Build the LSTM model
model = Sequential([
    Input(shape=(SEQ_LENGTH, len(characters))),
    LSTM(128),
    Dense(len(characters), activation='softmax')
])

model.compile(loss='categorical_crossentropy', optimizer=RMSprop(learning_rate=0.01))
model.fit(x, y, batch_size=256, epochs=20)

# Ensure model directory exists
os.makedirs("model", exist_ok=True)

# Save the model in .keras format
model.save('model/textgenerator.keras')

# Save character metadata
with open('model/meta.txt', 'w') as f:
    f.write(''.join(characters))
