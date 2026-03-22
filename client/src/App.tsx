import { useEffect, useState } from "react";
import "./App.css";
import { FaPlane } from "react-icons/fa";
import { parseNmeaSentence } from "nmea-simple";

function App() {
  const [messages, setMessages] = useState<string[]>([]);

  // The port is injected by the Uvicorn endpoint. Defaults to 8000 for dev mode
  const port = (window as Window & { API_PORT?: number }).API_PORT ?? 8000;

  useEffect(() => {
    const connect = () => {
      const socket = new WebSocket(`ws://localhost:${port}/adsb`);
      socket.onmessage = (e) => setMessages(e.data.split("\n"));
      socket.onclose = () => {
        setTimeout(connect, 2000);
      };
      socket.onerror = () => socket.close();
    };
    connect();
  }, [port]);

  useEffect(() => {
    fetch(`http://localhost:${port}/gps`)
      .then((r) => r.json())
      .then((data) => console.log("gps:", data));

    fetch(`http://localhost:${port}/ports`)
      .then((r) => r.json())
      .then((data) => console.log("ports:", data));
  }, [port]);

  useEffect(() => {
    const socket = new WebSocket(`ws://localhost:${port}/gps-stream`);
    socket.onmessage = (e) => {
      try {
        const parsed = parseNmeaSentence(e.data);
        if (parsed.sentenceId === "GGA") {
          console.log(
            "lat:",
            parsed.latitude,
            "lon:",
            parsed.longitude,
            "fix:",
            parsed.fixType,
          );
        }
      } catch {
        // unparseable sentence, ignore
      }
    };
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
        {messages.map((e, i) => {
          return <p key={i}>{e}</p>;
        })}
      </main>
      <footer className="bg-neutral-700">
        Copyright Moae {new Date().getFullYear()}
      </footer>
    </div>
  );
}

export default App;
