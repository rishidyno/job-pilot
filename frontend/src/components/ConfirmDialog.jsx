/**
 * Reusable confirmation dialog — replaces native confirm().
 */
import { useEffect, useRef } from 'react'

export default function ConfirmDialog({ title, message, confirmLabel = 'Confirm', cancelLabel = 'Cancel', variant = 'danger', onConfirm, onCancel }) {
  const btnRef = useRef(null)

  useEffect(() => {
    const h = (e) => { if (e.key === 'Escape') onCancel() }
    document.addEventListener('keydown', h)
    btnRef.current?.focus()
    return () => document.removeEventListener('keydown', h)
  }, [onCancel])

  const variantStyles = {
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    warning: 'bg-amber-600 hover:bg-amber-700 text-white',
    primary: 'bg-brand-600 hover:bg-brand-700 text-white',
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-[60] flex items-center justify-center p-4"
      onClick={onCancel} role="dialog" aria-modal="true" aria-label={title}>
      <div className="bg-white dark:bg-surface-800 rounded-xl w-full max-w-sm p-5 shadow-xl"
        onClick={e => e.stopPropagation()}>
        <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">{title}</h3>
        <p className="text-sm text-gray-500 dark:text-surface-400 mb-5">{message}</p>
        <div className="flex justify-end gap-2">
          <button onClick={onCancel}
            className="px-4 py-2 text-sm border border-gray-200 dark:border-surface-600 rounded-lg hover:bg-gray-50 dark:hover:bg-surface-700 text-gray-700 dark:text-surface-300">
            {cancelLabel}
          </button>
          <button ref={btnRef} onClick={onConfirm}
            className={`px-4 py-2 text-sm font-medium rounded-lg ${variantStyles[variant]}`}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
