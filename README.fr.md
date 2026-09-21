# Tsumugy-Narrative

**Languages:** [English](README.md) · [日本語](README.ja.md) · [中文](README.zh.md) · [한국어](README.ko.md) · [العربية](README.ar.md) · [Español](README.es.md) · **Français (ici)** · [Русский](README.ru.md)

## Qu’est-ce que c’est

https://github.com/user-attachments/assets/82d17d1e-6d3e-4422-b317-80a751a913e5

Même vidéo comme fichier du dépôt : [demo-claude.mp4](docs/assets/demo-claude.mp4)

> Une compétence simple qui transforme un texte en histoires de grande qualité. Elle produit une Histoire : un récit, une courte explication et un marqueur de Source.

Je suis étudiant en médecine. J’avais besoin d’un moyen pour comprendre des concepts difficiles en peu de temps. J’ai essayé de dessiner des images pour les mémoriser. J’ai demandé à l’IA de dessiner ces images pour moi. Mais l’IA ne savait pas dessiner des images exactes. Alors j’ai eu une nouvelle idée : je transforme une scène qui ressemble à une image en Histoire. Cela a très bien marché. Cela m’a vraiment aidé à comprendre des concepts complexes. J’ai partagé mes histoires avec des amis. Ils m’ont dit que les statistiques en santé publique semblaient très faciles. Une simple consigne donne un résultat différent à chaque fois, alors il faut toujours préciser « Rends cela plus amusant » ou « Je ne comprends pas la métaphore ». Cette compétence inclut un script d’auto-vérification. Il vérifie chaque Histoire. Ainsi, chaque Histoire garde une grande qualité, à chaque fois.

Exemple d’entrée :

```
Bonjour à toutes et à tous. Aujourd’hui, nous terminons la série de cours de pharmacologie. L’examen de mi-semestre aura lieu la semaine prochaine. Comme d’habitude, je répondrai à vos questions au fil du cours. Vous êtes nombreux à m’avoir demandé un médicament contre la somnolence diurne. J’en voudrais un moi aussi. Les antihistaminiques de première génération traversent la barrière hémato-encéphalique, donc ils provoquent somnolence, bouche sèche et difficulté à uriner. Les médicaments de seconde génération restent pour l’essentiel hors du cerveau, donc ils apaisent les symptômes d’allergie sans la somnolence…
(Extrait. Enregistrement d’un cours de 90 minutes.)
```

<details>
<summary>Exemple de sortie :</summary>

```

## Histoire

### Les Petits Feux d’artifice du Nez

Par un calme après-midi de printemps, la « neige de pollen printanier »🌸(pollen) tomba sans bruit au fond du nez.

Au fond du nez, les « feux d’artifice du nez »🎆(éternuement) éclatèrent dans un vif crépitement, et leur son sec résonna haut dans la tête douloureuse.

Du « nez robinet qui coule »🚰(nez qui coule), l’eau goutta goutte à goutte comme des larmes, et son contact froid parvint jusqu’aux lèvres sèches.

Derrière le doux parfum des fleurs, un invisible « téléphone à ficelle qui bourdonne »📞(nerf parasympathique) vibrait sans relâche.

Puis les « briques de l’embouteillage »🧱(leucotriène) s’entassèrent haut en travers de la route du nez, et la « lanterne bouchée »🏮(nez bouché) brilla d’un rouge profond.

Ne blâme pas le nez. Seuls ceux qui connaissent l’équipe des coulisses survivent au long printemps.

## Explication

Un petit récit triste du rhume des foins : l’éternuement, le nez qui coule et le nez bouché. Les feux d’artifice représentent l’éternuement, le robinet le nez qui coule, les briques le leucotriène.

> Source : cours de pharmacologie 30:12

voice: DA (fragile-confession style)

## Histoire

### La Vieille Route Grasse et le Train à Grande Vitesse

Dans un marché bordé d’étals de médicaments, une « vieille route grasse »🛢️(antihistaminiques de première génération) s’étirait longuement dans une odeur d’huile.

La vieille route franchit sans peine le « barrage du cerveau »🚧(barrière hémato-encéphalique) et troubla jusqu’à la blanche lumière de midi.

Un voyageur s’affaissa sur le « coussin du sommeil »🛋️(somnolence) et sombra profondément, entendant au loin le vent froid.

Seule une « gourde sèche »🥤(bouche sèche) restait dans sa bouche, et un goût amer répandait lentement son inquiétude sur la langue.

Le « robinet rouillé »🔩(difficulté à uriner) refusait de tourner, et des voix grondantes emplissaient la rue.

Choisis des heures d’éveil stables plutôt qu’une somnolence au rabais. Le « billet de train à grande vitesse »🎫(antihistaminiques de seconde génération) est la vraie réponse.

## Explication

Un récit animé des antihistaminiques anciens et nouveaux. La vieille route représente la première génération, le billet la seconde, le coussin la somnolence.

> Source : cours de pharmacologie 48:52

voice: MA (crowded-street style)
```

