/**
 * JOBPILOT — Page animation wrapper + stagger utility
 */

/** Wraps a page with fade-in-up animation on mount */
export function PageWrapper({ children, className = '' }) {
  return <div className={`page-enter ${className}`}>{children}</div>
}

/** Wraps a list item with staggered animation */
export function StaggerItem({ children, index = 0, className = '' }) {
  return (
    <div className={`stagger-item ${className}`} style={{ animationDelay: `${index * 60}ms` }}>
      {children}
    </div>
  )
}

/** Animated number that counts up and pops */
export function AnimatedNumber({ value, className = '' }) {
  return <span className={`count-pop inline-block ${className}`} key={value}>{value ?? '—'}</span>
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

import { useState, useEffect } from 'react'
