const API = 'http://localhost:8000'

export async function listDocuments() {
  const res = await fetch(`${API}/documents`)
  if (!res.ok) throw new Error('Failed to fetch documents')
  const data = await res.json()
  return data.documents
}

export async function deleteDocument(filename) {
  const res = await fetch(`${API}/documents/${encodeURIComponent(filename)}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete document')
}

export async function ingestPDF(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${API}/ingest`, { method: 'POST', body: form })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Upload failed')
  return data
}

export async function askQuestion(question) {
  const res = await fetch(`${API}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Request failed')
  return data
}
