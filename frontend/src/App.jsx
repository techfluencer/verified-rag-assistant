import { useState } from "react";

function App() {
  const [question, setQuestion] = useState(""); // Naming convention : x + setX('value')
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    console.log("asking", question);
    setLoading(true);
    setResult(null);
    setError(null);

    const payload = { question };

    const options = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    };

    try {
      const response = await fetch("http://localhost:8000/rag/ask", options);
      if (!response.ok) {
        throw new Error(`Server error (${response.status})`)
      }
      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err)
      setError("Something went wrong. Please try again.")
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Verified RAG Assistant</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) =>
            setQuestion(e.target.value.replaceAll(".", "") + ".")
          }
          placeholder="Ask about the LangChain docs..."
        />
        <span>@</span>
        <button type="submit">Ask</button>
      </form>
      {loading && <p>Thinking...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {result && (
        <div>
          <p>{result.answer}</p>
          <ul>
            {result.sources.map((url) => (
              <li key={url}>
                <a href={url} target="_blank">
                  {url}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </main>
  );
}

export default App;
