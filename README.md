# Plugin Orpheus TTS per Cheshire Cat

## Panoramica

Il plugin Orpheus TTS integra la sintesi vocale avanzata nel framework Cheshire Cat AI, utilizzando l'integrazione diretta con Ollama per la generazione di token personalizzati e la conversione in audio.

## Caratteristiche Principali

- **Integrazione Diretta Ollama**: Utilizza Ollama per la generazione di token personalizzati senza dipendenze FastAPI
- **Sintesi Vocale Avanzata**: Supporto per diverse voci, emozioni e modalità di sintesi
- **Cache Intelligente**: Sistema di cache per ottimizzare le performance e ridurre i tempi di risposta
- **Configurazione Flessibile**: Impostazioni complete tramite l'interfaccia admin del Cheshire Cat
- **Logging Integrato**: Utilizza il sistema di logging nativo del Cheshire Cat

## Struttura del Plugin

```
app/Orpheus/
├── orpheus_cat.py          # Integrazione principale con Cheshire Cat
├── orpheus_engine.py       # Motore di sintesi vocale Orpheus
├── orpheus_settings.py     # Configurazioni e impostazioni
├── test_orpheus.py         # Test del plugin
├── plugin.json             # Metadati del plugin
├── README.md               # Questa documentazione
└── CHESHIRE_CAT_GUIDE.md   # Guida completa al framework Cheshire Cat
```

## Installazione

### Prerequisiti

1. **Cheshire Cat AI** in esecuzione
2. **Ollama** installato e configurato
3. **Python 3.8+** con le dipendenze necessarie

### Dipendenze Python

```bash
pip install requests numpy pydantic
```

### Installazione del Plugin

1. Copia la cartella `Orpheus` nella directory `plugins` del tuo Cheshire Cat:
   ```bash
   cp -r app/Orpheus /path/to/cheshire-cat/plugins/
   ```

2. Riavvia il Cheshire Cat o ricarica i plugin dall'interfaccia admin

3. Attiva il plugin dall'interfaccia admin (`localhost:1865/admin`)

## Configurazione

### Impostazioni del Plugin

Accedi all'interfaccia admin del Cheshire Cat e configura le seguenti impostazioni:

#### Configurazione Ollama
- **Ollama Host**: URL del server Ollama (default: `http://localhost:11434`)
- **Ollama Model**: Modello Orpheus da utilizzare (default: `italian_spanish_3b`)
- **Ollama Timeout**: Timeout per le richieste (default: 30 secondi)

##### Modelli Orpheus Disponibili
Il plugin supporta diversi modelli Orpheus specializzati per lingue diverse:

- **`italian_spanish_3b`** (raccomandato per italiano): `hf.co/lex-au/Orpheus-3b-Italian_Spanish-FT-Q8_0.gguf:Q8_0`
- **`english_3b`** (modello principale): `hf.co/unsloth/orpheus-3b-0.1-ft-GGUF:Q8_0`
- **`korean_3b`**: `hf.co/lex-au/Orpheus-3b-Korean-FT-Q8_0.gguf:Q8_0`
- **`french_3b`**: `hf.co/lex-au/Orpheus-3b-French-FT-Q8_0.gguf:Q8_0`
- **`german_3b`**: `hf.co/lex-au/Orpheus-3b-German-FT-Q8_0.gguf:Q8_0`
- **`chinese_3b`**: `hf.co/lex-au/Orpheus-3b-Chinese-FT-Q8_0.gguf:Q8_0`
- **`hindi_3b`**: `hf.co/lex-au/Orpheus-3b-Hindi-FT-Q8_0.gguf:Q8_0`

Per installare un modello in Ollama:
```bash
ollama run hf.co/lex-au/Orpheus-3b-Italian_Spanish-FT-Q8_0.gguf:Q8_0
```

#### Configurazione Orpheus
- **Voice**: Voce da utilizzare (`male`, `female`, `child`, `elderly`)
- **Emotion**: Emozione da applicare (`neutral`, `happy`, `sad`, `angry`, `excited`, `calm`)
- **Mode**: Modalità di sintesi (`fast`, `quality`, `balanced`)
- **Speed**: Velocità di riproduzione (0.5 - 2.0)
- **Pitch**: Tonalità della voce (-1.0 - 1.0)
- **Volume**: Volume audio (0.0 - 1.0)

#### Configurazione Cache
- **Cache Enabled**: Abilita/disabilita la cache
- **Cache Directory**: Directory per i file cache
- **Cache Max Size**: Dimensione massima della cache in MB
- **Cache TTL**: Tempo di vita della cache in ore

#### Configurazione Audio
- **Audio Format**: Formato audio (`wav`, `mp3`, `ogg`)
- **Sample Rate**: Frequenza di campionamento (default: 22050)
- **Audio Directory**: Directory per i file audio generati

## Utilizzo

### Attivazione Automatica

Una volta installato e configurato, il plugin si attiva automaticamente per ogni messaggio del Cat. Il sistema:

1. Intercetta i messaggi in uscita tramite l'hook `before_cat_sends_message`
2. Genera l'audio utilizzando il motore Orpheus
3. Salva il file audio nella directory configurata
4. Riproduce l'audio (se configurato)

### Utilizzo Programmatico

```python
from cat.mad_hatter.decorators import hook

@hook
def my_custom_hook(message, cat):
    # Accesso al motore Orpheus
    orpheus = cat.mad_hatter.get_plugin_settings('Orpheus')
    
    # Generazione audio personalizzata
    audio_file = orpheus.generate_speech(
        text="Testo da sintetizzare",
        voice="female",
        emotion="happy"
    )
    
    return message
```

