"""🐱 Orpheus Cat Integration Module - Direct Ollama

Modulo di integrazione tra Orpheus TTS e Cheshire Cat.
Utilizza l'approccio diretto con Ollama per la generazione di token custom.
"""

import os
import re
import subprocess
import threading
from pathlib import Path
from typing import Dict, Any, Optional

from cat.log import log
from cat.mad_hatter.decorators import hook

from .orpheus_settings import (
    OrpheusSettings, 
    get_default_settings,
    validate_settings,
    OrpheusVoice,
    OrpheusEmotion,
    OrpheusFormat,
    OrpheusMode
)
from .orpheus_engine import OrpheusEngine, create_engine


# === CONFIGURAZIONE GLOBALE ===

# Istanza globale del motore Orpheus
_orpheus_engine: Optional[OrpheusEngine] = None
_engine_lock = threading.Lock()


def get_orpheus_engine() -> Optional[OrpheusEngine]:
    """🔧 Ottiene l'istanza globale del motore Orpheus"""
    global _orpheus_engine
    with _engine_lock:
        return _orpheus_engine


def init_orpheus_engine(settings: OrpheusSettings) -> bool:
    """🏗️ Inizializza il motore Orpheus globale"""
    global _orpheus_engine
    
    try:
        with _engine_lock:
            _orpheus_engine = create_engine(settings)
            
        if settings.enable_debug:
            log.info("🔧 Motore Orpheus inizializzato con successo")
        
        return True
        
    except Exception as e:
        log.error(f"🚨 Errore inizializzazione motore Orpheus: {str(e)}")
        return False


# === SCHEMA SETTINGS PER CHESHIRE CAT ===

@hook
def settings_schema():
    """📋 Schema delle impostazioni per Cheshire Cat"""
    return {
        "orpheus_tts": {
            "type": "object",
            "title": "🎵 Orpheus TTS Settings",
            "description": "Configurazione per il plugin Orpheus TTS con integrazione diretta Ollama",
            "properties": {
                # === CONFIGURAZIONE BASE ===
                "ollama_url": {
                    "type": "string",
                    "title": "🦙 Ollama URL",
                    "description": "URL del server Ollama per generazione token",
                    "default": "http://localhost:11434"
                },
                "voice": {
                    "type": "string",
                    "title": "🎤 Voce",
                    "description": "Voce da utilizzare per la sintesi",
                    "enum": [voice.value for voice in OrpheusVoice],
                    "default": OrpheusVoice.tara.value
                },
                "emotion": {
                    "type": "string",
                    "title": "😊 Emozione",
                    "description": "Emozione da applicare alla voce",
                    "enum": [emotion.value for emotion in OrpheusEmotion],
                    "default": OrpheusEmotion.neutral.value
                },
                "speed": {
                    "type": "number",
                    "title": "⚡ Velocità",
                    "description": "Velocità di riproduzione (0.5 - 2.0)",
                    "minimum": 0.5,
                    "maximum": 2.0,
                    "default": 1.0
                },
                "format": {
                    "type": "string",
                    "title": "🎧 Formato Audio",
                    "description": "Formato del file audio generato",
                    "enum": [fmt.value for fmt in OrpheusFormat],
                    "default": OrpheusFormat.wav.value
                },
                
                # === DEBUG E CONTROLLO ===
                "enable_debug": {
                    "type": "boolean",
                    "title": "🐛 Debug",
                    "description": "Abilita logging dettagliato",
                    "default": False
                },
                "enable_tts": {
                    "type": "boolean",
                    "title": "🔊 Abilita TTS",
                    "description": "Abilita/disabilita completamente il TTS",
                    "default": True
                }
            }
        }
    }


# === FUNZIONI UTILITY ===

