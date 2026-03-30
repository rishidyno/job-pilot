/**
 * JOBPILOT — PDF Viewer Modal — dark mode.
 */
import { useState, useEffect } from 'react'
import { X, Download, ZoomIn, ZoomOut, Maximize2, Minimize2 } from 'lucide-react'

export default function PdfViewer({ url, title, onClose }) {
  const [zoom, setZoom] = useState(100)
  const [fullscreen, setFullscreen] = useState(false)

  useEffect(() => {
    const h = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', h)
    return () => document.removeEventListener('keydown', h)
  }, [onClose])

  const handleDownload = () => {
    const a = document.createElement('a')
    a.href = url
    a.download = `${title || 'resume'}.pdf`
    a.click()
  }

  return (
    <div className="fixed inset-0 glass-overlay z-50 flex items-end sm:items-center justify-center p-0 sm:p-4"
      role="dialog" aria-modal="true" aria-label={`PDF viewer: ${title}`}>
      <div className={`bg-white dark:bg-surface-800 flex flex-col ${
        fullscreen ? 'w-full h-full rounded-none' : 'w-full h-[85vh] sm:h-[90vh] sm:max-w-5xl rounded-t-2xl sm:rounded-xl'
      }`}>
        <div className="flex items-center justify-between px-3 sm:px-4 py-3 border-b border-gray-200 dark:border-surface-700 shrink-0">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-surface-200 truncate max-w-[40%] sm:max-w-none">{title || 'Resume Preview'}</h3>
          <div className="flex items-center gap-0.5 sm:gap-1">
            <button onClick={() => setZoom(z => Math.max(50, z - 25))}
              className="p-1.5 hover:bg-gray-100 dark:hover:bg-surface-700 rounded-lg" aria-label="Zoom out">
              <ZoomOut className="w-4 h-4 text-gray-500 dark:text-surface-400" />
            </button>
            <span className="text-xs text-gray-400 dark:text-surface-500 w-10 text-center">{zoom}%</span>
            <button onClick={() => setZoom(z => Math.min(200, z + 25))}
              className="p-1.5 hover:bg-gray-100 dark:hover:bg-surface-700 rounded-lg" aria-label="Zoom in">
              <ZoomIn className="w-4 h-4 text-gray-500 dark:text-surface-400" />
            </button>
            <button onClick={() => setFullscreen(f => !f)}
              className="p-1.5 hover:bg-gray-100 dark:hover:bg-surface-700 rounded-lg hidden sm:block"
              aria-label={fullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}>
              {fullscreen ? <Minimize2 className="w-4 h-4 text-gray-500 dark:text-surface-400" /> : <Maximize2 className="w-4 h-4 text-gray-500 dark:text-surface-400" />}
            </button>
            <button onClick={handleDownload}
              className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 bg-brand-600 text-white text-xs font-medium rounded-lg hover:bg-brand-700"
              aria-label="Download PDF">
              <Download className="w-3.5 h-3.5" /> <span className="hidden sm:inline">Download</span>
            </button>
            <button onClick={onClose} className="p-1.5 hover:bg-gray-100 dark:hover:bg-surface-700 rounded-lg ml-0.5"
              aria-label="Close PDF viewer">
              <X className="w-4 h-4 text-gray-500 dark:text-surface-400" />
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-auto bg-gray-100 dark:bg-surface-900">
          <iframe src={url} className="border-0 mx-auto block"
            style={{ width: `${zoom}%`, height: '100%', minHeight: '100%' }} title={`PDF: ${title}`} />
        </div>
      </div>
    </div>
  )
}
