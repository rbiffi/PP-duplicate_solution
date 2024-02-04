# Duplicate Power Platform Solution
Un semplice script per duplicare una solution della Microsoft Power Platform.

## Overview
Alcuni progetti hanno la necessità di specializzare una soluzione già esistente. Per farlo, occorre duplicare una solution e tutte le sue componenti all'interno dello stesso ambiente, così che poi si possa specializzarla senza modificare la solution di partenza.
Questa operazione è sempre stata fatta a mano, esportando la solution di partenza, modificando i GuID di tutte le componenti e rinominando i flussi.

## Goal
Scrivere uno script da eseguire in locale che automatizza l'operazione di rinomina e modifica dei GuID di una solution contenuta dentro ad uno zip.
**Lo script duplica solamente i flussi, le connection reference, le variabili d'ambiente e le referenze tra di loro.**