def clean_text_for_tts(text: str) -> str:
    """🧹 Pulisce il testo per TTS ottimale usando librerie specializzate"""
    if not text:
        return ""
    
    try:
        import bleach
        
        # Rimuovi tutti i tag HTML mantenendo solo il testo
        text = bleach.clean(text, tags=[], strip=True)
        
    except ImportError:
        # Fallback per rimozione HTML se bleach non è disponibile
        text = re.sub(r'<[^>]+>', '', text)
    
    # Gestisci markdown (sempre necessario, anche con bleach)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Link markdown
    
    # Rimuovi caratteri speciali problematici
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    
    # Normalizza punteggiatura
    text = re.sub(r'\u2026', '...', text)  # …
    text = re.sub(r'[\u201C\u201D\u201E]', '"', text)  # "",",„
    text = re.sub(r'[\u2018\u2019\u201A]', "'", text)  # '',',`
    text = re.sub(r'[\u2013\u2014]', '-', text)  # –,—
    
    # Normalizza spazi
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Gestisci abbreviazioni comuni italiane
    text = re.sub(r'\bDr\.', 'Dottore', text)
    text = re.sub(r'\bProf\.', 'Professore', text)
    text = re.sub(r'\bSig\.', 'Signore', text)
    text = re.sub(r'\bSig\.ra', 'Signora', text)
    text = re.sub(r'\bIng\.', 'Ingegnere', text)
    text = re.sub(r'\bAvv\.', 'Avvocato', text)
    
    # Migliora pronuncia numeri e simboli
    text = re.sub(r'\b(\d+)°', r'\1 gradi', text)
    text = re.sub(r'\b(\d+)%', r'\1 percento', text)
    text = re.sub(r'\b(\d+)€', r'\1 euro', text)
    text = re.sub(r'\$(\d+)', r'\1 dollari', text)
    
    return text


def map_cat_settings_to_orpheus(cat_settings: Dict[str, Any]) -> OrpheusSettings:
    """🗺️ Mappa le impostazioni di Cheshire Cat a quelle di Orpheus"""
    orpheus_config = cat_settings.get("orpheus_tts", {})
    
    # Crea settings Orpheus base e aggiorna solo i valori presenti in Cat
    settings = OrpheusSettings()
    
    # Aggiorna solo i parametri configurabili dall'interfaccia Cat
    if "ollama_url" in orpheus_config:
        settings.ollama_url = orpheus_config["ollama_url"]
    if "voice" in orpheus_config:
        settings.voice = OrpheusVoice(orpheus_config["voice"])
    if "emotion" in orpheus_config:
        settings.emotion = OrpheusEmotion(orpheus_config["emotion"])
    if "speed" in orpheus_config:
        settings.speed = orpheus_config["speed"]
    if "format" in orpheus_config:
        settings.format = OrpheusFormat(orpheus_config["format"])
    if "enable_debug" in orpheus_config:
        settings.enable_debug = orpheus_config["enable_debug"]
    if "enable_tts" in orpheus_config:
        settings.enable_tts = orpheus_config["enable_tts"]
    
    return settings


def play_audio_file(audio_file: str, settings: OrpheusSettings) -> bool:
    """🔊 Riproduce file audio usando il player di sistema"""
    if not os.path.exists(audio_file):
        log.error(f"🚨 File audio non trovato: {audio_file}")
        return False
    
    try:
        if settings.enable_debug:
            log.info(f"🔊 Riproduzione audio: {audio_file}")
        
        # Determina comando di riproduzione basato su OS
        if os.name == 'nt':  # Windows
            # Usa PowerShell per riprodurre audio
            cmd = [
                "powershell", "-c",
                f"(New-Object Media.SoundPlayer '{audio_file}').PlaySync()"
            ]
        else:  # Linux/Mac
            # Prova diversi player audio
            players = ['aplay', 'paplay', 'afplay', 'play']
            cmd = None
            for player in players:
                if subprocess.run(['which', player], capture_output=True).returncode == 0:
                    cmd = [player, audio_file]
                    break
        
        if cmd:
            # Esegui in background per non bloccare
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        else:
            log.warning("⚠️ Nessun player audio trovato")
            return False
            
    except Exception as e:
        log.error(f"🚨 Errore riproduzione audio: {str(e)}")
        return False


# === HOOK PRINCIPALE CHESHIRE CAT ===

