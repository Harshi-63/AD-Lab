import React, { useState } from "react";
import axios from "axios";

const Chatbot = () => {
  const [file, setFile] = useState(null);
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState("llama"); // Default model

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      alert("File uploaded successfully!");
      setLoading(false);
    } catch (error) {
      console.error("Upload error:", error);
      alert("File upload failed.");
      setLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) return;

    setMessages([...messages, { text: query, sender: "user" }]);

    try {
      const response = await axios.post("http://127.0.0.1:5000/query", {
        query,
        model,
      });

      setMessages([...messages, { text: query, sender: "user" }, { text: response.data.answer, sender: "bot" }]);
      setQuery("");
    } catch (error) {
      console.error("Query error:", error);
      alert("Failed to get response.");
    }
  };

  return (
    <div style={{ width: "50%", margin: "auto", textAlign: "center" }}>
      <h2>Chatbot Interface</h2>

      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>

      <br /><br />

      <select onChange={(e) => setModel(e.target.value)} value={model}>
        <option value="llama">LLaMA</option>
        <option value="gemma">Gemma</option>
      </select>

      <div style={{ border: "1px solid black", padding: "10px", minHeight: "200px", marginTop: "20px" }}>
        {messages.map((msg, index) => (
          <p key={index} style={{ textAlign: msg.sender === "user" ? "right" : "left" }}>
            <strong>{msg.sender === "user" ? "You: " : "Bot: "}</strong> {msg.text}
          </p>
        ))}
      </div>

      <input
        type="text"
        placeholder="Ask a question..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleQuery}>Send</button>
    </div>
  );
};

export default Chatbot;
