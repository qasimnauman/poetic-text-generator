# Test Results & Evaluation

## Test Cases

| Length | Temperature | Output Summary         |
|--------|-------------|------------------------|
| 300    | 0.7         | Coherent, rhythmic     |
| 300    | 1.0         | Creative, less logical |

## Performance Graphs

- Training loss curve plotted during model training (see `model/training_logs.png`)

## Limitations

- Character-level model may struggle with semantic meaning
- No grammar or rhyme constraints
- Model trained only on Shakespeare, limiting stylistic variety

## Future Improvements

- Add rhyming mechanism
- Fine-tune on different poets
- Improve evaluation with BLEU/NLP metrics