@hook
def before_cat_sends_message(message, cat):
    """🎵 Hook principale: genera e riproduce audio prima che il Cat invii il messaggio
    
    Questo hook viene chiamato prima che Cheshire Cat invii una risposta all'utente.
    Genera l'audio TTS del messaggio e lo riproduce.
    """
    try:
        # Ottieni settings dal Cat
        cat_settings = cat.mad_hatter.get_plugin_settings()
        orpheus_settings = map_cat_settings_to_orpheus(cat_settings)
        
        # Controlla se TTS è abilitato
        if not orpheus_settings.enable_tts:
            if orpheus_settings.enable_debug:
                log.info("🔇 TTS disabilitato nelle impostazioni")
            return message
        
        # Inizializza motore se necessario
        engine = get_orpheus_engine()
        if not engine:
            if not init_orpheus_engine(orpheus_settings):
                log.error("🚨 Impossibile inizializzare motore Orpheus")
                return message
            engine = get_orpheus_engine()
        
        # Pulisci testo per TTS
        clean_text = clean_text_for_tts(message)
        if not clean_text:
            if orpheus_settings.enable_debug:
                log.info("📝 Testo vuoto dopo pulizia, skip TTS")
            return message
        
        # Controlla lunghezza testo
        if len(clean_text) > orpheus_settings.max_text_length:
            if orpheus_settings.enable_debug:
                log.warning(f"📏 Testo troncato: {len(clean_text)} > {orpheus_settings.max_text_length}")
            clean_text = clean_text[:orpheus_settings.max_text_length]
        
        # Genera nome file audio temporaneo
        import tempfile
        import time
        timestamp = int(time.time() * 1000)
        temp_dir = Path(tempfile.gettempdir()) / "orpheus_tts"
        temp_dir.mkdir(exist_ok=True)
        
        audio_file = temp_dir / f"orpheus_{timestamp}.{orpheus_settings.format.value}"
        
        # Genera audio
        if orpheus_settings.enable_debug:
            log.info(f"🎵 Generazione TTS per: {clean_text[:50]}...")
        
        success = engine.generate_speech(clean_text, str(audio_file))
        
        if success and audio_file.exists():
            # Riproduce audio in background
            threading.Thread(
                target=play_audio_file,
                args=(str(audio_file), orpheus_settings),
                daemon=True
            ).start()
            
            if orpheus_settings.enable_debug:
                log.info(f"✅ TTS completato: {audio_file}")
        else:
            log.error("🚨 Errore generazione TTS")
        
        # Cleanup file temporaneo dopo un po'
        def cleanup_temp_file():
            import time
            time.sleep(10)  # Aspetta 10 secondi
            try:
                if audio_file.exists():
                    audio_file.unlink()
            except Exception:
                pass
        
        threading.Thread(target=cleanup_temp_file, daemon=True).start()
        
    except Exception as e:
        log.error(f"🚨 Errore hook TTS: {str(e)}")
    
    # Restituisce sempre il messaggio originale
    return message


# === HOOK AGGIUNTIVI ===

@hook
def plugin_settings_load():
    """⚙️ Hook chiamato quando le impostazioni del plugin vengono caricate"""
    try:
        log.info("🔧 Orpheus TTS Plugin caricato")
        
        # Qui potresti fare inizializzazioni aggiuntive se necessario
        # Ad esempio, verificare la connessione a Ollama
        
    except Exception as e:
        log.error(f"🚨 Errore caricamento plugin: {str(e)}")


@hook  
def plugin_settings_save(settings):
    """💾 Hook chiamato quando le impostazioni del plugin vengono salvate"""
    try:
        if settings.get("orpheus_tts", {}).get("enable_debug", False):
            log.info("💾 Impostazioni Orpheus TTS salvate")
        
        # Reinizializza il motore con le nuove impostazioni
        global _orpheus_engine
        with _engine_lock:
            _orpheus_engine = None
        
        # Il motore verrà reinizializzato al prossimo utilizzo
        
    except Exception as e:
        log.error(f"🚨 Errore salvataggio impostazioni: {str(e)}")


# === FUNZIONI DI UTILITÀ PER DEBUG ===

def get_plugin_status() -> Dict[str, Any]:
    """📊 Ottiene lo stato del plugin per debug"""
    engine = get_orpheus_engine()
    
    status = {
        "plugin_loaded": True,
        "engine_initialized": engine is not None,
        "engine_stats": engine.get_stats() if engine else None,
        "engine_health": engine.health_check() if engine else None
    }
    
    return status


def test_tts_generation(text: str = "Ciao, questo è un test di Orpheus TTS") -> bool:
    """🧪 Test rapido di generazione TTS"""
    try:
        # Usa settings di default
        settings = get_default_settings()
        settings.enable_debug = True
        
        # Inizializza motore
        if not init_orpheus_engine(settings):
            return False
        
        engine = get_orpheus_engine()
        if not engine:
            return False
        
        # Test generazione
        import tempfile
        temp_file = Path(tempfile.gettempdir()) / "orpheus_test.wav"
        
        success = engine.generate_speech(text, str(temp_file))
        
        if success and temp_file.exists():
            log.info(f"✅ Test TTS riuscito: {temp_file}")
            # Cleanup
            temp_file.unlink()
            return True
        else:
            log.error("🚨 Test TTS fallito")
            return False
            
    except Exception as e:
        log.error(f"🚨 Errore test TTS: {str(e)}")
        return False