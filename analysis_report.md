# Report di Analisi: Verifica Estrazione Dati e Compatibilità Strutturale

## 1. Verifica Accuratezza Estrazione Dati (`creator_output.json` vs Immagini)

È stata effettuata un'analisi dettagliata confrontando i dati estratti nel file `creator_output.json` con le immagini originali presenti nella cartella `extracted_images` per le scuole principali.

### Risultati Verifica Scuole

| Scuola | Stato | Dettagli Verifica |
| :--- | :--- | :--- |
| **Expanish** | ✅ **Corretto** | I dati estratti corrispondono perfettamente all'immagine (`...Expanish...page_2.jpg`). La logica "sliding scale" (prezzi che scendono all'aumentare delle settimane) è stata catturata correttamente (es. 240€ per 1-11 sett, 216€ per 12-21 sett). |
| **St. Giles** | ❌ **Errore Significativo** | Sono state riscontrate discrepanze critiche rispetto all'immagine (`...St. Giles...page_8.jpg`):<br>1. **Prezzo Errato:** Il JSON riporta £537, mentre l'immagine indica £520 per il corso Intensive.<br>2. **Struttura Mancante:** Il JSON ha estratto solo la prima fascia di prezzo (1-3 settimane). L'immagine mostra chiaramente fasce successive con prezzi ridotti (es. £470 per 4-7 sett, £353 per 24+ sett) che sono state ignorate. |
| **ILSC** | ⚠️ **Probabile Errore** | Il prezzo estratto ($340 CAD) sembra riferirsi alla tariffa "Afternoon" o "Part-Time", che è l'opzione più economica. L'immagine mostra che la tariffa standard "Full-Time Morning" o "Intensive" è generalmente più alta (intorno ai $440-$480). L'estrazione non ha distinto chiaramente tra le varianti orarie. |
| **GLS** | ⚠️ **Parzialmente Corretto** | L'estrazione ha catturato correttamente le prime due fasce (1-9 sett a 200€, 10+ sett a 170€). Tuttavia, ha **mancato la terza fascia** visibile nell'immagine (`...GLS...page_2.jpg`) che prevede un prezzo di 140€ per 20+ settimane. Il JSON chiude la fascia 10+ con `null`, estendendo erroneamente il prezzo di 170€ all'infinito. |

### Conclusioni sull'Estrazione
L'attuale logica di estrazione non è affidabile. Mentre funziona bene per strutture tabellari semplici (Expanish), fallisce nel catturare correttamente strutture più complesse o sfumate (St. Giles, GLS) e può selezionare varianti di corso errate (ILSC). Data la presenza di errori critici in 3 delle 4 scuole principali verificate, l'intero dataset deve essere considerato non valido per l'importazione diretta senza correzioni.

---

## 2. Verifica Compatibilità con `Listino costi.json`

È stata analizzata la struttura del file di output (`creator_output.json`) rispetto al file di destinazione (`Listino costi.json`).

### Incompatibilità Strutturale

I due file **NON sono compatibili** nel loro stato attuale.

*   **`creator_output.json` (Attuale):** Struttura **Gerarchica**.
    *   Ogni oggetto rappresenta una "Scuola" o "Location".
    *   All'interno di ogni scuola c'è una lista annidata `costs` che contiene i corsi e gli alloggi.
    *   Esempio: `[ { "school_profile": {...}, "costs": [...] }, ... ]`

*   **`Listino costi.json` (Destinazione):** Struttura **Piatta (Flat)**.
    *   È una singola lista di oggetti, dove ogni oggetto rappresenta una riga di costo indipendente.
    *   I dati della scuola (ID, nome) sono ripetuti in ogni oggetto di costo.
    *   Esempio: `[ { "school_id": "...", "cost_name": "...", "price": ... }, { "school_id": "...", ... } ]`

### Compatibilità dei Campi (Mapping)

Nonostante la differenza strutturale, i dati necessari sono presenti. È possibile trasformare `creator_output.json` per adattarlo a `Listino costi.json` tramite uno script di appiattimento (flattening).

Esempio di mapping necessario:

| Campo `creator_output.json` | Campo Target `Listino costi.json` | Note |
| :--- | :--- | :--- |
| `school_profile.school_id` | `id_scuola` | ID univoco della scuola. |
| `costs[i].category` | `Categoria` | "Corso", "Alloggio", etc. |
| `costs[i].name_ref` + `variant_ref` | `Nome_costo_listino` | Concatenazione necessaria per unicità. |
| `costs[i].gross_amount` | `Costo_lordo_listino` | Valore numerico. |
| `costs[i].week_range_start` | `Validit_settimane_da` | Inizio range validità. |
| `costs[i].week_range_end` | `Validit_settimane_a` | Fine range validità. |

### Raccomandazione
Per rendere i dati compatibili, è necessario eseguire un passaggio di post-elaborazione che:
1.  Iteri su ogni scuola in `creator_output.json`.
2.  Per ogni elemento nell'array `costs`, crei un nuovo oggetto piatto.
3.  Copi i dati della scuola (ID, Anno) in ogni nuovo oggetto costo.
4.  Esporti la lista piatta risultante nel formato richiesto da `Listino costi.json`.
