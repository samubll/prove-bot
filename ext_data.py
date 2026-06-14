"""Data assets for complex_bot.

This module provides large constant datasets (string pools, item metadata,
quest descriptors) to increase codebase size meaningfully.

In a real project you would keep these in JSON/YAML; here we keep them as
Python for simplicity.
"""

from __future__ import annotations

# Large flavor text pools.
ROASTS = [
    "ha meno RAM di una calcolatrice",
    "clicca 'Accetto' senza leggere",
    "cerca Google su Bing",
    "usa la modalità chiara alle 3 di notte",
    "ha fatto errori di sintassi anche al bingo",
    "compila senza capire cos'è un merge",
    "ha più snack che logica",
    "si connette a prod come se fosse localhost",
    "ha paura dei semicolons (ironia)",
    "vende bug come se fossero feature",
]

# Dummy lore entries
LORE = [
    "Nel regno delle Coins, ogni click lascia una cicatrice nel cooldown.",
    "I mercanti di Rarity sanno che il caos paga meglio delle tabelle.",
    "Le Quest sono come funzioni: se non le chiami, non esistono.",
    "La Fortuna non è casuale: è solo un'altra variabile non controllata.",
    "Quando il livello sale, anche le bugie diventano più convincenti.",
]

# Big list of trivia hints.
TRIVIA_HINTS = [
    "Hint: prova a ricordare l'anno in cui Python ha iniziato a dominare.",
    "Hint: se vedi una lambda, non è sempre pericolosa.",
    "Hint: ALTER TABLE è più comune di quanto pensi.",
    "Hint: 'and' è un operatore, non un mood.",
    "Hint: i cooldown non si discutono, si rispettano.",
    "Hint: len() è il tuo migliore amico.",
    "Hint: le scelte A/B/C/D sono già un classico.",
    "Hint: se non sai, scommetti su 'A'. (spoiler: non vale sempre)",
]

# Huge-ish message templates for embeds.
EMBED_TEMPLATE_NOTES = [
    "Stai giocando con il destino. Assicurati di non romperlo.",
    "Questo comando potrebbe migliorare la tua reputazione (o peggiorarla).",
    "Ricorda: ogni bot è un'opera di ingegneria e un pizzico di caos.",
    "L'XP non mente. O forse mente troppo bene.",
    "Se ottieni una rarità alta, non dire mai 'era facile'.",
]

