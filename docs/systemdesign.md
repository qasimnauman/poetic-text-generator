# System Design – Poetic Text Generator

## Architecture

- **Frontend (optional)**: Web interface (Flask frontend)
- **Backend**: Python (Flask API) using trained LSTM model
- **Model**: Trained on Shakespearean text using character-level RNN (LSTM)

## Methodology

- Preprocess large poetic corpus (e.g., Shakespeare)
- Convert characters to integer sequences
- Train LSTM to predict next character
- Generate output by sampling from trained model using a temperature parameter

## AI Technique Justification

- **RNNs/LSTMs** are ideal for sequential data like text.
- Character-level modeling ensures flexibility across vocab styles.
- Fitness functions and temperature tuning help control creativity and coherence.

## Libraries Used

- TensorFlow / Keras
- Flask
- NumPy
