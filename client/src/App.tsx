import { useEffect, useState } from "react";
import "./App.css";
import { FaPlane } from "react-icons/fa";

function App() {
  const [messages, setMessages] = useState<string[]>([]);
  
  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/adsb");
    socket.onmessage = (e) => setMessages(e.data.split("\n"));
    return () => socket.close();
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      <header className="flex w-full items-center gap-10">
        <FaPlane color="#ffffff" />
        <span>OpenAir</span>
      </header>
      <main className="flex-1">
        <h1>Welcome to the initial commit of OpenAir</h1>
        {messages.map(
          (e, i) => {
            return <p key={i}>
              {e}
            </p>
          }
        )}
      </main>
      <footer className="bg-neutral-700">
        Copyright Moae {new Date().getFullYear()}
      </footer>
    </div>
  );
}

export default App;
