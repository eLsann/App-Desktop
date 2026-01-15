"""
Edge TTS Engine with pyttsx3 Fallback
Uses Microsoft Edge neural voices with fallback to local pyttsx3
"""
import os
import time
import hashlib
import threading
import asyncio
from dataclasses import dataclass
from pathlib import Path
from logger_config import get_logger

logger = get_logger("tts")

# Cache directory
CACHE_DIR = Path("tts_cache")
CACHE_DIR.mkdir(exist_ok=True)


@dataclass
class TTSConfig:
    edge_voice: str = "id-ID-ArdiNeural"
    volume: float = 1.0
    rate: str = "+0%"
    pitch: str = "+0Hz"
    use_pyttsx_fallback: bool = True


class TTSEngine:
    """TTS with Edge TTS + pyttsx3 fallback for reliability"""
    
    def __init__(self, cfg: TTSConfig = None):
        self.cfg = cfg or TTSConfig()
        self._lock = threading.Lock()
        self._last_key = None
        self._last_time = 0.0
        self._pyttsx_engine = None
        self._mixer_ready = False
        self._edge_available = True
        
        self._init_mixer()
        self._init_pyttsx()
        
        logger.info(f"TTS Engine initialized - Voice: {self.cfg.edge_voice}")
    
    def _init_mixer(self):
        """Initialize pygame mixer"""
        try:
            import pygame
            pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=512)
            self._mixer_ready = True
            logger.info("Pygame mixer ready")
        except Exception as e:
            logger.warning(f"Pygame mixer failed: {e}")
    
    def _init_pyttsx(self):
        """Initialize pyttsx3 as fallback"""
        try:
            import pyttsx3
            self._pyttsx_engine = pyttsx3.init()
            self._pyttsx_engine.setProperty('rate', 150)
            self._pyttsx_engine.setProperty('volume', self.cfg.volume)
            logger.info("pyttsx3 fallback ready")
        except Exception as e:
            logger.warning(f"pyttsx3 init failed: {e}")
    
    def _get_cache_path(self, text: str) -> Path:
        """Get cache file path based on text hash"""
        cache_key = f"{text}_{self.cfg.edge_voice}"
        text_hash = hashlib.md5(cache_key.encode()).hexdigest()[:16]
        return CACHE_DIR / f"tts_{text_hash}.mp3"
    
    def speak_once(self, key: str, text: str, cooldown: float = 4.0):
        """Speak with cooldown to avoid repetition"""
        if not text or not isinstance(text, str):
            return
        
        text = text.strip()
        if len(text) > 300:
            text = text[:300]
        
        now = time.time()
        with self._lock:
            if self._last_key == key and (now - self._last_time) < cooldown:
                return
            self._last_key = key
            self._last_time = now
        
        threading.Thread(target=self._speak, args=(text,), daemon=True).start()
    
    def _speak(self, text: str):
        """Speak text with Edge TTS or fallback"""
        cache_path = self._get_cache_path(text)
        
        # Try cache first
        if cache_path.exists() and cache_path.stat().st_size > 1000:
            logger.debug(f"Playing from cache")
            if self._play_audio(cache_path):
                return
        
        # Try Edge TTS
        if self._edge_available:
            success = self._try_edge_tts(text, cache_path)
            if success:
                return
        
        # Fallback to pyttsx3
        logger.info("Using pyttsx3 fallback")
        self._speak_pyttsx(text)
    
    def _try_edge_tts(self, text: str, cache_path: Path) -> bool:
        """Try generating audio with Edge TTS"""
        try:
            asyncio.run(self._generate_edge_tts(text, cache_path))
            if cache_path.exists() and cache_path.stat().st_size > 1000:
                return self._play_audio(cache_path)
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                logger.warning("Edge TTS rate limited, using fallback")
                self._edge_available = False
            else:
                logger.error(f"Edge TTS error: {e}")
        return False
    
    async def _generate_edge_tts(self, text: str, output_path: Path):
        """Generate audio with Edge TTS"""
        import edge_tts
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.cfg.edge_voice,
            rate=self.cfg.rate,
            pitch=self.cfg.pitch
        )
        await communicate.save(str(output_path))
    
    def _play_audio(self, audio_path: Path) -> bool:
        """Play audio file using pygame"""
        if not self._mixer_ready:
            return False
        
        try:
            import pygame
            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.set_volume(self.cfg.volume)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
            return True
            
        except Exception as e:
            logger.warning(f"Pygame playback failed: {e}")
            # Delete corrupt file
            try:
                audio_path.unlink()
            except:
                pass
            return False
    
    def _speak_pyttsx(self, text: str):
        """Speak using pyttsx3 (local, always works)"""
        if not self._pyttsx_engine:
            return
        try:
            self._pyttsx_engine.say(text)
            self._pyttsx_engine.runAndWait()
        except Exception as e:
            logger.error(f"pyttsx3 error: {e}")
    
    def preload_common_greetings(self, names: list[str]):
        """Pre-generate greetings (skipped if Edge TTS unavailable)"""
        if not self._edge_available:
            logger.info("Preload skipped - using pyttsx3 fallback")
            return
            
        templates = [
            "Halo {name}, absensi masuk berhasil.",
            "Terima kasih {name}, absensi pulang berhasil.",
            "Halo {name}, mohon tunggu sebentar.",
        ]
        
        def _preload():
            count = 0
            for name in names[:5]:  # Limit to first 5 names
                for template in templates:
                    text = template.format(name=name)
                    cache_path = self._get_cache_path(text)
                    if not cache_path.exists():
                        try:
                            asyncio.run(self._generate_edge_tts(text, cache_path))
                            count += 1
                            time.sleep(0.5)  # Rate limit delay
                        except Exception as e:
                            if "403" in str(e):
                                self._edge_available = False
                                logger.warning("Preload stopped - rate limited")
                                return
            if count > 0:
                logger.info(f"Preloaded {count} audio files")
        
        threading.Thread(target=_preload, daemon=True).start()
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            import pygame
            if self._mixer_ready:
                pygame.mixer.quit()
        except:
            pass
        
        if self._pyttsx_engine:
            try:
                self._pyttsx_engine.stop()
            except:
                pass
        
        logger.info("TTS engine cleaned up")
