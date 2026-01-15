import cv2
import numpy as np
import threading
import time
from typing import List, Dict, Optional, Tuple
from logger_config import get_logger

logger = get_logger("camera")

class CameraFaceCropper:
    def __init__(self, cam_index=0):
        self.cam_index = cam_index
        # Initialize Haar Cascade classifier once
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.cap = None
        self._lock = threading.Lock()
        self._frame_count = 0
        self._last_error_time = 0
        self._mirror_mode = False  # False = normal, True = mirror
        self._available_cameras = []
        
        # Discover available cameras
        self._discover_cameras()
        
        try:
            self.open(self.cam_index)
            logger.info(f"Camera initialized successfully on index {cam_index}")
        except Exception as e:
            logger.error(f"Failed to initialize camera: {str(e)}")
            raise

    def _discover_cameras(self):
        """Discover all available cameras"""
        self._available_cameras = []
        
        for i in range(10):  # Check cameras 0-9
            try:
                temp_cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if temp_cap.isOpened():
                    ret, frame = temp_cap.read()
                    if ret and frame is not None:
                        # Get camera info
                        width = int(temp_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(temp_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = temp_cap.get(cv2.CAP_PROP_FPS)
                        
                        camera_info = {
                            'index': i,
                            'name': f'Camera {i}',
                            'resolution': f'{width}x{height}',
                            'fps': fps,
                            'working': True
                        }
                        self._available_cameras.append(camera_info)
                        logger.info(f"Found camera {i}: {width}x{height} @ {fps}fps")
                    
                    temp_cap.release()
            except Exception as e:
                logger.debug(f"Camera {i} not available: {str(e)}")
                continue
        
        logger.info(f"Discovered {len(self._available_cameras)} available cameras")

    def get_available_cameras(self) -> List[Dict]:
        """Get list of available cameras"""
        return self._available_cameras.copy()

    def open(self, cam_index: int):
        """Open camera with improved error handling and validation"""
        with self._lock:
            self.cam_index = cam_index
            
            # Release existing camera
            if self.cap is not None:
                try:
                    self.cap.release()
                    logger.debug(f"Released camera {self.cam_index}")
                except Exception as e:
                    logger.warning(f"Error releasing camera: {e}")
                finally:
                    self.cap = None
            
            # Validate camera index
            if cam_index < 0 or cam_index > 10:
                raise ValueError(f"Invalid camera index: {cam_index}")
            
            # Try to open camera
            self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"Failed to open camera {cam_index}")
            
            # Test if camera can read frames
            try:
                ret, test_frame = self.cap.read()
                if not ret or test_frame is None:
                    raise RuntimeError(f"Camera {cam_index} opened but cannot read frames")
                
                # Check frame dimensions
                height, width = test_frame.shape[:2]
                if width < 320 or height < 240:
                    logger.warning(f"Camera {cam_index} has low resolution: {width}x{height}")
                
                logger.info(f"Camera {cam_index} opened successfully: {width}x{height}")
                
            except Exception as e:
                self.cap.release()
                self.cap = None
                raise RuntimeError(f"Camera {cam_index} test failed: {str(e)}")

    def flip_next(self, max_index=4):
        """Switch to next available camera"""
        available_indices = [cam['index'] for cam in self._available_cameras]
        
        if not available_indices:
            logger.error("No available cameras to flip to")
            return self.cam_index
        
        # Find next camera in available list
        current_idx = self.cam_index
        next_idx = None
        
        for cam_idx in available_indices:
            if cam_idx > current_idx:
                next_idx = cam_idx
                break
        
        # If no next camera found, loop to first
        if next_idx is None:
            next_idx = available_indices[0]
        
        try:
            self.open(next_idx)
            logger.info(f"Switched to camera {next_idx}")
            return next_idx
        except Exception as e:
            logger.error(f"Failed to switch to camera {next_idx}: {str(e)}")
            return self.cam_index

    def toggle_mirror(self):
        """Toggle mirror mode"""
        self._mirror_mode = not self._mirror_mode
        mode = "mirror" if self._mirror_mode else "normal"
        logger.info(f"Camera mode set to: {mode}")
        return self._mirror_mode

    def set_mirror_mode(self, mirror: bool):
        """Set mirror mode explicitly"""
        self._mirror_mode = mirror
        mode = "mirror" if self._mirror_mode else "normal"
        logger.info(f"Camera mode set to: {mode}")

    def read_frame(self):
        """Read frame from camera with error handling and statistics"""
        with self._lock:
            if self.cap is None:
                logger.warning("Camera not initialized")
                return None
            
            try:
                ret, frame = self.cap.read()
                
                if not ret or frame is None:
                    current_time = time.time()
                    if current_time - self._last_error_time > 5:  # Log every 5 seconds
                        logger.error(f"Failed to read frame from camera {self.cam_index}")
                        self._last_error_time = current_time
                    return None
                
                # Apply mirror mode if enabled
                if self._mirror_mode:
                    frame = cv2.flip(frame, 1)  # Horizontal flip
                
                # Update frame counter
                self._frame_count += 1
                
                # Log frame stats periodically
                if self._frame_count % 100 == 0:
                    height, width = frame.shape[:2]
                    logger.debug(f"Frame #{self._frame_count}: {width}x{height}")
                
                return frame
                
            except Exception as e:
                logger.error(f"Error reading frame from camera {self.cam_index}: {str(e)}")
                return None

    def find_face_crop(self, frame_bgr, pad=0.18):
        """Find and crop face from frame using OpenCV Haar Cascade"""
        if frame_bgr is None:
            logger.warning("No frame provided for face detection")
            return None, None
        
        try:
            h, w = frame_bgr.shape[:2]
            
            # Validate frame dimensions
            if h < 100 or w < 100:
                logger.warning(f"Frame too small for face detection: {w}x{h}")
                return None, None
            
            logger.debug(f"Processing frame {w}x{h} for face detection")
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            
            # Detect faces using pre-initialized cascade
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) == 0:
                logger.debug("No faces detected in frame")
                return None, None
            
            logger.debug(f"Found {len(faces)} face(s)")
            
            # Use the first detected face
            x, y, bw, bh = faces[0]
            
            # Validate bounding box
            if bw <= 0 or bh <= 0:
                logger.warning("Invalid face detection bounding box")
                return None, None
            
            # Ensure coordinates are within frame bounds
            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(w, x + bw)
            y2 = min(h, y + bh)
            
            # Validate final coordinates
            if x2 <= x1 or y2 <= y1:
                logger.warning("Invalid face crop coordinates")
                return None, None
            
            # Apply padding
            px = int(bw * pad)
            py = int(bh * pad)
            x1 = max(0, x1 - px)
            y1 = max(0, y1 - py)
            x2 = min(w, x1 + bw + 2 * px)
            y2 = min(h, y1 + bh + 2 * py)
            
            # Final validation
            if x2 <= x1 or y2 <= y1:
                logger.warning("Invalid padded face crop coordinates")
                return None, None
            
            crop = frame_bgr[y1:y2, x1:x2].copy()
            
            # Validate crop
            if crop is None or crop.size == 0:
                logger.warning("Failed to create face crop")
                return None, None
            
            return crop, (x1, y1, x2, y2)
            
        except Exception as e:
            logger.error(f"Error in face detection: {str(e)}")
            return None, None

    def capture_photo(self, save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """Capture a single photo from camera"""
        frame = self.read_frame()
        if frame is None:
            logger.error("Failed to capture photo: no frame available")
            return None
        
        if save_path:
            try:
                cv2.imwrite(save_path, frame)
                logger.info(f"Photo saved to: {save_path}")
            except Exception as e:
                logger.error(f"Failed to save photo: {str(e)}")
        
        return frame

    def encode_jpg(self, img_bgr, quality=80):
        """Encode image to JPEG with validation and error handling"""
        if img_bgr is None:
            logger.warning("No image provided for JPEG encoding")
            return None
        
        if not (0 <= quality <= 100):
            raise ValueError(f"Invalid JPEG quality: {quality}")
        
        try:
            h, w = img_bgr.shape[:2]
            
            # Validate image dimensions
            if h < 50 or w < 50:
                logger.warning(f"Image too small for JPEG encoding: {w}x{h}")
                return None
            
            ok, buf = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
            
            if not ok or buf is None:
                logger.error("Failed to encode image to JPEG")
                return None
            
            jpg_bytes = buf.tobytes()
            
            # Validate encoded data
            if len(jpg_bytes) == 0:
                logger.error("JPEG encoding produced empty data")
                return None
            
            if len(jpg_bytes) > 10 * 1024 * 1024:  # 10MB limit
                logger.warning(f"JPEG too large: {len(jpg_bytes)} bytes")
                return None
            
            return jpg_bytes
            
        except Exception as e:
            logger.error(f"Error encoding JPEG: {str(e)}")
            return None

    def release(self):
        """Release camera resources with proper cleanup"""
        with self._lock:
            if self.cap is not None:
                try:
                    self.cap.release()
                    logger.info(f"Camera {self.cam_index} released successfully")
                except Exception as e:
                    logger.error(f"Error releasing camera: {str(e)}")
                finally:
                    self.cap = None
            
            logger.info("Camera resources cleaned up")