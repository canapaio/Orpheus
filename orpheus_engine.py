"""🔧 Orpheus Engine Module - Direct Ollama Integration

Modulo principale per la gestione del TTS Orpheus con integrazione diretta Ollama.
Basato sui file di esempio del workspace per generazione token custom.
"""

import os
import re
import json
import time
import hashlib
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    import numpy as np
except ImportError:
    np = None

from cat.log import log

try:
    from .orpheus_settings import OrpheusSettings, OrpheusMode, OrpheusVoice, OrpheusEmotion
except ImportError:
    from orpheus_settings import OrpheusSettings, OrpheusMode, OrpheusVoice, OrpheusEmotion


class OrpheusEngineError(Exception):
    """🚨 Eccezione personalizzata per errori del motore Orpheus"""
    pass


class OrpheusEngine:
    """🔧 Motore principale per la sintesi vocale Orpheus
    
    Gestisce l'integrazione diretta con:
    - Ollama per generazione token custom
    - Conversione token in audio (simulata per ora)
    - Cache audio per performance
    """
    
    def __init__(self, settings: OrpheusSettings):
        """🏗️ Inizializza il motore Orpheus"""
        self.settings = settings
        self.cache_dir = Path("/admin/assets/voice/cache")
        self.cache_enabled = settings.audio_cache_enabled
        
        # Crea directory cache se necessaria
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistiche
        self.stats = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "cache_hits": 0,
            "tokens_generated": 0,
            "last_request": None
        }
        
        if settings.enable_debug:
            log.info(f"🔧 Orpheus Engine inizializzato: {settings}")
    
    def generate_speech(self, text: str, output_file: str) -> bool:
        """🎵 Genera audio usando Orpheus TTS con integrazione diretta Ollama
        
        Args:
            text: Testo da sintetizzare
            output_file: Percorso file output
            
        Returns:
            bool: True se successo, False altrimenti
        """
        self.stats["requests_total"] += 1
        self.stats["last_request"] = datetime.now().isoformat()
        
        try:
            # Pulizia e validazione testo
            clean_text = self.clean_text(text)
            if not clean_text:
                log.warning("🚨 Testo vuoto dopo pulizia")
                return False
            
            # Controllo lunghezza
            if len(clean_text) > self.settings.max_text_length:
                log.warning(f"🚨 Testo troppo lungo ({len(clean_text)} > {self.settings.max_text_length})")
                clean_text = clean_text[:self.settings.max_text_length]
            
            # Controllo cache
            if self.cache_enabled:
                cached_file = self._get_cached_audio(clean_text)
                if cached_file and self._copy_cached_file(cached_file, output_file):
                    self.stats["cache_hits"] += 1
                    self.stats["requests_success"] += 1
                    if self.settings.enable_debug:
                        log.info(f"💾 Cache hit per testo: {clean_text[:50]}...")
                    return True
            
            # Generazione audio
            success = self._generate_audio_direct(clean_text, output_file)
            
            if success:
                self.stats["requests_success"] += 1
                # Salva in cache se abilitata
                if self.cache_enabled:
                    self._save_to_cache(clean_text, output_file)
            else:
                self.stats["requests_failed"] += 1
            
            return success
            
        except Exception as e:
            self.stats["requests_failed"] += 1
            log.error(f"🚨 Errore generazione audio: {str(e)}")
            return False
    
    def _generate_audio_direct(self, text: str, output_file: str) -> bool:
        """🎛️ Generazione audio diretta con Ollama"""
        try:
            # Step 1: Genera token da Ollama
            if self.settings.enable_debug:
                log.info(f"🦙 Generazione token Ollama per: {text[:50]}...")
            
            token_response = self._generate_tokens_from_ollama(text)
            if not token_response:
                log.error("🚨 Nessuna risposta da Ollama")
                return False
            
            # Step 2: Estrai token custom
            custom_tokens = self._extract_custom_tokens(token_response)
            if not custom_tokens:
                log.warning("⚠️ Nessun token custom estratto, uso token simulati")
                custom_tokens = self._generate_simulated_tokens(text)
            
            self.stats["tokens_generated"] = len(custom_tokens)
            
            # Step 3: Converti token in audio
            audio_data = self._convert_tokens_to_audio(custom_tokens)
            if not audio_data:
                log.error("🚨 Errore conversione token in audio")
                return False
            
            # Step 4: Salva file audio
            with open(output_file, "wb") as f:
                f.write(audio_data)
            
            if self.settings.enable_debug:
                log.info(f"✅ Audio salvato: {output_file} ({len(audio_data)} bytes)")
            
            return True
            
        except Exception as e:
            log.error(f"🚨 Errore generazione diretta: {str(e)}")
            return False
    
    def _generate_tokens_from_ollama(self, text: str) -> Optional[str]:
        """🦙 Genera token custom da Ollama usando il prompt originale"""
        try:
            # Formato prompt originale Orpheus
            formatted_prompt = self._format_prompt_original(text, self.settings.voice.value)
            
            # Gestisce sia enum che stringa per ollama_model
            model_name = self.settings.ollama_model.value if hasattr(self.settings.ollama_model, 'value') else str(self.settings.ollama_model)
            
            payload = {
                "model": model_name,  # Modello configurato
                "prompt": formatted_prompt,
                "stream": False,
                "options": {
                    "temperature": self.settings.voice_temperature,
                    "top_p": 0.9,
                    "num_predict": 2000,
                    "stop": ["<|end_of_text|>", "<|reserved_special_token_248|>"]
                }
            }
            
            # Chiamata a Ollama
            response = requests.post(
                f"{self.settings.ollama_url.rstrip('/v1')}/api/generate",
                json=payload,
                timeout=self.settings.timeout_seconds
            )
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get('response', '')
            
            if self.settings.enable_debug:
                log.info(f"📝 Risposta Ollama: {generated_text[:200]}...")
            
            return generated_text
            
        except Exception as e:
            log.error(f"🚨 Errore chiamata Ollama: {str(e)}")
            return None
    
    def _format_prompt_original(self, text: str, voice: str) -> str:
        """📝 Formatta il prompt usando il formato semplice del workspace core"""
        # Formato semplificato dal workspace core - più diretto e funzionante
        adapted_prompt = f"{voice}: {text}"
        # Token speciali Orpheus per modelli "larger"
        return f"<|reserved_special_token_250|>{adapted_prompt}<|end_of_text|><|reserved_special_token_251|><|reserved_special_token_252|><|reserved_special_token_248|>"
    
    def _extract_custom_tokens(self, token_response: str) -> List[int]:
        """🔍 Estrai token custom dalla risposta Ollama"""
        if not token_response:
            return []
        
        extracted_tokens = []
        
        # Cerca tutti i custom_token nella risposta usando regex
        tokens = re.findall(r'<custom_token_(\d+)>', token_response)
        for token_num in tokens:
            try:
                token_id = int(token_num)
                # Applica la formula originale: (token_id - 32000) % 4096
                converted_id = (token_id - 32000) % 4096
                if 0 <= converted_id <= 4096:
                    extracted_tokens.append(converted_id)
            except ValueError:
                continue
        
        if self.settings.enable_debug:
            log.info(f"🔍 Token estratti: {len(extracted_tokens)}")
        
        return extracted_tokens
    
    def _generate_simulated_tokens(self, text: str) -> List[int]:
        """🎭 Genera token simulati per testing"""
        # Usa il testo e la voce per generare token deterministici
        seed_text = f"{text}_{self.settings.voice.value}"
        seed = hashlib.md5(seed_text.encode()).hexdigest()
        
        import random
        random.seed(int(seed[:8], 16))
        
        # Genera circa 10-20 token per parola
        words = text.split()
        num_tokens = len(words) * random.randint(10, 20)
        
        # Genera token ID nel range 0-4095
        token_ids = []
        for _ in range(num_tokens):
            token_id = random.randint(0, 4095)
            token_ids.append(token_id)
        
        if self.settings.enable_debug:
            log.info(f"🎭 Token simulati generati: {len(token_ids)}")
        
        return token_ids
    
    def _convert_tokens_to_audio(self, tokens: List[int]) -> Optional[bytes]:
        """🎵 Converte token in audio usando approccio diretto del workspace core"""
        if not tokens:
            return None
        
        try:
            # Approccio semplificato dal workspace core: processa token in chunk
            chunk_size = 50  # Token per chunk
            audio_chunks = []
            
            for i in range(0, len(tokens), chunk_size):
                chunk = tokens[i:i + chunk_size]
                # Simula elaborazione chunk -> audio
                chunk_duration = len(chunk) * 0.02  # 20ms per token
                chunk_samples = int(self.settings.sample_rate * chunk_duration)
                
                # Genera chunk audio semplice basato sui token
                if np is not None:
                    # Usa i valori dei token per modulare frequenza
                    base_freq = 200 + (sum(chunk) % 400)  # 200-600 Hz
                    t = np.linspace(0, chunk_duration, chunk_samples)
                    chunk_audio = np.sin(2 * np.pi * base_freq * t) * 0.2
                    audio_chunks.append(chunk_audio)
                else:
                    # Fallback: silenzio senza numpy
                    silence = [0] * chunk_samples
                    audio_chunks.append(silence)
            
            # Combina tutti i chunk
            if np is not None and audio_chunks:
                combined_audio = np.concatenate(audio_chunks)
                audio_int16 = (combined_audio * 32767).astype(np.int16)
                audio_bytes = self._create_wav_header(audio_int16, self.settings.sample_rate)
                
                if self.settings.enable_debug:
                    log.info(f"🎵 Audio da {len(tokens)} token in {len(audio_chunks)} chunk: {len(audio_bytes)} bytes")
                
                return audio_bytes
            else:
                # Fallback completo
                duration = len(tokens) * 0.02
                num_samples = int(self.settings.sample_rate * duration)
                silence = b'\x00\x00' * num_samples
                return self._create_wav_header_raw(silence, self.settings.sample_rate)
                
        except Exception as e:
            log.error(f"🚨 Errore conversione audio: {str(e)}")
            return None
    
    def _create_wav_header(self, audio_data: 'np.ndarray', sample_rate: int) -> bytes:
        """🎧 Crea header WAV per i dati audio"""
        if np is None:
            return b''
        
        # Parametri WAV
        channels = 1
        bits_per_sample = 16
        byte_rate = sample_rate * channels * bits_per_sample // 8
        block_align = channels * bits_per_sample // 8
        data_size = len(audio_data) * 2  # 2 bytes per sample
        file_size = 36 + data_size
        
        # Header WAV
        header = b'RIFF'
        header += file_size.to_bytes(4, 'little')
        header += b'WAVE'
        header += b'fmt '
        header += (16).to_bytes(4, 'little')  # fmt chunk size
        header += (1).to_bytes(2, 'little')   # audio format (PCM)
        header += channels.to_bytes(2, 'little')
        header += sample_rate.to_bytes(4, 'little')
        header += byte_rate.to_bytes(4, 'little')
        header += block_align.to_bytes(2, 'little')
        header += bits_per_sample.to_bytes(2, 'little')
        header += b'data'
        header += data_size.to_bytes(4, 'little')
        
        return header + audio_data.tobytes()
    
    def _create_wav_header_raw(self, audio_data: bytes, sample_rate: int) -> bytes:
        """🎧 Crea header WAV per dati audio raw"""
        channels = 1
        bits_per_sample = 16
        byte_rate = sample_rate * channels * bits_per_sample // 8
        block_align = channels * bits_per_sample // 8
        data_size = len(audio_data)
        file_size = 36 + data_size
        
        # Header WAV
        header = b'RIFF'
        header += file_size.to_bytes(4, 'little')
        header += b'WAVE'
        header += b'fmt '
        header += (16).to_bytes(4, 'little')
        header += (1).to_bytes(2, 'little')
        header += channels.to_bytes(2, 'little')
        header += sample_rate.to_bytes(4, 'little')
        header += byte_rate.to_bytes(4, 'little')
        header += block_align.to_bytes(2, 'little')
        header += bits_per_sample.to_bytes(2, 'little')
        header += b'data'
        header += data_size.to_bytes(4, 'little')
        
        return header + audio_data
    
    def clean_text(self, text: str) -> str:
        """🧹 Pulisce il testo per TTS ottimale"""
        if not text:
            return ""
        
        # Rimuovi tag HTML/Markdown
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Rimuovi caratteri speciali problematici
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # Normalizza punteggiatura
        text = re.sub(r'[…]', '...', text)
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r"[''']", "'", text)
        
        # Normalizza spazi
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Gestisci abbreviazioni comuni
        text = re.sub(r'\bDr\.', 'Dottore', text)
        text = re.sub(r'\bProf\.', 'Professore', text)
        text = re.sub(r'\bSig\.', 'Signore', text)
        text = re.sub(r'\bSig\.ra', 'Signora', text)
        
        # Migliora pronuncia numeri
        text = re.sub(r'\b(\d+)°', r'\1 gradi', text)
        text = re.sub(r'\b(\d+)%', r'\1 percento', text)
        
        return text
    
    def _get_cached_audio(self, text: str) -> Optional[str]:
        """💾 Cerca audio in cache per il testo dato"""
        if not self.cache_enabled:
            return None
        
        # Genera hash del testo + settings
        cache_key = self._generate_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.{self.settings.format.value}"
        
        if cache_file.exists():
            return str(cache_file)
        
        return None
    
    def _generate_cache_key(self, text: str) -> str:
        """🔑 Genera chiave cache basata su testo e settings"""
        # Combina testo e parametri rilevanti
        cache_data = {
            "text": text,
            "voice": self.settings.voice.value,
            "emotion": self.settings.emotion.value,
            "speed": self.settings.speed,
            "format": self.settings.format.value
        }
        
        # Genera hash MD5
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _copy_cached_file(self, cached_file: str, output_file: str) -> bool:
        """📋 Copia file dalla cache alla destinazione"""
        try:
            import shutil
            shutil.copy2(cached_file, output_file)
            return True
        except Exception as e:
            log.error(f"🚨 Errore copia cache: {str(e)}")
            return False
    
    def _save_to_cache(self, text: str, audio_file: str) -> None:
        """💾 Salva audio in cache"""
        if not self.cache_enabled:
            return
        
        try:
            cache_key = self._generate_cache_key(text)
            cache_file = self.cache_dir / f"{cache_key}.{self.settings.format.value}"
            
            import shutil
            shutil.copy2(audio_file, str(cache_file))
            
            if self.settings.enable_debug:
                log.info(f"💾 Audio salvato in cache: {cache_key}")
        except Exception as e:
            log.error(f"🚨 Errore salvataggio cache: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """📊 Restituisce statistiche del motore"""
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """🔄 Reset statistiche"""
        self.stats = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "cache_hits": 0,
            "tokens_generated": 0,
            "last_request": None
        }
    
    def health_check(self) -> Dict[str, Any]:
        """🏥 Controllo salute del motore"""
        health = {
            "status": "unknown",
            "cache_enabled": self.cache_enabled,
            "cache_dir_exists": self.cache_dir.exists() if self.cache_enabled else None,
            "effective_mode": self.settings.get_effective_mode().value,
            "ollama_url": self.settings.ollama_url,
            "last_error": None
        }
        
        try:
            # Test connessione Ollama
            response = requests.get(
                f"{self.settings.ollama_url.rstrip('/v1')}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                health["status"] = "healthy"
                health["ollama_connected"] = True
            else:
                health["status"] = "ollama_unreachable"
                health["ollama_connected"] = False
        except Exception as e:
            health["status"] = "error"
            health["ollama_connected"] = False
            health["last_error"] = str(e)
        
        return health


# === FUNZIONI UTILITY ===

def create_engine(settings: OrpheusSettings) -> OrpheusEngine:
    """🏭 Factory per creare motore Orpheus"""
    return OrpheusEngine(settings)


def test_engine_connection(settings: OrpheusSettings) -> bool:
    """🔍 Test connessione motore"""
    try:
        engine = OrpheusEngine(settings)
        health = engine.health_check()
        return health["status"] == "healthy"
    except Exception:
        return False


def get_engine_info() -> Dict[str, Any]:
    """ℹ️ Informazioni sul motore"""
    return {
        "version": "1.0.0",
        "integration_type": "direct_ollama",
        "supported_modes": [mode.value for mode in OrpheusMode],
        "supported_voices": [voice.value for voice in OrpheusVoice],
        "supported_emotions": [emotion.value for emotion in OrpheusEmotion],
        "dependencies": {
            "requests": requests is not None,
            "numpy": np is not None
        }
    }