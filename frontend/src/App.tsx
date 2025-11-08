import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import './App.css'

interface OCRResult {
  page_number: number
  ocr_text: string
  status: string
  error?: string
  page_image?: string
}

interface StreamingState {
  total_pages: number
  results: OCRResult[]
  processing_page?: number
  api_calls_made?: number
  complete: boolean
}

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [streamingState, setStreamingState] = useState<StreamingState | null>(null)
  const [error, setError] = useState<string>('')
  const [dragActive, setDragActive] = useState(false)
  const [currentPageIndex, setCurrentPageIndex] = useState(0)

  // Use environment variable for API URL, fallback to localhost for development
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile)
        setError('')
        setStreamingState(null)
        setCurrentPageIndex(0)
      } else {
        setError('Please upload a PDF file')
        setFile(null)
      }
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile)
        setError('')
        setStreamingState(null)
        setCurrentPageIndex(0)
      } else {
        setError('Please upload a PDF file')
        setFile(null)
      }
    }
  }

  const handleSubmit = async () => {
    if (!file) {
      setError('Please select a PDF file')
      return
    }

    setLoading(true)
    setError('')
    setCurrentPageIndex(0)
    setStreamingState({
      total_pages: 0,
      results: [],
      complete: false
    })

    const formData = new FormData()
    formData.append('file', file)

    try {
      const uploadResponse = await fetch(`${API_URL}/ocr/stream`, {
        method: 'POST',
        body: formData,
      })

      if (!uploadResponse.ok) {
        throw new Error(`HTTP error! status: ${uploadResponse.status}`)
      }

      const reader = uploadResponse.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('Failed to get response reader')
      }

      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) {
          setLoading(false)
          break
        }

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              console.log('SSE received:', data.type, data)
              
              if (data.type === 'metadata') {
                setStreamingState(prev => ({
                  ...prev!,
                  total_pages: data.total_pages
                }))
              } else if (data.type === 'processing') {
                setStreamingState(prev => ({
                  ...prev!,
                  processing_page: data.page_number
                }))
              } else if (data.type === 'result') {
                // IMMEDIATELY add result to the list - this shows it in real-time!
                setStreamingState(prev => {
                  const newResults = [...prev!.results, {
                    page_number: data.page_number,
                    ocr_text: data.ocr_text,
                    status: data.status,
                    error: data.error,
                    page_image: data.page_image
                  }]
                  console.log('Results updated, count:', newResults.length)
                  return {
                    ...prev!,
                    results: newResults,
                    processing_page: undefined
                  }
                })
              } else if (data.type === 'complete') {
                setStreamingState(prev => ({
                  ...prev!,
                  complete: true,
                  api_calls_made: data.api_calls_made
                }))
                setLoading(false)
              } else if (data.type === 'error') {
                setError(data.message)
                setLoading(false)
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e, line)
            }
          }
        }
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while processing the PDF')
      setLoading(false)
    }
  }

  const handleReset = () => {
    setFile(null)
    setStreamingState(null)
    setError('')
    setLoading(false)
    setCurrentPageIndex(0)
  }

  const handleDownloadMarkdown = () => {
    if (!streamingState || streamingState.results.length === 0) {
      return
    }

    const markdownContent = streamingState.results
      .filter(result => result.status === 'success')
      .map(result => {
        return `# Page ${result.page_number}\n\n${result.ocr_text}\n\n---\n`
      })
      .join('\n')

    const fullContent = `# OCR Results - ${file?.name || 'Document'}\n\n` +
      `**Total Pages:** ${streamingState.total_pages}\n` +
      `**Successful Pages:** ${streamingState.results.filter(r => r.status === 'success').length}\n` +
      `**Generated:** ${new Date().toLocaleString()}\n\n` +
      `---\n\n` +
      markdownContent

    const blob = new Blob([fullContent], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${file?.name.replace('.pdf', '') || 'ocr-results'}.md`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const handleNextPage = () => {
    if (streamingState && currentPageIndex < streamingState.results.length - 1) {
      setCurrentPageIndex(currentPageIndex + 1)
    }
  }

  const handlePrevPage = () => {
    if (currentPageIndex > 0) {
      setCurrentPageIndex(currentPageIndex - 1)
    }
  }

  const handlePageClick = (index: number) => {
    setCurrentPageIndex(index)
  }

  const hasResults = streamingState && streamingState.results.length > 0
  const currentResult = hasResults ? streamingState.results[currentPageIndex] : null

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>📄 Handwritten Form OCR</h1>
          <p>Upload your PDF and extract handwritten text with AI</p>
        </header>

        {!hasResults ? (
          <div className="upload-section">
            <div
              className={`drop-zone ${dragActive ? 'drag-active' : ''} ${file ? 'has-file' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input')?.click()}
            >
              <input
                id="file-input"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
              
              {file ? (
                <div className="file-info">
                  <svg className="file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="file-name">{file.name}</p>
                  <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              ) : (
                <div className="upload-prompt">
                  <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="upload-text">Drag & drop your PDF here</p>
                  <p className="upload-subtext">or click to browse</p>
                </div>
              )}
            </div>

            {error && (
              <div className="error-message">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {error}
              </div>
            )}

            {loading && streamingState && (
              <div className="processing-status">
                <div className="processing-info">
                  <span className="spinner"></span>
                  <div>
                    <p className="processing-text">
                      {streamingState.processing_page 
                        ? `Processing page ${streamingState.processing_page} of ${streamingState.total_pages}...`
                        : 'Initializing...'}
                    </p>
                    <p className="processing-subtext">
                      {streamingState.results.length} / {streamingState.total_pages} pages completed
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="button-group">
              {file && (
                <>
                  <button className="button button-primary" onClick={handleSubmit} disabled={loading}>
                    {loading ? (
                      <>
                        <span className="spinner"></span>
                        Processing...
                      </>
                    ) : (
                      <>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Extract Text
                      </>
                    )}
                  </button>
                  <button className="button button-secondary" onClick={handleReset} disabled={loading}>
                    Reset
                  </button>
                </>
              )}
            </div>
          </div>
        ) : (
          <div className="results-section">
            <div className="results-header">
              <h2>OCR Results {!streamingState.complete && '(Processing...)'}</h2>
              <div className="header-buttons">
                <button 
                  className="button button-download" 
                  onClick={handleDownloadMarkdown}
                  disabled={loading || streamingState.results.filter(r => r.status === 'success').length === 0}
                  title="Download all results as markdown file"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Download Markdown
                </button>
                <button className="button button-secondary" onClick={handleReset} disabled={loading}>
                  Upload New PDF
                </button>
              </div>
            </div>

            <div className="results-summary">
              <p>Total Pages: <strong>{streamingState.total_pages}</strong></p>
              {streamingState.api_calls_made && (
                <p>API Calls Made: <strong>{streamingState.api_calls_made}</strong></p>
              )}
              <p>Completed: <strong>{streamingState.results.length}</strong></p>
              <p>Successful: <strong>{streamingState.results.filter(r => r.status === 'success').length}</strong></p>
            </div>

            {/* Page Thumbnails */}
            <div className="page-thumbnails">
              {streamingState.results.map((result, index) => (
                <div
                  key={result.page_number}
                  className={`thumbnail ${index === currentPageIndex ? 'active' : ''} ${result.status}`}
                  onClick={() => handlePageClick(index)}
                >
                  {result.page_image ? (
                    <img src={result.page_image} alt={`Page ${result.page_number}`} />
                  ) : (
                    <div className="thumbnail-placeholder">
                      <span className="spinner-small"></span>
                    </div>
                  )}
                  <span className="thumbnail-label">Page {result.page_number}</span>
                </div>
              ))}
              {loading && streamingState.processing_page && (
                <div className="thumbnail processing">
                  <div className="thumbnail-placeholder">
                    <span className="spinner-small"></span>
                  </div>
                  <span className="thumbnail-label">Page {streamingState.processing_page}</span>
                </div>
              )}
            </div>

            {/* Side-by-Side Viewer */}
            {currentResult && (
              <div className="viewer-container">
                <div className="pdf-viewer">
                  <div className="viewer-header">
                    <h3>Original PDF - Page {currentResult.page_number}</h3>
                  </div>
                  <div className="pdf-image-container">
                    {currentResult.page_image ? (
                      <img 
                        src={currentResult.page_image} 
                        alt={`Page ${currentResult.page_number}`}
                        className="pdf-image"
                      />
                    ) : (
                      <div className="image-placeholder">
                        <span className="spinner"></span>
                        <p>Loading image...</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="ocr-viewer">
                  <div className="viewer-header">
                    <h3>OCR Output - Page {currentResult.page_number}</h3>
                    <span className={`status-badge ${currentResult.status}`}>
                      {currentResult.status}
                    </span>
                  </div>
                  <div className="ocr-content-container">
                    {currentResult.status === 'success' ? (
                      <div className="markdown-content">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          rehypePlugins={[rehypeRaw]}
                        >
                          {currentResult.ocr_text}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <div className="error-box">
                        <p>Error processing this page:</p>
                        <p className="error-detail">{currentResult.error}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Navigation Controls */}
            <div className="navigation-controls">
              <button
                className="nav-button"
                onClick={handlePrevPage}
                disabled={currentPageIndex === 0}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Previous
              </button>
              
              <div className="page-indicator">
                Page {currentPageIndex + 1} of {streamingState.results.length}
              </div>
              
              <button
                className="nav-button"
                onClick={handleNextPage}
                disabled={currentPageIndex >= streamingState.results.length - 1}
              >
                Next
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
