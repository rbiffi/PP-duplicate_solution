# Duplicate Power Platform Solution
Un semplice script da linea di comando per duplicare una solution della Microsoft Power Platform.

## Overview
Alcuni progetti hanno la necessità di specializzare una soluzione già esistente. Per farlo, occorre duplicare una solution e tutte le sue componenti all'interno dello stesso ambiente, così che poi si possa specializzarla senza modificare la solution di partenza.  
Questa operazione è sempre stata fatta a mano, esportando la solution di partenza, modificando i GuID di tutte le componenti e rinominando i flussi.

## Goal
Script da eseguire da linea di comando che automatizza l'operazione di rinomina e modifica dei GUID delle componenti di una solution contenuta dentro ad uno zip.  
Lo script prende in **input** due parametri:
1. il path dello zip contenente la solution (obbligatorio)
2. un'opzione richiamabile con -rw, che vuole una lista separata da virgola di coppie di parole da sostituire. Le coppie di parole hanno come sintassi "old|new" (facoltativo)

Lo script restituisce in **output**:
- uno zip contenente la solution duplicata. Viene creata all'interno della cartella che conteneva la solution di partenza.

## Limiti
- lo script è stato testato solo per la duplicazione di flow, connection references e variabili d'ambiente
- è consigliato inserire sempre una coppia di parole da sostituire all'interno della solution
- la coppia di parole non devono contenere spazi o caratteri speciali

## Esempio d'uso
> $ ./duplicate_solution.exe ./Solution_1_0_0_5.zip -rw "Madrid|Amsterdam,First|Second"

Per leggere il manuale:
> $ ./duplicate_solution.exe -h
