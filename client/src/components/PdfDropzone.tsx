import { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { uploadPdf } from "../services/api"
import type { Document } from "../types"

interface Props {
  onUploadSuccess: (doc: Document) => void
}

function UploadIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  )
}

export function PdfDropzone({ onUploadSuccess }: Props) {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0]
      if (!file) return
      setUploading(true)
      setError(null)
      try {
        const doc = await uploadPdf(file)
        onUploadSuccess(doc)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed")
      } finally {
        setUploading(false)
      }
    },
    [onUploadSuccess]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    multiple: false,
    disabled: uploading,
  })

  return (
    <div
      {...getRootProps()}
      className={`dropzone ${isDragActive ? "dropzone--active" : ""} ${uploading ? "dropzone--uploading" : ""}`}
    >
      <input {...getInputProps()} />
      <UploadIcon />
      {uploading ? "Uploading…" : isDragActive ? "Drop PDF here" : "Upload PDF"}
      {error && <span className="dropzone__error">{error}</span>}
    </div>
  )
}
