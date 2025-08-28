# 📦 Dipendenze Plugin Orpheus TTS

Questo documento descrive tutte le dipendenze utilizzate dal plugin Orpheus TTS per Cheshire Cat.

## 🔧 Dipendenze Core

### pydantic>=2.0.0
**Utilizzo**: Validazione e gestione delle configurazioni (✅ **Migrato a V2**)
- Utilizzato in `orpheus_settings.py` per definire i modelli di configurazione
- Utilizza `@field_validator` invece del deprecato `@validator`
- Configurazione tramite `model_config` invece di `class Config`
- Fornisce validazione automatica dei tipi e dei valori
- Gestisce gli enum per voci, emozioni, formati e modelli
- Essenziale per l'integrazione con il sistema di settings di Cheshire Cat
- **Nota**: Completamente compatibile con Pydantic V2 senza warning di deprecazione

### requests>=2.28.0
**Utilizzo**: Comunicazione HTTP con Ollama
- Utilizzato in `orpheus_engine.py` per le chiamate API a Ollama
- Gestisce le richieste POST per la generazione di token
- Implementa timeout e gestione errori per le connessioni
- Fondamentale per l'integrazione diretta con Ollama

## 🎵 Dipendenze Audio

### numpy>=1.21.0
**Utilizzo**: Elaborazione audio e generazione sinusoidale
- Utilizzato in `orpheus_engine.py` per la generazione di audio simulato
- Gestisce array audio e conversioni di tipo
- Crea forme d'onda sinusoidali per la simulazione TTS
- Converte audio in formato int16 per compatibilità WAV
- **Nota**: Opzionale con fallback a silenzio se non disponibile

### scipy>=1.7.0
**Utilizzo**: Elaborazione avanzata del segnale audio
- **Stato**: Attualmente non utilizzata nel codice
- **Scopo**: Riservata per future implementazioni di filtri audio
- Potenziale uso per effetti audio e miglioramenti qualità
- **Raccomandazione**: Può essere rimossa se non pianificata per sviluppi futuri

## 🌐 Dipendenze di Rete (Opzionali)

### aiohttp>=3.8.0
**Utilizzo**: Comunicazioni HTTP asincrone
- **Stato**: Attualmente non utilizzata nel codice
- **Scopo**: Riservata per future implementazioni asincrone
- Potenziale uso per migliorare le performance delle chiamate Ollama
- **Raccomandazione**: Può essere rimossa se non necessaria

### openai>=1.0.0
**Utilizzo**: Compatibilità API OpenAI
- **Stato**: Attualmente non utilizzata nel codice
- **Scopo**: Riservata per future integrazioni con servizi TTS cloud
- Potenziale uso per fallback o servizi alternativi
- **Raccomandazione**: Può essere rimossa se non pianificata

## 🚀 Dipendenze Future (Commentate)

### torch>=2.0.0, torchaudio>=2.0.0, transformers>=4.20.0
**Utilizzo**: Integrazione diretta con modelli SNAC
- **Stato**: Commentate nel requirements.txt
- **Scopo**: Per implementazione futura di SNAC (Symbolic Neural Audio Codec)
- Permetterebbero generazione audio reale invece di simulazione
- **Peso**: Dipendenze molto pesanti (~2GB+)
- **Raccomandazione**: Mantenere commentate fino a implementazione effettiva

## 🐱 Dipendenze Cheshire Cat

### cat.log, cat.mad_hatter.decorators
**Utilizzo**: Integrazione con framework Cheshire Cat
- Fornite automaticamente dal framework Cheshire Cat
- `cat.log`: Sistema di logging integrato
- `cat.mad_hatter.decorators.hook`: Decoratori per hook del plugin
- **Nota**: Non incluse in requirements.txt perché parte del framework

## 📚 Dipendenze Standard Python

Queste librerie sono parte della libreria standard Python e non richiedono installazione:

- `os`: Operazioni sistema operativo
- `re`: Espressioni regolari per pulizia testo
- `json`: Parsing JSON per comunicazione Ollama
- `time`: Gestione timestamp e timing
- `hashlib`: Generazione hash per cache
- `pathlib`: Gestione percorsi file
- `typing`: Type hints per migliore documentazione
- `datetime`: Gestione date e orari
- `subprocess`: Esecuzione comandi sistema per riproduzione audio
- `threading`: Gestione thread per audio asincrono
- `enum`: Definizione enumerazioni

## 🔍 Analisi Utilizzo Effettivo

### Dipendenze Essenziali (Utilizzate Attivamente)
1. **pydantic** - Configurazioni e validazione
2. **requests** - Comunicazione Ollama
3. **numpy** - Generazione audio (con fallback)

### Dipendenze Opzionali (Non Utilizzate Attualmente)
1. **scipy** - Elaborazione audio avanzata
2. **aiohttp** - HTTP asincrono
3. **openai** - API OpenAI

### Raccomandazioni

**Per Installazione Minima**:
```
pydantic>=2.0.0
requests>=2.28.0
numpy>=1.21.0
```

**Per Installazione Completa**:
```
pydantic>=2.0.0
requests>=2.28.0
numpy>=1.21.0
scipy>=1.7.0
aiohttp>=3.8.0
openai>=1.0.0
```

**Per Sviluppo Futuro con SNAC**:
```
# Aggiungere quando necessario
torch>=2.0.0
torchaudio>=2.0.0
transformers>=4.20.0
```

## 🎯 Note di Compatibilità

- **Python**: Richiede Python 3.8+
- **Cheshire Cat**: Compatibile con versioni recenti del framework
- **Ollama**: Richiede Ollama in esecuzione per funzionalità complete
- **Sistema Operativo**: Compatibile Windows/Linux/macOS
- **Audio**: Riproduzione audio dipende dal sistema operativo (PowerShell su Windows, aplay/paplay su Linux)

## 🔧 Installazione Consigliata

```bash
# Installazione base (sufficiente per la maggior parte degli usi)
pip install pydantic>=2.0.0 requests>=2.28.0 numpy>=1.21.0

# Installazione completa (include dipendenze future)
pip install -r requirements.txt
```