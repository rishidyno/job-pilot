/**
 * JOBPILOT — MarkdownEditor
 * Edit/Preview toggle + fullscreen expand for markdown content.
 */
import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { Pencil, Eye, Maximize2, Minimize2, X, Save, Check } from 'lucide-react'

function MarkdownPreview({ content }) {
  return (
    <div className="prose prose-sm dark:prose-invert max-w-none
      prose-headings:text-gray-900 dark:prose-headings:text-white prose-headings:font-semibold
      prose-h1:text-lg prose-h2:text-base prose-h3:text-sm
      prose-p:text-gray-600 dark:prose-p:text-surface-300 prose-p:leading-relaxed
      prose-li:text-gray-600 dark:prose-li:text-surface-300
      prose-strong:text-gray-800 dark:prose-strong:text-surface-200
      prose-code:text-brand-600 dark:prose-code:text-brand-400 prose-code:bg-brand-50 dark:prose-code:bg-brand-950/30 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-xs
      prose-hr:border-gray-200 dark:prose-hr:border-surface-700
      prose-ul:my-1 prose-li:my-0.5">
      <ReactMarkdown>{content || '*No content yet — switch to Edit mode to add content.*'}</ReactMarkdown>
    </div>
  )
}

export default function MarkdownEditor({ value, onChange, onSave, saving, label, icon: Icon, description, placeholder }) {
  const [mode, setMode] = useState('preview') // 'edit' | 'preview'
  const [fullscreen, setFullscreen] = useState(false)
  const [saved, setSaved] = useState(false)

  const handleSave = async () => {
    await onSave?.()
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  // Escape closes fullscreen
  useEffect(() => {
    if (!fullscreen) return
    const h = (e) => { if (e.key === 'Escape') setFullscreen(false) }
    document.addEventListener('keydown', h)
    return () => document.removeEventListener('keydown', h)
  }, [fullscreen])

  const toolbar = (
    <div className="flex items-center justify-between mb-3">
      <div className="flex items-center gap-2">
        {Icon && <Icon className="w-5 h-5 text-brand-500 shrink-0" />}
        <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">{label}</h2>
      </div>
      <div className="flex items-center gap-1.5">
        {/* Edit/Preview toggle */}
        <div className="flex bg-gray-100 dark:bg-surface-700 rounded-lg p-0.5">
          <button onClick={() => setMode('edit')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
              mode === 'edit' ? 'bg-white dark:bg-surface-600 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500 dark:text-surface-400 hover:text-gray-700 dark:hover:text-surface-200'
            }`} aria-label="Edit mode" aria-pressed={mode === 'edit'}>
            <Pencil className="w-3 h-3" /> Edit
          </button>
          <button onClick={() => setMode('preview')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
              mode === 'preview' ? 'bg-white dark:bg-surface-600 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500 dark:text-surface-400 hover:text-gray-700 dark:hover:text-surface-200'
            }`} aria-label="Preview mode" aria-pressed={mode === 'preview'}>
            <Eye className="w-3 h-3" /> Preview
          </button>
        </div>

        {/* Fullscreen */}
        <button onClick={() => setFullscreen(f => !f)}
          className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-surface-700 text-gray-400 dark:text-surface-500"
          aria-label={fullscreen ? 'Exit fullscreen' : 'Fullscreen'}>
          {fullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
        </button>

        {/* Save */}
        <button onClick={handleSave} disabled={saving}
          className="flex items-center gap-1 px-3 py-1.5 bg-brand-600 text-white text-xs font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50"
          aria-label={`Save ${label}`}>
          {saved ? <Check className="w-3 h-3" /> : <Save className="w-3 h-3" />}
          {saved ? 'Saved!' : 'Save'}
        </button>
      </div>
    </div>
  )

  const content = (
    <>
      {mode === 'edit' ? (
        <textarea value={value} onChange={e => onChange(e.target.value)}
          className={`w-full px-4 py-3 bg-gray-50 dark:bg-surface-900 border border-gray-200 dark:border-surface-700 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-500 resize-y leading-relaxed ${
            fullscreen ? 'flex-1' : 'h-[350px] sm:h-[400px]'
          }`}
          placeholder={placeholder}
          spellCheck={false}
          aria-label={`${label} editor`} />
      ) : (
        <div className={`px-4 py-3 bg-gray-50 dark:bg-surface-900 border border-gray-200 dark:border-surface-700 rounded-lg overflow-y-auto ${
          fullscreen ? 'flex-1' : 'h-[350px] sm:h-[400px]'
        }`}>
          <MarkdownPreview content={value} />
        </div>
      )}
      {description && !fullscreen && (
        <p className="text-xs text-gray-400 dark:text-surface-500 mt-2">{description}</p>
      )}
    </>
  )

  // Fullscreen modal
  if (fullscreen) {
    return (
      <div className="fixed inset-0 glass-overlay z-50 flex items-center justify-center p-3 sm:p-6"
        role="dialog" aria-modal="true" aria-label={`${label} — fullscreen editor`}>
        <div className="bg-white dark:bg-surface-800 rounded-xl w-full h-full max-w-5xl flex flex-col p-4 sm:p-6 shadow-2xl">
          {toolbar}
          {content}
        </div>
      </div>
    )
  }

  // Inline card
  return (
    <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4 sm:p-6">
      {toolbar}
      {content}
    </div>
  )
}
