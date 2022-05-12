# NetworkProject
# Traccia 2: Architettura client-server UDP per trasferimento file
Lo scopo de progetto è quello di progettare ed implementare in linguaggio Python un’applicazione client-server per il
trasferimento di file che impieghi il servizio di rete senza connessione (socket tipo SOCK_DGRAM, ovvero UDP come
protocollo di strato di trasporto).
# Il software deve permettere:
• Connessione client-server senza autenticazione

• La visualizzazione sul client dei file disponibili sul server

• Il download di un file dal server

• L’upload di un file sul server

# La comunicazione tra client e server deve avvenire tramite un opportuno protocollo. Il protocollo di comunicazione
deve prevedere lo scambio di due tipi di messaggi:
• messaggi di comando: vengono inviati dal client al server per richiedere l’esecuzione delle diverse operazioni

• messaggi di risposta: vengono inviati dal server al client in risposta ad un comando con l’esito dell’operazione.

# Funzionalità del server: Il server deve fornire le seguenti funzionalità:
• L’invio del messaggio di risposta al comando list al client richiedente

• il messaggio di risposta contiene la file list, ovvero la lista dei nomi dei file disponibili per la condivisione

• L’invio del messaggio di risposta al comando get contenente il file richiesto, se presente, od un opportuno

messaggio di errore;
• La ricezione di un messaggio put contenente il file da caricare sul server e l’invio di un messaggio di risposta con
l’esito dell’operazione.

# Funzionalità del client: I client deve fornire le seguenti funzionalità:
• L’invio del messaggio list per richiedere la lista dei nomi dei file disponibili

• L’invio del messaggio get per ottenere un file

• La ricezione di un file richiesta tramite il messaggio di get o la gestione dell’eventuale errore

• L’invio del messaggio put per effettuare l’upload di un file sul server e la ricezione del messaggio di risposta con
l’esito dell’operazione.
