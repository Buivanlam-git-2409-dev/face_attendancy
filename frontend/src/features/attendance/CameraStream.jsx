import React, { useEffect, useRef, useState } from 'react'
import { Button } from '../../shared/ui'
import { recognitionService } from '../../shared/api/recognitionService'
import '../../shared/ui/theme.css'
import './CameraStream.css'

const TOAST_DURATION_MS = 4000
const ATTENDANCE_COOLDOWN_MS = 6000

export const CameraStream = ({
  course = '',
  lectureNo = '',
  disabled = false,
  onRecognitionSuccess,
}) => {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const lastAttendanceRef = useRef(0)

  const [isStarting, setIsStarting] = useState(true)
  const [isProcessing, setIsProcessing] = useState(false)
  const [cameraError, setCameraError] = useState('')
  const [recognitionError, setRecognitionError] = useState('')
  const [toastMessage, setToastMessage] = useState('')

  const showToast = (message) => {
    setToastMessage(message)

    window.clearTimeout(showToast.timeoutId)
    showToast.timeoutId = window.setTimeout(() => {
      setToastMessage('')
    }, TOAST_DURATION_MS)
  }

  const stopStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop())
      streamRef.current = null
    }
  }

  const startStream = async () => {
    setIsStarting(true)
    setCameraError('')
    setRecognitionError('')

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      })

      streamRef.current = stream

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }
    } catch (error) {
        console.error('Camera error:', error)
        let message = 'Camera unavailable. Check permissions and try again.'
        if (error.name === 'NotAllowedError') {
          message = 'Camera permission was denied. Please allow camera access in your browser.'
        }
        if (error.name === 'NotFoundError') {
          message = 'No camera device found on this computer.'
        }
        if (error.name === 'NotReadableError') {
          message = 'Camera is being used by another app. Close Zoom/Teams/Camera app and try again.'
        }
        if (error.name === 'OverconstrainedError') {
          message = 'Camera does not support the requested resolution.'
        }
        setCameraError(message)
    } finally {
      setIsStarting(false)
    }
  }

  useEffect(() => {
    startStream()

    return () => {
      stopStream()
    }
  }, [])

  const captureFrameAsFile = async () => {
    const video = videoRef.current
    const canvas = canvasRef.current

    if (!video || !canvas) {
      throw new Error('Camera is not ready')
    }

    if (video.videoWidth === 0 || video.videoHeight === 0) {
      throw new Error('Camera frame is empty')
    }

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    const blob = await new Promise((resolve) => {
      canvas.toBlob(resolve, 'image/jpeg', 0.9)
    })

    if (!blob) {
      throw new Error('Unable to capture camera frame')
    }

    return new File([blob], `attendance-frame-${Date.now()}.jpg`, {
      type: 'image/jpeg',
    })
  }

  const handleVerifyFrame = async () => {
    setRecognitionError('')

    if (disabled) {
      setRecognitionError('Please enter course and lecture number first.')
      return
    }

    if (!course || lectureNo === '' || lectureNo === null || lectureNo === undefined) {
      setRecognitionError('Course and lecture number are required.')
      return
    }

    const now = Date.now()
    if (now - lastAttendanceRef.current < ATTENDANCE_COOLDOWN_MS) {
      setRecognitionError('Please wait a few seconds before scanning again.')
      return
    }

    setIsProcessing(true)

    try {
      const file = await captureFrameAsFile()

      const result = await recognitionService.verifyFrame({
        file,
        course,
        lecture_no: lectureNo,
      })

      lastAttendanceRef.current = Date.now()

      const detectedFaces =
        result?.detectedFaces ||
        result?.detected_faces ||
        result?.results?.length ||
        0

      const message =
        detectedFaces > 0
          ? `Recognition completed. Detected faces: ${detectedFaces}`
          : 'Recognition completed.'

      showToast(message)

      if (onRecognitionSuccess) {
        onRecognitionSuccess(result)
      }
    } catch (error) {
      setRecognitionError(error.message || 'Recognition failed. Try again.')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleRetryCamera = () => {
    stopStream()
    startStream()
  }

  const statusText = cameraError
    ? 'Camera unavailable'
    : recognitionError
      ? 'Recognition issue'
      : isProcessing
        ? 'Sending frame to backend'
        : 'Live preview'

  return (
    <div className="camera-stream">
      <div className="camera-stream__preview">
        <video className="camera-stream__video" ref={videoRef} muted playsInline />
        <canvas className="camera-stream__overlay" ref={canvasRef} />

        {(isStarting || isProcessing) && !cameraError && (
          <div className="camera-stream__loading" aria-live="polite">
            <span className="camera-stream__spinner" aria-hidden="true" />
            <span>{isProcessing ? 'Recognizing...' : 'Starting camera...'}</span>
          </div>
        )}

        {cameraError && (
          <div className="camera-stream__error" role="alert">
            <div>
              <p className="camera-stream__error-title">Camera unavailable</p>
              <p className="camera-stream__error-body">{cameraError}</p>
            </div>
            <Button variant="outline" size="sm" onClick={handleRetryCamera}>
              Retry camera
            </Button>
          </div>
        )}

        {!cameraError && recognitionError && (
          <div className="camera-stream__error camera-stream__error--compact" role="alert">
            <div>
              <p className="camera-stream__error-title">Recognition notice</p>
              <p className="camera-stream__error-body">{recognitionError}</p>
            </div>
          </div>
        )}
      </div>

      <div className="camera-stream__meta">
        <div className="camera-stream__status">
          <span
            className={`camera-stream__dot ${
              cameraError ? 'is-error' : recognitionError ? 'is-warning' : 'is-live'
            }`}
          />
          <span>{statusText}</span>
        </div>

        <div className="camera-stream__hint">
          Course: {course || '-'} / Lecture: {lectureNo || '-'}
        </div>
      </div>

      <div className="camera-stream__actions">
        <Button
          type="button"
          onClick={handleVerifyFrame}
          loading={isProcessing}
          disabled={isStarting || Boolean(cameraError) || disabled}
        >
          Verify Current Frame
        </Button>
      </div>

      {toastMessage && (
        <div className="camera-stream__toast" role="status" aria-live="polite">
          <div className="camera-stream__toast-title">Recognition completed</div>
          <div className="camera-stream__toast-body">{toastMessage}</div>
        </div>
      )}
    </div>
  )
}

export default CameraStream