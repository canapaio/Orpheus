"""🎭 Orpheus Settings Module

Modulo per la gestione delle configurazioni del plugin Orpheus TTS.
Contiene tutte le impostazioni, enum e validazioni per il plugin.
"""

from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional


class OrpheusVoice(str, Enum):
    """🎵 Enum per le voci disponibili in Orpheus"""
    tara = "tara"           # Femminile, espressiva, versatile
    alex = "alex"           # Maschile, professionale, chiara
    sarah = "sarah"         # Femminile, dolce, calda
    emma = "emma"           # Femminile, giovane, energica
    daniel = "daniel"       # Maschile, seria, autorevole
    michael = "michael"     # Maschile, profonda, sicura
    nova = "nova"           # Femminile, moderna, tecnologica
    echo = "echo"           # Speciale, effetti unici


class OrpheusEmotion(str, Enum):
    """😊 Enum per le emozioni supportate"""
    neutral = "neutral"         # Tono neutro, standard
    happy = "happy"             # Allegro, positivo
    sad = "sad"                 # Triste, malinconico
    angry = "angry"             # Arrabbiato, intenso
    excited = "excited"         # Eccitato, entusiasta
    calm = "calm"               # Calmo, rilassato
    mysterious = "mysterious"   # Misterioso, intrigante


class OrpheusFormat(str, Enum):
    """📁 Enum per i formati audio supportati"""
    mp3 = "mp3"     # Formato compresso, compatibile
    wav = "wav"     # Formato non compresso, alta qualità
    flac = "flac"   # Formato lossless, qualità massima
    opus = "opus"   # Formato moderno, efficiente


class OrpheusMode(str, Enum):
    """⚡ Enum per le modalità di funzionamento"""
    ollama_direct = "ollama_direct"     # Integrazione diretta Ollama + SNAC


class OrpheusModel(str, Enum):
    """🤖 Enum per i modelli Orpheus disponibili"""
    # Modello principale inglese - TESTATO E FUNZIONANTE
    english_3b = "hf.co/unsloth/orpheus-3b-0.1-ft-GGUF:Q8_0"
    italian_spanish_3b = "hf.co/unsloth/orpheus-3b-0.1-ft-GGUF:Q8_0"    # Italiano/Spagnolo, 3B
    korean_3b = "hf.co/unsloth/orpheus-3b-0.1-ft-GGUF:Q8_0"             # Coreano, 3B parametri
    french_3b = "hf.co/unsloth/orpheus-3b-0.1-ft-GGUF:Q8_0"             # Francese, 3B parametri
    german_3b = "hf.co/unsloth/orpheus-3b-0.1-ft-GGUF:Q8_0"             # Tedesco, 3B parametri
    chinese_3b = "hf.co/unsloth/orpheus-3b-0.1-ft-GGUF:Q8_0"            # Cinese, 3B parametri
    hindi_3b = "hf.co/unsloth/orpheus-3b-0.1-ft-GGUF:Q8_0"              # Hindi, 3B parametri


