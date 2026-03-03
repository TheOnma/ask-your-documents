import { useRef, useState } from 'react'

export default function Sidebar({ documents, onUpload, onDelete }) {
  const fileInputRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)
  const [status, setStatus] = useState({ text: '', type: '' })

  function handleFiles(files) {
    const file = files[0]
    if (!file) return
    if (!file.name.endsWith('.pdf')) {
      setStatus({ text: 'Only PDF files are supported.', type: 'error' })
      return
    }
    setStatus({ text: 'Uploading…', type: '' })
    onUpload(file, setStatus)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Upload zone */}
      <div className="p-4">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          hidden
          onChange={e => { if (e.target.files[0]) handleFiles(e.target.files); e.target.value = '' }}
        />
        <div
          onClick={() => fileInputRef.current.click()}
          onDragOver={e => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={e => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files) }}
          className={`border-2 border-dashed rounded-lg p-5 text-center cursor-pointer transition-colors
            ${dragOver ? 'border-red-400 bg-red-50' : 'border-gray-300 hover:border-red-400 hover:bg-red-50'}`}
        >
          <div className="text-3xl mb-2">📄</div>
          <p className="text-sm text-gray-500">
            Drop a PDF here or <strong className="text-gray-700">click to browse</strong>
          </p>
        </div>
        <p className={`text-xs mt-2 min-h-[1.25rem] ${status.type === 'error' ? 'text-red-500' : status.type === 'success' ? 'text-green-600' : 'text-gray-400'}`}>
          {status.text}
        </p>
      </div>
    </div>
  )
}
