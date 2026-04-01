/**
 * JOBPILOT — LaTeX Editor (Monaco-based)
 * Reusable VS Code-like editor for LaTeX content.
 */
import Editor from '@monaco-editor/react'
import { useTheme } from '../hooks/useTheme'

export default function LatexEditor({ value, onChange, height = '100%', readOnly = false }) {
  const { dark } = useTheme()

  return (
    <Editor
      height={height}
      language="latex"
      theme={dark ? 'vs-dark' : 'light'}
      value={value}
      onChange={onChange}
      options={{
        readOnly,
        fontSize: 13,
        fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
        minimap: { enabled: true, scale: 1 },
        lineNumbers: 'on',
        wordWrap: 'on',
        scrollBeyondLastLine: false,
        bracketPairColorization: { enabled: true },
        autoClosingBrackets: 'always',
        tabSize: 2,
        padding: { top: 12 },
        smoothScrolling: true,
        cursorBlinking: 'smooth',
        cursorSmoothCaretAnimation: 'on',
        renderLineHighlight: 'line',
      }}
      loading={
        <div className="flex items-center justify-center h-full text-sm text-gray-400 dark:text-surface-500">
          Loading editor...
        </div>
      }
    />
  )
}
