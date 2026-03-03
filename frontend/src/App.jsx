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
    </div>
  )
}
