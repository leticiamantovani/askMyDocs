import { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { uploadPdf } from "../services/api"
import type { Document } from "../types"

interface Props {
  onUploadSuccess: (doc: Document) => void
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
    <div {...getRootProps()} className={`dropzone ${isDragActive ? "dropzone--active" : ""} ${uploading ? "dropzone--uploading" : ""}`}>
      <input {...getInputProps()} />
      {uploading ? (
        <p>Uploading…</p>
      ) : isDragActive ? (
        <p>Drop the PDF here</p>
      ) : (
        <p>Drag & drop a PDF here, or click to select</p>
      )}
      {error && <p className="dropzone__error">{error}</p>}
    </div>
  )
}