</details>

## Démarrage rapide (1 minute)

Choisissez votre parcours. Chaque parcours prend environ une minute.

### Application Claude (sans terminal)

1. Téléchargez le paquet : [narrative-formatter.skill](dist/narrative-formatter.skill).
2. Ouvrez l’application Claude. Ouvrez le menu hamburger. Allez dans Personnaliser. Appuyez sur Ajouter.
3. Glissez-déposez le fichier. Activez l’exécution du code.
4. Posez votre question dans le chat. Donnez le matériau et le mode.

https://github.com/user-attachments/assets/e70f9b9c-9f10-4012-85fe-a42d782cffb6

Même vidéo comme fichier du dépôt : [install-claude.mp4](docs/assets/install-claude.mp4)

Si le téléversement échoue, téléchargez de nouveau le paquet. Si vous ne voyez aucune rubrique Skills, activez l’exécution du code.

### Agent de programmation (terminal)

Premier choix pour tous les agents de programmation : Npx. Npx est fourni avec Node.js. Installez-le d’abord : https://nodejs.org/

```bash
npx skills add Karimuto/tsumugy-narrative
npx skills list
```

## Utilisation

Créer une histoire ne demande qu’un seul appel à la compétence. Dans l’application Claude ou un agent de programmation comme ClaudeCode, Codex, Pi ou OpenCode. Tapez :

```
/narrative-formatter <input file>. mode: <mode (optional)>.
```

Exemple, pour écrire à côté du fichier d’entrée :

```
/narrative-formatter "pharmacology2Lect3.pdf" (or drug and drop some files). mode: serial.
```

Trois modes (par défaut, `fable`) :

- **episodic** : fidèle au texte, une histoire complète par chapitre.
- **serial** : un même protagoniste et un même monde, prolongés d’épisode en épisode. La mémoire est reprise dans le ledger.
- **fable** (par défaut) : l’impression d’abord, quitte à tolérer quelques inexactitudes pour rester mémorable.

## Comment ça marche

Six étapes. Chacune est simple. Un lecteur lycéen peut les suivre.

1. Lisez le texte difficile. Repérez les idées clés et leurs liens.
2. Construisez une petite scène. Utilisez des personnages qui agissent et ressentent.
3. Enveloppez chaque mot difficile dans une métaphore. Marquez-la avec des crochets.
4. Donnez à chaque personnage et à chaque chose un seul emoji. Utilisez le même emoji à chaque apparition.
5. Rédigez le brouillon de l’Histoire : titre, récit, courte explication, marqueur de Source.
6. Lancez le script d’auto-vérification. Il affiche PASS, CONDITIONAL PASS ou FAIL. Corrigez ce qu’il signale. Livrez uniquement un travail PASS ou CONDITIONAL PASS.

Un Thread en série garde un Ledger. Le Ledger conserve le monde et les personnages. Chaque nouvel épisode lit d’abord le Ledger.

## Contribution

Lisez [CONTRIBUTING.md](CONTRIBUTING.md) (canonique ; [日本語](CONTRIBUTING.ja.md) · [中文](CONTRIBUTING.zh.md)). Les issues et les pull requests sont bienvenues en japonais ou en anglais.

## Licence

![MIT](https://img.shields.io/badge/license-MIT-green) ![version](https://img.shields.io/badge/version-0.1.0-blue)

MIT ([LICENSE](LICENSE)).
