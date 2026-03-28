/**
 * useFocusTrap — traps focus inside a modal/dialog.
 * Usage: const ref = useFocusTrap()  →  <div ref={ref}>...</div>
 */
import { useEffect, useRef } from 'react'

export function useFocusTrap() {
  const ref = useRef(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const focusable = el.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
    const first = focusable[0]
    const last = focusable[focusable.length - 1]

    first?.focus()

    const handler = (e) => {
      if (e.key !== 'Tab') return
      if (focusable.length === 0) { e.preventDefault(); return }
      if (e.shiftKey) {
        if (document.activeElement === first) { e.preventDefault(); last?.focus() }
      } else {
        if (document.activeElement === last) { e.preventDefault(); first?.focus() }
      }
    }

    el.addEventListener('keydown', handler)
    return () => el.removeEventListener('keydown', handler)
  }, [])

  return ref
}