## API del Plugin

### OrpheusEngine

Classe principale per la sintesi vocale:

```python
from orpheus_engine import OrpheusEngine

# Inizializzazione
engine = OrpheusEngine(settings)

# Generazione audio
audio_file = engine.generate_speech(
    text="Ciao, sono il Cheshire Cat!",
    voice="female",
    emotion="happy"
)

# Statistiche
stats = engine.get_stats()
print(f"Audio generati: {stats['total_generated']}")

# Pulizia cache
engine.cleanup_cache()
```

### Hooks Disponibili

#### `before_cat_sends_message`
Intercetta e processa i messaggi prima dell'invio:

```python
@hook
def before_cat_sends_message(final_output, cat):
    # Il plugin genera automaticamente l'audio
    # per il contenuto di final_output.content
    return final_output
```

#### `on_plugin_settings_load`
Gestisce il caricamento delle impostazioni:

```python
@hook
def on_plugin_settings_load(settings, cat):
    # Inizializzazione del motore Orpheus
    return settings
```

## Testing

### Test Standalone

```bash
cd app/Orpheus
python test_orpheus.py
```

**Nota**: I test standalone non possono utilizzare il sistema di logging del Cat. Utilizzare solo per test delle funzionalità core.

### Test con Cheshire Cat

1. Avvia il Cheshire Cat
2. Attiva il plugin dall'interfaccia admin
3. Invia un messaggio nella chat
4. Verifica la generazione dell'audio

## Troubleshooting

### Problemi Comuni

#### Plugin non si attiva
- Verifica che il file `plugin.json` sia presente
- Controlla i log del Cheshire Cat per errori di importazione
- Assicurati che tutte le dipendenze siano installate

#### Errori di connessione Ollama
- Verifica che Ollama sia in esecuzione
- Controlla l'URL di connessione nelle impostazioni
- Verifica che il modello specificato sia disponibile

#### Audio non generato
- Controlla le impostazioni della directory audio
- Verifica i permessi di scrittura
- Controlla i log per errori specifici

#### Cache non funzionante
- Verifica le impostazioni della directory cache
- Controlla i permessi di lettura/scrittura
- Verifica lo spazio disco disponibile

### Log e Debug

Il plugin utilizza il sistema di logging integrato del Cheshire Cat. Per abilitare il debug:

1. Imposta `CCAT_LOG_LEVEL=DEBUG` nelle variabili d'ambiente
2. Riavvia il Cheshire Cat
3. Monitora i log per informazioni dettagliate

## Sviluppo e Contributi

### Struttura del Codice

- **orpheus_cat.py**: Logica di integrazione con Cheshire Cat
- **orpheus_engine.py**: Motore di sintesi vocale core
- **orpheus_settings.py**: Modelli di configurazione Pydantic

### Estensioni Future

- Supporto per modelli TTS aggiuntivi
- Integrazione con servizi cloud TTS
- Supporto per lingue multiple
- Effetti audio avanzati
- Interfaccia web per configurazione avanzata

### Contribuire

1. Fork del repository
2. Crea un branch per la tua feature
3. Implementa le modifiche
4. Aggiungi test appropriati
5. Invia una pull request

## Licenza

Questo plugin è rilasciato sotto licenza GPL3, in conformità con il framework Cheshire Cat.

## Supporto

Per supporto e discussioni:
- **Discord Community**: Cheshire Cat AI Discord
- **Documentazione**: [Cheshire Cat Docs](https://cheshire-cat-ai.github.io/docs/)
- **Issues**: Repository GitHub del progetto

## 🎵 Voci Disponibili

| Voce | Tipo | Caratteristiche |
|------|------|----------------|
| tara | Femminile | Espressiva, versatile |
| alex | Maschile | Professionale, chiara |
| sarah | Femminile | Dolce, calda |
| emma | Femminile | Giovane, energica |
| daniel | Maschile | Seria, autorevole |
| michael | Maschile | Profonda, sicura |
| nova | Femminile | Moderna, tecnologica |
| echo | Speciale | Effetti unici |

## 😊 Emozioni Supportate

- **Neutral**: Tono neutro, standard
- **Happy**: Allegro, positivo
- **Sad**: Triste, malinconico
- **Angry**: Arrabbiato, intenso
- **Excited**: Eccitato, entusiasta
- **Calm**: Calmo, rilassato
- **Mysterious**: Misterioso, intrigante

## 🔧 Sviluppo

### Struttura Modulare
- **orpheus_settings.py**: Gestione configurazioni con Pydantic
- **orpheus_engine.py**: Logica TTS e integrazione Orpheus
- **orpheus_cat.py**: Hook e integrazione Cheshire Cat

### Testing
```bash
# Test configurazioni
python -m pytest tests/test_settings.py

# Test engine
python -m pytest tests/test_engine.py

# Test integrazione
python -m pytest tests/test_integration.py
```

## 📝 Changelog

### v1.0.0 - Versione Iniziale
- ✅ Architettura modulare implementata
- ✅ 8 voci multiple supportate
- ✅ 7 emozioni integrate
- ✅ Doppia modalità Ollama/FastAPI
- ✅ Integrazione completa Cheshire Cat

## 🤝 Contributi

Contributi benvenuti! Apri una issue o pull request per miglioramenti.

## 📄 Licenza

MIT License - Vedi LICENSE file per dettagli.

---

*Sostituisce Kokoro-Cat con architettura superiore e qualità audio avanzata* 🎭✨