class OrpheusSettings(BaseModel):
    """⚙️ Configurazioni principali del plugin Orpheus
    
    Gestisce tutti i parametri configurabili del plugin TTS Orpheus
    per l'integrazione con Cheshire Cat.
    """
    
    # === CONFIGURAZIONE ENDPOINTS ===
    ollama_url: str = Field(
        default="http://localhost:11434",
        description="URL base per Ollama endpoint (integrazione diretta)"
    )
    
    ollama_model: OrpheusModel = Field(
        default=OrpheusModel.english_3b,
        description="Modello Ollama da utilizzare per la generazione TTS"
    )
    
    # === PARAMETRI VOCALI ===
    voice: OrpheusVoice = Field(
        default=OrpheusVoice.tara,
        description="Voce selezionata per la sintesi vocale"
    )
    
    emotion: OrpheusEmotion = Field(
        default=OrpheusEmotion.neutral,
        description="Emozione da applicare alla sintesi vocale"
    )
    
    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Velocità di riproduzione (0.5x - 2.0x)"
    )
    
    # === FORMATO OUTPUT ===
    format: OrpheusFormat = Field(
        default=OrpheusFormat.mp3,
        description="Formato audio di output"
    )
    
    # === MODALITÀ OPERATIVA ===
    mode: OrpheusMode = Field(
        default=OrpheusMode.ollama_direct,
        description="Modalità di funzionamento del TTS"
    )
    
    # === OPZIONI AVANZATE ===
    
    enable_emotional_synthesis: bool = Field(
        default=True,
        description="Abilita sintesi emotiva avanzata"
    )
    
    # === CONTROLLO QUALITÀ ===
    sample_rate: int = Field(
        default=22050,
        description="Sample rate audio (Hz)"
    )
    
    bit_depth: int = Field(
        default=16,
        description="Profondità bit audio"
    )
    
    # === TIMEOUT E PERFORMANCE ===
    timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Timeout per generazione audio (secondi)"
    )
    
    max_text_length: int = Field(
        default=1000,
        ge=100,
        le=5000,
        description="Lunghezza massima testo per TTS"
    )
    
    # === PERSONALIZZAZIONE ===
    custom_voice_path: Optional[str] = Field(
        default=None,
        description="Percorso a voce personalizzata (opzionale)"
    )
    
    voice_temperature: float = Field(
        default=0.7,
        ge=0.1,
        le=1.0,
        description="Temperatura per variabilità vocale"
    )
    
    # === DEBUG E LOGGING ===
    enable_debug: bool = Field(
        default=False,
        description="Abilita logging debug dettagliato"
    )
    
    save_audio_files: bool = Field(
        default=True,
        description="Salva file audio generati"
    )
    
    audio_cache_enabled: bool = Field(
        default=True,
        description="Abilita cache audio per testi ripetuti"
    )
    
    @field_validator('ollama_url')
    @classmethod
    def validate_ollama_url(cls, v):
        """Valida che l'URL Ollama sia ben formato"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL deve iniziare con http:// o https://')
        if not v.endswith('/v1'):
            v = v.rstrip('/') + '/v1'
        return v
    
    @field_validator('speed')
    @classmethod
    def validate_speed(cls, v):
        """Valida velocità di riproduzione"""
        if not 0.5 <= v <= 2.0:
            raise ValueError('Velocità deve essere tra 0.5 e 2.0')
        return v
    
    @field_validator('voice_temperature')
    @classmethod
    def validate_temperature(cls, v):
        """Valida temperatura vocale"""
        if not 0.1 <= v <= 1.0:
            raise ValueError('Temperatura deve essere tra 0.1 e 1.0')
        return v
    
    @field_validator('sample_rate')
    @classmethod
    def validate_sample_rate(cls, v):
        """Valida sample rate audio"""
        valid_rates = [8000, 16000, 22050, 44100, 48000]
        if v not in valid_rates:
            raise ValueError(f'Sample rate deve essere uno di: {valid_rates}')
        return v
    
    @field_validator('bit_depth')
    @classmethod
    def validate_bit_depth(cls, v):
        """Valida profondità bit"""
        if v not in [8, 16, 24, 32]:
            raise ValueError('Bit depth deve essere 8, 16, 24 o 32')
        return v
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True,
        "extra": "forbid",
        "json_schema_extra": {
            "example": {
                "ollama_url": "http://localhost:11434/v1",
                "ollama_model": "italian_spanish_3b",
                "voice": "tara",
                "emotion": "neutral",
                "speed": 1.0,
                "format": "mp3",
                "mode": "auto",
                "enable_emotional_synthesis": True,
                "timeout_seconds": 30,
                "enable_debug": False
            }
        }
    }
    
    def get_voice_description(self) -> str:
        """🎵 Restituisce descrizione della voce selezionata"""
        voice_descriptions = {
            OrpheusVoice.tara: "Femminile, espressiva, versatile",
            OrpheusVoice.alex: "Maschile, professionale, chiara",
            OrpheusVoice.sarah: "Femminile, dolce, calda",
            OrpheusVoice.emma: "Femminile, giovane, energica",
            OrpheusVoice.daniel: "Maschile, seria, autorevole",
            OrpheusVoice.michael: "Maschile, profonda, sicura",
            OrpheusVoice.nova: "Femminile, moderna, tecnologica",
            OrpheusVoice.echo: "Speciale, effetti unici"
        }
        return voice_descriptions.get(self.voice, "Voce sconosciuta")
    
    def get_emotion_description(self) -> str:
        """😊 Restituisce descrizione dell'emozione selezionata"""
        emotion_descriptions = {
            OrpheusEmotion.neutral: "Tono neutro, standard",
            OrpheusEmotion.happy: "Allegro, positivo",
            OrpheusEmotion.sad: "Triste, malinconico",
            OrpheusEmotion.angry: "Arrabbiato, intenso",
            OrpheusEmotion.excited: "Eccitato, entusiasta",
            OrpheusEmotion.calm: "Calmo, rilassato",
            OrpheusEmotion.mysterious: "Misterioso, intrigante"
        }
        return emotion_descriptions.get(self.emotion, "Emozione sconosciuta")
    
    def get_effective_mode(self) -> OrpheusMode:
        """⚡ Determina modalità effettiva basata su configurazione"""
        if self.mode == OrpheusMode.auto:
            return OrpheusMode.ollama_direct if self.use_ollama_direct else OrpheusMode.fastapi
        return self.mode
    
    def to_dict(self) -> dict:
        """📋 Converte settings in dizionario per logging/debug"""
        return self.dict()
    
    def __str__(self) -> str:
        """🔍 Rappresentazione stringa per debug"""
        return f"OrpheusSettings(voice={self.voice}, emotion={self.emotion}, mode={self.get_effective_mode()})"


