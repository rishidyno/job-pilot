/**
 * JOBPILOT — PDF Viewer Modal
 * In-app PDF viewer with download, zoom, and fullscreen.
 */
import { useState } from 'react'
import { X, Download, ZoomIn, ZoomOut, Maximize2, Minimize2 } from 'lucide-react'

export default function PdfViewer({ url, title, onClose }) {
  const [zoom, setZoom] = useState(100)
  const [fullscreen, setFullscreen] = useState(false)

  const handleDownload = () => {
    const a = document.createElement('a')
    a.href = url
    a.download = `${title || 'resume'}.pdf`
    a.click()
  }

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
      <div className={`bg-white rounded-xl flex flex-col transition-all ${
        fullscreen ? 'w-full h-full rounded-none' : 'w-full max-w-5xl h-[90vh]'
      }`}>
        {/* Toolbar */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 shrink-0">
          <h3 className="text-sm font-semibold text-gray-700 truncate">{title || 'Resume Preview'}</h3>
          <div className="flex items-center gap-1">
            <button onClick={() => setZoom(z => Math.max(50, z - 25))}
              className="p-1.5 hover:bg-gray-100 rounded-lg" title="Zoom out">
              <ZoomOut className="w-4 h-4 text-gray-500" />
            </button>
            <span className="text-xs text-gray-400 w-10 text-center">{zoom}%</span>
            <button onClick={() => setZoom(z => Math.min(200, z + 25))}
              className="p-1.5 hover:bg-gray-100 rounded-lg" title="Zoom in">
              <ZoomIn className="w-4 h-4 text-gray-500" />
            </button>
            <div className="w-px h-5 bg-gray-200 mx-1" />
            <button onClick={() => setFullscreen(f => !f)}
              className="p-1.5 hover:bg-gray-100 rounded-lg" title="Toggle fullscreen">
              {fullscreen
                ? <Minimize2 className="w-4 h-4 text-gray-500" />
                : <Maximize2 className="w-4 h-4 text-gray-500" />}
            </button>
            <button onClick={handleDownload}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-brand-600 text-white text-xs font-medium rounded-lg hover:bg-brand-700">
              <Download className="w-3.5 h-3.5" /> Download
            </button>
            <button onClick={onClose} className="p-1.5 hover:bg-gray-100 rounded-lg ml-1" title="Close">
              <X className="w-4 h-4 text-gray-500" />
            </button>
          </div>
        </div>

        {/* PDF iframe */}
        <div className="flex-1 overflow-auto bg-gray-100">
          <iframe
            src={url}
            className="border-0 mx-auto block"
            style={{ width: `${zoom}%`, height: '100%', minHeight: '100%' }}
            title="PDF Viewer"
          />
        </div>
      </div>
    </div>
  )
}
