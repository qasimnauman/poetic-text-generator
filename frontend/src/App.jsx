import React, { useState } from 'react';

const App = () => {
  const [length, setLength] = useState(100);
  const [temperature, setTemperature] = useState(0.7);
  const [poem, setPoem] = useState('');
  const [wordDiversity, setWordDiversity] = useState(null);
  const [audioUrl, setAudioUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Poll for audio file availability
  const checkAudio = async (url, retries = 5, delay = 1000) => {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(url, { method: 'HEAD' });
        if (response.ok) return true;
        await new Promise(resolve => setTimeout(resolve, delay));
      } catch {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    return false;
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setPoem('');
    setWordDiversity(null);
    setAudioUrl('');

    try {
      const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ length: parseInt(length), temperature: parseFloat(temperature) }),
      });
      const data = await response.json();
      if (response.ok) {
        setPoem(data.poem);
        setWordDiversity(data.metrics.word_diversity);
        const audio = `http://localhost:8000${data.metrics.audio}`;
        const audioExists = await checkAudio(audio);
        if (audioExists) {
          setAudioUrl(audio);
        } else {
          setError('Audio file not available yet; try refreshing.');
        }
      } else {
        setError(data.detail || 'Failed to generate poem');
      }
    } catch (err) {
      setError(err.message || 'Error connecting to the server');
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async () => {
    setLoading(true);
    setError('');
    setPoem('');
    setWordDiversity(null);
    setAudioUrl('');

    try {
      const response = await fetch('http://localhost:8000/test');
      const data = await response.json();
      if (response.ok) {
        setPoem(data.poem);
        setWordDiversity(data.metrics.word_diversity);
        setAudioUrl(`http://localhost:8000${data.metrics.audio}`);
      } else {
        setError(data.detail || 'Failed to fetch test poem');
      }
    } catch (err) {
      setError(err.message || 'Error connecting to the server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl w-full mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">
        AI Poetic Text Generator
      </h1>

      <form onSubmit={handleGenerate} className="space-y-4">
        <div>
          <label htmlFor="length" className="block text-sm font-medium text-gray-700">
            Poem Length (characters)
          </label>
          <input
            type="number"
            id="length"
            value={length}
            onChange={(e) => setLength(e.target.value)}
            min="10"
            max="500"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            required
          />
        </div>
        <div>
          <label htmlFor="temperature" className="block text-sm font-medium text-gray-700">
            Temperature (0–2)
          </label>
          <input
            type="number"
            id="temperature"
            value={temperature}
            onChange={(e) => setTemperature(e.target.value)}
            min="0"
            max="2"
            step="0.1"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            required
          />
        </div>
        <div className="flex space-x-4">
          <button
            type="submit"
            disabled={loading}
            className={`flex-1 py-2 px-4 rounded-md text-white font-semibold ${
              loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'
            }`}
          >
            {loading ? 'Generating...' : 'Generate Poem'}
          </button>
          <button
            type="button"
            onClick={handleTest}
            disabled={loading}
            className={`flex-1 py-2 px-4 rounded-md text-white font-semibold ${
              loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            Test Poem
          </button>
        </div>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
          {error}
        </div>
      )}

      {poem && (
        <div className="mt-6 p-4 bg-gray-50 rounded-md">
          <h2 className="text-xl font-semibold text-gray-800">Generated Poem</h2>
          <pre className="mt-2 text-gray-700 whitespace-pre-wrap">{poem}</pre>
          {wordDiversity !== null && (
            <p className="mt-2 text-gray-600">
              Word Diversity: {wordDiversity.toFixed(3)}
            </p>
          )}
          {audioUrl && (
            <div className="mt-4">
              <audio controls className="w-full">
                <source src={audioUrl} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
            </div>
          )}
        </div>
      )}

      {loading && (
        <div className="mt-4 flex justify-center">
          <div className="animate-spin h-8 w-8 border-4 border-indigo-600 border-t-transparent rounded-full"></div>
        </div>
      )}
    </div>
  );
};

export default App;