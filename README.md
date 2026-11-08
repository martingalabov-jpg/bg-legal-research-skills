# bg-legal-research-skills

Скилове за AI асистенти (Perplexity, Claude и всеки инструмент с формат `SKILL.md`), които
описват **как и откъде да се търси българско право**: кой закон урежда въпроса, къде е
актуалният текст на даден член, как се намират наредби и стари редакции и как се търси и цитира
съдебна практика.

*English: Agent skills (SKILL.md) that teach an AI assistant where and how to research Bulgarian
law: a map of 397 laws and 27 codes in 20 branches with links to lex.bg, search playbooks for
legislation and for court decisions, and citation rules. Content is in Bulgarian.*

## Съдържание

| Папка | Какво е |
|---|---|
| `skills/bg-legal-research/` | **Един общ скил**: картата и двете ръководства. Най-лесен за качване |
| `skills/bg-legal-map/` | Карта по 20 отрасъла: кодекси и закони с линк към lex.bg, пътищата в АПИС, меродавният съд |
| `skills/bg-legislation-search/` | Как се намира акт, член, наредба, редакция към минала дата, законопроект и право на ЕС |
| `skills/bg-court-decisions-search/` | Кой съд е меродавен; тълкувателни решения, КС, ECLI, ЕСПЧ, Съдът на ЕС; как се цитира |
| `perplexity/SPACE_INSTRUCTIONS.md` | Инструкции за Perplexity Space |
| `data/` | Изходните данни: `lex-map.json` (актове и публикации от lex.bg) и `apis-map.json` (пътища в АПИС по отрасли) |
| `scripts/` | Скриптове за обновяване на картата от lex.bg |

Готовите `.zip` архиви за качване са в [Releases](../../releases).

## Инсталиране

**Perplexity → Skills:** Create skill → Upload a skill → качи `bg-legal-research.zip` от Releases.
Може и трите отделни архива.

**Perplexity Space:** постави `perplexity/SPACE_INSTRUCTIONS.md` в Custom instructions и качи като
файлове `SKILL.md` от трите скила и `skills/bg-legal-map/references/bg-legal-map.md`.

**Claude Code:** копирай папката на скила в `~/.claude/skills/`. Сложи или общия скил, или трите
отделни, не и двете, за да не се дублират.

## Обновяване на картата

```bash
python3 -I scripts/crawl.py data/raw.json
python3 -I scripts/classify.py data/raw.json data/lex-map.json
python3 -I scripts/build.py
```

`crawl.py` сваля списъците „Закони“ и „Кодекси“ от lex.bg и аналитичните публикации от
news.lex.bg. `classify.py` ги разпределя по отрасли. Ако даден акт не попадне в отрасъл, скриптът
го отпечатва и трябва да добавиш правило. `build.py` генерира файла с картата и архивите в `dist/`.
`scripts/lexbg.py` търси по заглавие сред законите, кодексите, наредбите и правилниците и вади
текста на конкретен член.

`apis-map.json` се поддържа ръчно. АПИС е платена система: картата съдържа само имената на
разделите като пътеводител, а не съдържание. Не обхождайте АПИС автоматично, защото рискувате
блокиране на акаунта.

## Ограничения

- Данните са от 08.11.2026. Новите закони след тази дата трябва да се проверят в lex.bg или в
  Държавен вестник.
- Всеки акт е в един отрасъл, а граничните закони са в най-близкия.
- Скиловете дават правна информация и методика за търсене, а не правен съвет.
- Проектът не е свързан с lex.bg, АПИС, Сиела или който и да е съд.
