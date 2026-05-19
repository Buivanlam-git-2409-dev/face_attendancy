import React, { useEffect, useRef, useState } from 'react';
import { Button } from '../../shared/ui';
import '../../shared/ui/theme.css';
import './CameraStream.css';

const DETECTION_INTERVAL_MS = 900;
const TOAST_DURATION_MS = 3200;
const ATTENDANCE_COOLDOWN_MS = 5000;

export const CameraStream = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const detectorRef = useRef(null);
  const detectionTimerRef = useRef(null);
  const isDetectingRef = useRef(false);
  const lastAttendanceRef = useRef(0);

  const [isStarting, setIsStarting] = useState(true);
  const [isDetecting, setIsDetecting] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const [recognitionError, setRecognitionError] = useState('');
  const [toastMessage, setToastMessage] = useState('');

  const setupDetector = () => {
    if ('FaceDetector' in window) {
      detectorRef.current = new window.FaceDetector({
        fastMode: true,
        maxDetectedFaces: 3
      });
      setRecognitionError('');
      return true;
    }

    detectorRef.current = null;
    setRecognitionError('Recognition is unavailable in this browser.');
    return false;
  };

  const stopStream = () => {
    if (detectionTimerRef.current) {
      clearInterval(detectionTimerRef.current);
      detectionTimerRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  };

  const syncCanvasSize = (video, canvas) => {
    if (!video || !canvas) return;
    if (video.videoWidth === 0 || video.videoHeight === 0) return;
    if (canvas.width !== video.videoWidth) canvas.width = video.videoWidth;
    if (canvas.height !== video.videoHeight) canvas.height = video.videoHeight;
  };

  const showToast = (message) => {
    setToastMessage(message);
    window.clearTimeout(showToast.timeoutId);
    showToast.timeoutId = window.setTimeout(() => {
      setToastMessage('');
    }, TOAST_DURATION_MS);
  };

  const drawBoundingBoxes = (faces) => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;

    syncCanvasSize(video, canvas);

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#22d3ee';
    ctx.lineWidth = 2;

    faces.forEach(face => {
      const { x, y, width, height } = face.boundingBox;
      ctx.strokeRect(x, y, width, height);
    });
  };

  const detectFaces = async () => {
    if (!detectorRef.current || isDetectingRef.current) return;

    const video = videoRef.current;
    if (!video || video.readyState < 2) return;

    isDetectingRef.current = true;
    setIsDetecting(true);

    try {
      const faces = await detectorRef.current.detect(video);
      drawBoundingBoxes(faces);

      if (faces.length > 0) {
        const now = Date.now();
        if (now - lastAttendanceRef.current > ATTENDANCE_COOLDOWN_MS) {
          lastAttendanceRef.current = now;
          showToast('Attendance marked');
        }
      }
    } catch (error) {
      setRecognitionError('Recognition failed. Try again.');
      if (detectionTimerRef.current) {
        clearInterval(detectionTimerRef.current);
        detectionTimerRef.current = null;
      }
      if (canvasRef.current) {
        const ctx = canvasRef.current.getContext('2d');
        ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      }
    } finally {
      isDetectingRef.current = false;
      setIsDetecting(false);
    }
  };

  const startStream = async () => {
    setIsStarting(true);
    setCameraError('');
    setupDetector();

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setIsStarting(false);

      if (!detectionTimerRef.current && detectorRef.current) {
        detectionTimerRef.current = window.setInterval(detectFaces, DETECTION_INTERVAL_MS);
      }
    } catch (error) {
      setCameraError('Camera unavailable. Check permissions and try again.');
      setIsStarting(false);
    }
  };

  useEffect(() => {
    startStream();

    return () => {
      stopStream();
    };
  }, []);

  const handleRetryCamera = () => {
    stopStream();
    startStream();
  };

  const handleRetryRecognition = () => {
    setRecognitionError('');
    setupDetector();
    if (!detectionTimerRef.current && detectorRef.current) {
      detectionTimerRef.current = window.setInterval(detectFaces, DETECTION_INTERVAL_MS);
    }
  };

  const statusText = cameraError
    ? 'Camera unavailable'
    : recognitionError
      ? 'Recognition paused'
      : isDetecting
        ? 'Processing frame'
        : 'Live preview';

  return (
    <div className="camera-stream">
      <div className="camera-stream__preview">
        <video className="camera-stream__video" ref={videoRef} muted playsInline />
        <canvas className="camera-stream__overlay" ref={canvasRef} />

        {(isStarting || isDetecting) && !cameraError && (
          <div className="camera-stream__loading" aria-live="polite">
            <span className="camera-stream__spinner" aria-hidden="true" />
            <span>Processing frame</span>
          </div>
        )}

        {cameraError && (
          <div className="camera-stream__error" role="alert">
            <p className="camera-stream__error-title">Camera unavailable</p>
            <p className="camera-stream__error-body">{cameraError}</p>
            <Button variant="outline" size="sm" onClick={handleRetryCamera}>Retry camera</Button>
          </div>
        )}

        {!cameraError && recognitionError && (
          <div className="camera-stream__error camera-stream__error--compact" role="alert">
            <div>
              <p className="camera-stream__error-title">Recognition paused</p>
              <p className="camera-stream__error-body">{recognitionError}</p>
            </div>
            <Button variant="outline" size="sm" onClick={handleRetryRecognition}>Retry recognition</Button>
          </div>
        )}
      </div>

      <div className="camera-stream__meta">
        <div className="camera-stream__status">
          <span className={`camera-stream__dot ${cameraError ? 'is-error' : recognitionError ? 'is-warning' : 'is-live'}`} />
          <span>{statusText}</span>
        </div>
        <div className="camera-stream__hint">Position your face within the frame for best results.</div>
      </div>

      {toastMessage && (
        <div className="camera-stream__toast" role="status" aria-live="polite">
          <div className="camera-stream__toast-title">Attendance marked</div>
          <div className="camera-stream__toast-body">Recognition confirmed for the current frame.</div>
        </div>
      )}
    </div>
  );
};

export default CameraStream;