# === FUNZIONI UTILITY ===

def get_default_settings() -> OrpheusSettings:
    """🏭 Factory per settings di default"""
    return OrpheusSettings()


def validate_settings(settings_dict: dict) -> OrpheusSettings:
    """✅ Valida e crea settings da dizionario"""
    try:
        return OrpheusSettings(**settings_dict)
    except Exception as e:
        raise ValueError(f"Configurazione non valida: {str(e)}")


def get_available_voices() -> list[str]:
    """🎵 Lista voci disponibili"""
    return [voice.value for voice in OrpheusVoice]


def get_available_emotions() -> list[str]:
    """😊 Lista emozioni disponibili"""
    return [emotion.value for emotion in OrpheusEmotion]


def get_available_formats() -> list[str]:
    """📁 Lista formati disponibili"""
    return [format.value for format in OrpheusFormat]


def get_available_models() -> list[str]:
    """🤖 Lista modelli disponibili"""
    return [model.value for model in OrpheusModel]


def get_model_description(model: OrpheusModel) -> str:
    """🤖 Restituisce descrizione del modello"""
    descriptions = {
        OrpheusModel.english_3b: "Modello inglese principale (3B parametri)",
        OrpheusModel.italian_spanish_3b: "Modello italiano/spagnolo (raccomandato per italiano)",
        OrpheusModel.korean_3b: "Modello coreano specializzato",
        OrpheusModel.french_3b: "Modello francese specializzato",
        OrpheusModel.german_3b: "Modello tedesco specializzato",
        OrpheusModel.chinese_3b: "Modello cinese mandarino specializzato",
        OrpheusModel.hindi_3b: "Modello hindi specializzato"
    }
    return descriptions.get(model, "Modello sconosciuto")


# === COSTANTI ===

DEFAULT_VOICE = OrpheusVoice.tara
DEFAULT_EMOTION = OrpheusEmotion.neutral
DEFAULT_FORMAT = OrpheusFormat.mp3
DEFAULT_SPEED = 1.0
DEFAULT_TIMEOUT = 30

# Mapping per compatibilità con Kokoro-Cat
KOKORO_VOICE_MAPPING = {
    "alloy": OrpheusVoice.alex,
    "echo": OrpheusVoice.echo,
    "fable": OrpheusVoice.sarah,
    "onyx": OrpheusVoice.daniel,
    "nova": OrpheusVoice.nova,
    "shimmer": OrpheusVoice.emma
}


def map_kokoro_voice(kokoro_voice: str) -> OrpheusVoice:
    """🔄 Mappa voci Kokoro a voci Orpheus per migrazione"""
    return KOKORO_VOICE_MAPPING.get(kokoro_voice, DEFAULT_VOICE)