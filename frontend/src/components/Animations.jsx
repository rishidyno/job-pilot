/**
 * JOBPILOT — Animation utilities
 */
import { useState, useEffect } from 'react'

/** Wraps a page with fade-in-up animation on mount */
export function PageWrapper({ children, className = '' }) {
  return <div className={`page-enter ${className}`}>{children}</div>
}

/** Scroll progress bar */
export function ScrollProgress() {
  const [width, setWidth] = useState(0)
  useEffect(() => {
    const handler = () => {
      const scrollTop = document.documentElement.scrollTop
      const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight
      setWidth(scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0)
    }
    window.addEventListener('scroll', handler, { passive: true })
    return () => window.removeEventListener('scroll', handler)
  }, [])
  return width > 0 ? <div className="scroll-progress" style={{ width: `${width}%` }} /> : null
}
