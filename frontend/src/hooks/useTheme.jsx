/**
 * JOBPILOT — Multi-theme system
 * 6 themes: Light, Dark, Midnight, Nord, Sunset, Emerald
 * Uses CSS variables + data-theme attribute on <html>
 */
import { createContext, useContext, useState, useEffect } from 'react'

export const THEMES = [
  { id: 'light', label: 'Light', icon: '☀️', description: 'Clean & bright', isDark: false },
  { id: 'dark', label: 'Dark', icon: '🌙', description: 'Easy on the eyes', isDark: true },
  { id: 'midnight', label: 'Midnight', icon: '🌌', description: 'Deep OLED black', isDark: true },
  { id: 'nord', label: 'Nord', icon: '❄️', description: 'Cool arctic blue', isDark: true },
  { id: 'sunset', label: 'Sunset', icon: '🌅', description: 'Warm amber glow', isDark: true },
  { id: 'emerald', label: 'Emerald', icon: '🌿', description: 'Nature green', isDark: true },
]

const ThemeContext = createContext(null)

export function ThemeProvider({ children }) {
  const [themeId, setThemeId] = useState(() => {
    const saved = localStorage.getItem('jobpilot-theme')
    if (saved && THEMES.find(t => t.id === saved)) return saved
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  })

  const theme = THEMES.find(t => t.id === themeId) || THEMES[0]

  useEffect(() => {
    const root = document.documentElement
    // Set dark class for Tailwind dark: variants
    if (theme.isDark) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    // Set data-theme for CSS variable overrides
    root.setAttribute('data-theme', themeId)
    localStorage.setItem('jobpilot-theme', themeId)
  }, [themeId, theme.isDark])

  // System preference fallback
  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = (e) => {
      if (!localStorage.getItem('jobpilot-theme')) {
        setThemeId(e.matches ? 'dark' : 'light')
      }
    }
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])

  const setTheme = (id) => setThemeId(id)
  // Compat: dark boolean + toggle for existing code
  const dark = theme.isDark
  const toggle = () => setThemeId(dark ? 'light' : 'dark')

  return (
    <ThemeContext.Provider value={{ theme, themeId, setTheme, dark, toggle, themes: THEMES }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
