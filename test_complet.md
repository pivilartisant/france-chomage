# 🧪 Test du système complet

## 1. Test des scrapers

### Communication :
```bash
python flemme_communication.py
```
- Vérifiez que `jobs_communication.json` est créé
- Regardez le contenu (nombre d'offres)

### Design :
```bash
python flemme_design.py
```
- Vérifiez que `jobs_design.json` est créé
- Regardez le contenu

## 2. Test des bots Telegram

### Bot communication (topic 3) :
```bash
python bot_communication.py
```
- Les offres de comm apparaissent dans le topic 3

### Bot design (topic 40) :
```bash
python bot_design.py
```
- Les offres de design apparaissent dans le topic 40

## 3. Test du workflow complet manuel

```bash
# Workflow communication
python flemme_communication.py && python bot_communication.py

# Workflow design  
python flemme_design.py && python bot_design.py
```

## 4. Test du scheduler (automatique)

```bash
python scheduler.py
```
- Laissez tourner quelques minutes
- Vérifiez les logs dans la console

## 5. Vérifications

- [ ] Les 2 fichiers JSON sont créés
- [ ] Les messages apparaissent dans les bons topics
- [ ] Format des messages correct (émojis, liens, hashtags)
- [ ] Pas d'erreurs dans la console
- [ ] Rate limiting respecté (2 sec entre messages)

## 🐛 Si ça marche pas

1. **Erreur token** : Vérifiez le `.env`
2. **Pas d'offres** : Changez les termes de recherche
3. **Erreur topic** : Vérifiez que le bot est admin du groupe
4. **Import errors** : `pip install -r requirements.txt`

## 💡 Test rapide (tout en un)

```bash
# Récupère les offres des 2 domaines et les envoie
python flemme_communication.py && python flemme_design.py && python bot_communication.py && python bot_design.py
```

Voilà, c'est tout ! Si ça marche, lancez `python scheduler.py` et c'est parti pour l'automatisation.
