# nopla - db setup and seed
In this directory, I put all the json files that will seed my mongodb in local development (dockerized).
Example:
```
# expressions.js
[
  {
    "text": "a beau mentir qui vient de loin",
    "link": "https://fr.wiktionary.org/wiki/a_beau_mentir_qui_vient_de_loin",
    "lang": "fr",
    "categories": [
      "adage"
    ]
  },
  {
    "text": "à bon chat, bon rat",
    "link": "https://fr.wiktionary.org/wiki/%C3%A0_bon_chat,_bon_rat",
    "lang": "fr",
    "categories": [
      "adage"
    ]
  }
]
```