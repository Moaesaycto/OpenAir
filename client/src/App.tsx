import './App.css'
import { FaPlane } from "react-icons/fa";

function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="flex w-full items-center gap-10">
        <FaPlane color="#ffffff" />
        <span>
          OpenAir
        </span>
      </header>
      <main className="flex-1">
        <h1>
          Welcome to the initial commit of OpenAir
        </h1>
      </main>
      <footer className="bg-neutral-700">
        Copyright Moae {new Date().getFullYear()}
      </footer>
    </div>
  )
}

export default App
