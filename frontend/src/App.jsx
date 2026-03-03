import { useState, useEffect } from 'react'

export default function App() {
  const [documents, setDocuments] = useState([])

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-red-600 text-white px-6 h-14 flex items-center justify-between flex-shrink-0">
        <h1 className="font-semibold text-base tracking-tight">Ask Your Documents</h1>
        <div className="flex items-center gap-2 text-sm text-white/80">
          <span className="w-2 h-2 rounded-full bg-green-400 inline-block"></span>
          <span>
            {documents.length === 1 ? '1 document' : `${documents.length} documents`}
          </span>
        </div>
      </header>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-72 bg-white border-r border-gray-200 flex flex-col flex-shrink-0 overflow-y-auto">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Documents</h2>
          </div>
        </aside>

        {/* Main chat column */}
        <main className="flex-1 flex flex-col overflow-hidden bg-gray-50">
        </main>
      </div>

      {/* Footer */}
      <footer className="bg-red-600 text-white/90 text-center py-2 text-xs flex-shrink-0">
        Made with love ❤️
      </footer>
    </div>
  )
}
