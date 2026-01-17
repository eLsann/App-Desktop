import requests
import json
import os
from typing import Dict, Any, Optional
import time
from logger_config import get_logger

logger = get_logger("api_client")


class ApiClient:
    def __init__(self, base_url: str, device_id: str, device_token: str, timeout=12.0):
        self.base_url = base_url.rstrip("/")
        self.device_id = device_id
        self.device_token = device_token
        self.timeout = float(timeout)

        self._admin_token: str | None = None
        self.session = requests.Session()
        
        # Connection status tracking for smart reconnection
        self._is_online = True
        self._last_error_time = 0
        self._consecutive_failures = 0
        self._retry_backoff = 1  # Exponential backoff: 1, 2, 4, 8... seconds
        self._max_backoff = 30   # Max 30 seconds between retries
    
    @property
    def is_online(self) -> bool:
        """Check if API is currently reachable"""
        return self._is_online
    
    def check_health(self) -> bool:
        """Quick health check to API - returns True if online"""
        try:
            r = self.session.get(f"{self.base_url}/health", timeout=3)
            if r.status_code == 200:
                self._is_online = True
                self._consecutive_failures = 0
                self._retry_backoff = 1
                return True
        except:
            pass
        self._is_online = False
        return False

    # ---------------- Token (admin) ----------------
    @property
    def admin_token(self) -> str | None:
        return self._admin_token

    @admin_token.setter
    def admin_token(self, v: str | None):
        """Sanitize token so we never send 'Bearer Bearer ...' or quotes."""
        if not isinstance(v, str):
            self._admin_token = v
            return
        tok = v.strip().strip('"').strip("'")
        if tok.lower().startswith("bearer "):
            tok = tok[7:].strip()
        self._admin_token = tok

    # alias kompatibilitas (kalau ada code lama)
    @property
    def admin_bearer(self) -> str | None:
        return self._admin_token

    @admin_bearer.setter
    def admin_bearer(self, v: str | None):
        self.admin_token = v

    # ---------------- Device ----------------

    
    def recognize_multi(self, jpg_bytes: bytes) -> dict:
        """Send full frame for multi-face recognition (max 5 faces)"""
        if not jpg_bytes or len(jpg_bytes) == 0:
            raise ValueError("Empty image data")
        
        url = f"{self.base_url}/v1/recognize_multi"
        headers = {"X-Device-Id": self.device_id, "X-Device-Token": self.device_token}
        files = {"file": ("frame.jpg", jpg_bytes, "image/jpeg")}

        try:
            logger.debug(f"Sending multi-face request: {len(jpg_bytes)} bytes")
            r = self.session.post(url, headers=headers, files=files, timeout=self.timeout)
            
            if r.status_code >= 400:
                # Server error (but reachable) - do not queue
                try:
                    error_data = r.json()
                    raise RuntimeError(f"API error {r.status_code}: {error_data.get('detail', r.text)}")
                except json.JSONDecodeError:
                    raise RuntimeError(f"API error {r.status_code}: {r.text}")
            
            result = r.json()
            logger.debug(f"Multi-face response: {len(result.get('faces', []))} faces")
            
            # If successful, check if we have queued items to flush
            self._flush_queue_in_background()
            
            return result
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # OFFLINE DETECTED - QUEUE IT
            logger.warning("Offline detected! Queuing request...")
            self._save_to_queue(jpg_bytes)
            # Return empty "success" so app doesn't crash
            return {
                "status": "offline_queued",
                "faces": [],
                "recognized_names": [],
                "combined_audio": "Sistem sedang offline. Data disimpan dan akan dikirim nanti."
            }
        except Exception as e:
            logger.error(f"Unexpected error in recognize_multi: {e}")
            raise

    # ---------------- Offline Queue ----------------
    def _save_to_queue(self, jpg_bytes: bytes):
        """Save failed request to local disk"""
        try:
            queue_dir = "offline_queue"
            if not os.path.exists(queue_dir):
                os.makedirs(queue_dir)
            
            import base64
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"req_{timestamp}.json"
            filepath = os.path.join(queue_dir, filename)
            
            # Encode image
            b64_img = base64.b64encode(jpg_bytes).decode('utf-8')
            
            data = {
                "timestamp": timestamp,
                "image_b64": b64_img,
                "retry_count": 0
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f)
            
            logger.info(f"Saved connection request to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save offline queue: {e}")

    def _flush_queue_in_background(self):
        """Trigger queue flush (simple check, assume threaded elsewhere or quick check)"""
        # For simplicity, we just check if dir exists and has files
        # Ideally this should be a separate thread, but let's check count first
        queue_dir = "offline_queue"
        if not os.path.exists(queue_dir):
            return
            
        files = [f for f in os.listdir(queue_dir) if f.endswith(".json")]
        if not files:
            return
            
        # Only start a flush if not already flushing (simple flag needed)
        # For now, let's just process ONE item per successful request to avoid blocking
        # or implement a proper background worker in App
        pass 
        
    def process_offline_queue(self) -> int:
        """Process all queued offline requests. Call this from a background thread."""
        queue_dir = "offline_queue"
        if not os.path.exists(queue_dir):
            return 0
            
        files = sorted([f for f in os.listdir(queue_dir) if f.endswith(".json")])
        if not files:
            return 0
        
        logger.info(f"Processing offline queue: {len(files)} items")
        processed = 0
        
        import base64
        
        for filename in files:
            filepath = os.path.join(queue_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                img_bytes = base64.b64decode(data["image_b64"])
                
                # Send (blocking)
                url = f"{self.base_url}/v1/recognize_multi"
                headers = {"X-Device-Id": self.device_id, "X-Device-Token": self.device_token}
                files_payload = {"file": ("queued_frame.jpg", img_bytes, "image/jpeg")}
                
                r = self.session.post(url, headers=headers, files=files_payload, timeout=self.timeout)
                
                if r.status_code < 400:
                    # Success
                    os.remove(filepath)
                    processed += 1
                    logger.info(f"Synced queued item {filename}")
                else:
                    logger.warning(f"Failed to sync {filename}: {r.status_code}")
                    # Keep file, maybe retry later
                    
            except Exception as e:
                logger.error(f"Error processing queue file {filename}: {e}")
                # If file is corrupt, delete it
                if "JSONDecodeError" in str(e):
                    os.remove(filepath)
        
        return processed

    # ---------------- Admin Auth ----------------
    def admin_login(self, username: str, password: str) -> dict:
        """Admin login with improved validation and error handling"""
        if not username or not password:
            raise ValueError("Username and password are required")
        
        if len(username) > 100 or len(password) > 100:
            raise ValueError("Username or password too long")
        
        url = f"{self.base_url}/admin/login"
        
        try:
            logger.info(f"Admin login attempt for user: {username}")
            r = self.session.post(
                url,
                json={"username": username, "password": password},
                timeout=self.timeout,
            )
            
            if r.status_code == 401:
                raise RuntimeError("Invalid username or password")
            elif r.status_code == 429:
                raise RuntimeError("Too many login attempts - please wait")
            elif r.status_code >= 500:
                raise RuntimeError(f"Server error: {r.status_code}")
            elif r.status_code >= 400:
                try:
                    error_data = r.json()
                    raise RuntimeError(f"Login error: {error_data.get('detail', r.text)}")
                except json.JSONDecodeError:
                    raise RuntimeError(f"Login error: {r.text}")

            data = r.json()
            token = data.get("access_token") or data.get("token") or data.get("jwt")
            if not token:
                raise RuntimeError(f"Token not found in login response: {data}")

            self.admin_token = token
            logger.info(f"Admin login successful for user: {username}")
            return data
            
        except requests.exceptions.Timeout:
            raise RuntimeError("Login timeout - server not responding")
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Connection error during login")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error during login: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in admin_login: {str(e)}")
            raise

    def _admin_headers(self) -> dict:
        if not self.admin_token:
            return {}
        return {"Authorization": f"Bearer {self.admin_token}"}

    def _admin_request(self, method: str, path: str, **kwargs):
        if not self.admin_token:
            raise RuntimeError("Belum login admin.")

        url = f"{self.base_url}{path}"

        headers = kwargs.pop("headers", {}) or {}
        headers = {**headers, **self._admin_headers()}

        # ✅ fix timeout dobel: kalau caller passing timeout, pakai itu
        timeout = kwargs.pop("timeout", self.timeout)

        r = self.session.request(method, url, headers=headers, timeout=timeout, **kwargs)
        if r.status_code >= 400:
            raise RuntimeError(f"{r.status_code} {r.text}")
        return r

    # ---------------- Admin Endpoints ----------------
    def admin_list_persons(self) -> list[dict]:
        return self._admin_request("GET", "/admin/persons").json()

    def admin_create_person(self, name: str) -> dict:
        return self._admin_request("POST", "/admin/persons", json={"name": name}).json()

    def admin_delete_person(self, person_id: int) -> dict:
        """Delete a person by ID"""
        if not isinstance(person_id, int) or person_id <= 0:
            raise ValueError("Invalid person ID")
        return self._admin_request("DELETE", f"/admin/persons/{person_id}").json()

    def admin_monthly_report(self, month: str) -> dict:
        """Get monthly attendance report"""
        return self._admin_request("GET", f"/admin/reports/monthly?month={month}").json()

    def admin_list_events(self, limit=50, offset=0, status=None, name=None, day=None, device_id=None) -> list[dict]:
        """Get attendance events with optional filters"""
        params = []
        if limit:
            params.append(f"limit={limit}")
        if offset:
            params.append(f"offset={offset}")
        if status:
            params.append(f"status={status}")
        if name:
            params.append(f"name={name}")
        if day:
            params.append(f"day={day}")
        if device_id:
            params.append(f"device_id={device_id}")
        
        query_string = "&".join(params) if params else ""
        url = f"/admin/events{f'?{query_string}' if query_string else ''}"
        return self._admin_request("GET", url).json()

    def admin_enroll_person(self, person_id: int, image_paths: list[str]) -> dict:
        """Enroll person with improved file validation and error handling"""
        if not image_paths:
            raise ValueError("No images provided")
        
        if len(image_paths) > 10:  # Limit to 10 images
            raise ValueError("Too many images - maximum 10 allowed")
        
        # Validate person ID
        if not isinstance(person_id, int) or person_id <= 0:
            raise ValueError("Invalid person ID")
        
        files = []
        opened_files = []
        
        try:
            for i, path in enumerate(image_paths):
                if not path or not isinstance(path, str):
                    raise ValueError(f"Invalid image path at index {i}")
                
                # Security: validate file path
                if ".." in path or path.startswith("/") or ":" not in path:
                    raise ValueError(f"Invalid file path: {path}")
                
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Image file not found: {path}")
                
                # Check file size (max 5MB per image)
                file_size = os.path.getsize(path)
                if file_size > 5 * 1024 * 1024:
                    raise ValueError(f"Image too large: {path} ({file_size} bytes)")
                
                # Check file extension
                valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
                if not path.lower().endswith(valid_extensions):
                    raise ValueError(f"Invalid image format: {path}")
                
                f = open(path, 'rb')
                opened_files.append(f)
                
                filename = os.path.basename(path)
                files.append(("files", (filename, f, "image/jpeg")))
            
            logger.info(f"Enrolling person {person_id} with {len(image_paths)} images")
            
            return self._admin_request(
                "POST",
                f"/admin/persons/{person_id}/enroll",
                files=files,
                timeout=120,
            ).json()
            
        except Exception as e:
            logger.error(f"Error enrolling person {person_id}: {str(e)}")
            raise
        finally:
            # Always close opened files
            for f in opened_files:
                try:
                    f.close()
                except Exception as close_error:
                    logger.warning(f"Error closing file: {close_error}")

    def admin_rebuild_cache(self) -> dict:
        # rebuild bisa agak lama
        return self._admin_request("POST", "/admin/rebuild_cache", timeout=120).json()

    def admin_reset_attendance(self) -> dict:
        """Reset all attendance data (for demo)"""
        return self._admin_request("POST", "/admin/reset_attendance").json()

    def admin_create_admin(self, username: str, password: str, setup_token: str | None = None) -> dict:
        """Create admin user.

        Expected API endpoint (to be added in new-api): POST /admin/create_admin
        - If no admin exists yet: requires X-Setup-Token header
        - If admin exists: can be allowed with Authorization: Bearer <token>
        """
        username = (username or "").strip()
        password = password or ""
        if not username or not password:
            raise ValueError("Username and password are required")

        url = f"{self.base_url}/admin/create_admin"

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if setup_token:
            headers["X-Setup-Token"] = setup_token.strip()
        if self.admin_token:
            headers["Authorization"] = f"Bearer {self.admin_token}"

        payload = {"username": username, "password": password}

        try:
            logger.info(f"Create admin attempt: {username}")
            r = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)

            if r.status_code == 404:
                raise RuntimeError(
                    "API belum mendukung create admin. Update API new-api terlebih dahulu (tambahkan endpoint /admin/create_admin)."
                )
            if r.status_code in (401, 403):
                try:
                    err = r.json().get("detail")
                except Exception:
                    err = r.text
                raise RuntimeError(f"Tidak diizinkan membuat admin: {err}")
            if r.status_code >= 500:
                raise RuntimeError(f"Server error: {r.status_code}")
            if r.status_code >= 400:
                try:
                    err = r.json().get("detail")
                except Exception:
                    err = r.text
                raise RuntimeError(f"Create admin error {r.status_code}: {err}")

            return r.json() if r.content else {"ok": True}
        except requests.exceptions.Timeout:
            raise RuntimeError("Request timeout - server not responding")
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Connection error - check network and server")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error: {str(e)}")
