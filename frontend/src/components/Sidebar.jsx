export default function Sidebar({ documents, onUpload, onDelete }) {
  return (
    <div className="flex flex-col h-full">
      {/* Upload zone */}
      <div className="p-4">
        <div
          className="border-2 border-dashed border-gray-300 rounded-lg p-5 text-center cursor-pointer
                     hover:border-red-400 hover:bg-red-50 transition-colors"
        >
          <div className="text-3xl mb-2">📄</div>
          <p className="text-sm text-gray-500">
            Drop a PDF here or <strong className="text-gray-700">click to browse</strong>
          </p>
        </div>
        <p className="text-xs text-gray-400 mt-2 min-h-[1.25rem]"></p>
      </div>
    </div>
  )
}
