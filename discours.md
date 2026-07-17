## S01 : Titre [FR]

Bonjour à toutes et à tous, et merci d'être présents. Je suis Aniss Outaleb, étudiant en majeure SCIA à l'EPITA, et je vais vous présenter mon stage de fin d'études, réalisé chez Aubay Solutec, au sein du laboratoire d'innovation du groupe, le Lab'Innov. Pendant six mois, j'ai travaillé sur une question simple à poser et difficile à résoudre : comment rendre fiables les modèles d'IA qui décrivent des images.

## S02 : Introduction : l'IA se trompe avec aplomb [FR]

Regardez cette cuisine. Un modèle de vision-langage, un VLM, c'est-à-dire un modèle qui prend une image en entrée et produit du texte, la décrit avec un aplomb parfait : un plat bleu avec des pommes et une orange. Sauf que si vous regardez bien... ce sont des mangues et des citrons. C'est fluide, c'est convaincant, et c'est faux. C'est ça, une hallucination visuelle : un détail que rien dans l'image ne supporte, énoncé avec la même confiance qu'un fait vérifié.

Ma mission tenait en une phrase : rendre ces modèles auditables. Détecter l'hallucination, la mesurer, et la corriger, sans jamais réentraîner le modèle. C'est le fil que je vais dérouler avec vous.

## S03 : Aubay / Lab'Innov [FR]

D'abord, le contexte. Aubay est une ESN, une entreprise de services du numérique, cotée, environ neuf mille collaborateurs en Europe, six cent un virgule six millions d'euros de chiffre d'affaires en 2025. Ses clients, banques, assurances, secteur public, lui confient des systèmes critiques.

Et sur l'IA générative, ces clients butent tous sur le même obstacle, ce qu'on appelle en interne le mur de la fiabilité : des modèles impressionnants, mais imprévisibles et opaques. Le Lab'Innov, où j'ai travaillé, fait de la recherche appliquée, avec le projet Explainable Aubay Intelligence. Son pari est lucide : on ne concurrence pas les géants sur l'entraînement de modèles fondateurs. On construit des surcouches légères de supervision, qui se branchent sur l'existant. Mon stage est exactement là-dedans.

## S04 : Équipe et mission [FR]

Concrètement, nous étions cinq super stagiaires sur le projet, encadrés par deux responsables du Lab'Innov. Je suis arrivé en février sur un état de l'art large autour de l'interprétabilité mécaniste : comprendre ce qui se passe à l'intérieur des modèles.

Et à l'issue de cet état de l'art, trois sujets d'explicabilité se sont dessinés au sein de l'équipe : le biais dans les textes, les descriptions d'images, et les caractéristiques des langues. Je me suis dirigé vers le PoC dédié aux hallucinations visuelles, pour trois raisons : c'est un sujet qui m'intéressait vraiment, je l'avais déjà traité pendant l'état de l'art, et cela permettait d'équilibrer les effectifs entre les sous-groupes. En avril j'ai ajouté un détecteur d'hallucinations, le détecteur NTP, j'y reviens dans quelques minutes ; en mai nous avons lancé la plateforme NeuralScope, et en juin j'ai consolidé le tout par des benchmarks croisés. Une mission qui a évolué, donc, et c'est assumé.

## S05 : Problématique [FR]

Posons le problème proprement. Une hallucination visuelle, c'est un détail plausible mais que rien dans l'image ne supporte : un objet, une couleur, un contexte inventé. Dans l'analyse documentaire ou la vérification d'identité, c'est rédhibitoire.

La solution évidente, faire relire chaque description par un second modèle, coûte le double. Et le modèle doit rester en zero-shot : poids figés, pas de réentraînement.

D'où ma vraie question d'ingénieur : quel signal de risque peut-on extraire du modèle lui-même, et quand faut-il intervenir ?

## S06 : Démarche : de l'état de l'art à l'arbitrage [FR]

Ma démarche en trois temps. D'abord explorer large, avec l'état de l'art sur l'interprétabilité mécaniste et les hallucinations. Ensuite, prototyper en parallèle : l'équipe a monté plusieurs preuves de concept. Enfin, arbitrer : c'est le document que vous voyez, présenté en comité : pour chaque PoC, sa valeur métier, son coût, sa démontrabilité. Mon critère de convergence était simple : une méthode intégrable chez un client vaut plus qu'une méthode parfaite en laboratoire.

Un mot de méthode : [IND-1] la pastille en haut à droite des slides renvoie à la trace correspondante dans les annexes de mon dossier, pour que chaque affirmation soit vérifiable sur pièces.

## S07 : Ce que j'ai abandonné [FR]

Et la première chose que je veux vous montrer, c'est un échec. [IND-1] Notre première itération, le VLM-juge, était l'approche standard de l'industrie : un second modèle relit l'image et la description, et juge. Voici le prompt que je lui donnais : comparer l'image, le titre de référence et le brouillon, et ne renvoyer que les concepts hallucinés.

C'est ici que ma contrainte matérielle entre en jeu : tout devait tenir sur huit gigas de mémoire graphique, la RTX 2080 du poste mis à ma disposition pour mes recherches. J'ai mesuré cette approche, et je l'ai abandonnée, pour trois raisons. Deux passes complètes de génération par image : insoutenable sur ces huit gigas. Un signal quasi inexistant : la correction ne se déclenchait que dans moins d'un pour cent des cas. Et un effet plafond : changer de prompt ou de juge n'améliorait rien.

[IND-1] Savoir tuer une piste, c'est aussi de la conception. La conclusion était claire : il fallait entrer dans le modèle lui-même. Ce pivot est documenté dans le dossier, la référence est sur la slide.

## S08 : Détecter : NTP [FR]

La méthode NTP repose sur une intuition clé : si l'IA peut prédire une phrase avec certitude **même sans voir la photo**, c'est qu'elle est en train d'halluciner par pur automatisme.

Regardez ces deux exemples réels issus de nos tests.
*   **À gauche**, le cas d'ancrage réel. L'IA décrit un enfant avec un livre. Sa confiance est de **0.78** quand elle voit l'image, mais chute à **0.17** quand on lui cache. Elle a donc eu besoin de "regarder" pour être sûre.
*   **À droite**, l'hallucination. L'IA prétend que l'homme a les jambes croisées, alors que c'est faux. Notez le dépassement : sa confiance est plus élevée quand on lui cache la photo (**0.65**) que quand elle la voit (**0.58**) ! Elle est aveuglée par son propre biais statistique. 

C'est ce décalage que notre détecteur analyse pour isoler les phrases suspectes.

## S08bis : Pipeline NTP en détail [FR]

Mais comment transforme-t-on ces probabilités en une décision concrète ? C'est tout l'intérêt de notre pipeline.

Comme vous le voyez sur ce schéma, nous comparons deux flux de probabilités :
1.  **Description NTP** : C'est la confiance de l'IA quand elle regarde l'image.
2.  **Linguistic NTP** : C'est sa confiance basée uniquement sur la grammaire et ses habitudes de langage (sans l'image).

Pour chaque phrase, nous extrayons des **caractéristiques statistiques** : le nombre de mots, la moyenne de confiance, l'instabilité (l'écart-type).

Ces données nourrissent ensuite un **classifieur léger** (un *lightweight model* comme une Régression Logistique). Ce petit modèle "expert" apprend à détecter l'hallucination quand le signal linguistique prend le dessus sur le signal visuel. C'est ce qui rend notre outil extrêmement rapide, économe en ressources et facile à intégrer dans n'importe quel système existant.

## S09 : Corriger : ASD [FR]

Détecter, c'est bien ; corriger, c'est mieux. L'Activation Steering Decoding intervient dans les activations internes du modèle. En calibration, je fais générer le modèle sur des images annotées, j'étiquette chaque phrase comme factuelle ou hallucinée grâce aux objets de référence, et je contraste les activations internes des deux groupes de tokens. Cette différence me donne un vecteur de contrôle, que j'injecte dans le tiers central du décodeur, assez profond pour être abstrait, assez loin de la sortie pour ne pas casser la syntaxe.

À l'inférence, deux voies génèrent en parallèle : une voie renforcée vers la réalité, une voie poussée vers le biais. Le décodage contrastif amplifie la première et soustrait la seconde. Deux paramètres pilotent tout ça : alpha, la force du contraste, et lambda, l'intensité de l'injection. Je les ai réglés par une recherche manuelle de paramètres, une grille complète que vous trouverez en annexe du rapport.

## S10 : Pipeline filter+asd [FR]

L'architecture finale assemble les deux briques, et la logique tient en une phrase : on ne corrige que quand c'est risqué. Le VLM génère, le NTP score chaque phrase ; risque faible, on conserve tel quel ; risque élevé, l'ASD ré-ancre la phrase dans l'image. Le modèle reste en zero-shot, l'intervention est ciblée, le coût marginal quasi nul.

Voilà pour la conception. I will now switch to English for the results and the limitations of this work.

## S11 : [EN] Evaluation protocol

Does it actually work? I used three corpora, covering three different kinds of hallucination, and you can see a sample of each on screen. MSCOCO, natural scenes: the failure mode is inventing objects. LV-Hallucinations, finely labelled descriptions: colors, textures, context. And TextVQA, documents, signs and labels, where hallucinating means misreading text: the closest to Aubay's business use cases.

Detection is evaluated sentence by sentence. The headline metric is ROC-AUC: it measures how well the detector separates hallucinated sentences from correct ones. Zero point five means a coin flip; one would be a perfect separation.

## S12 : [EN] Model benchmark

[IND-6] First result: I benchmarked the detector on four different generator models, on the LV-Hallucinations test split. The task was to find a model that would both hallucinate enough and let us detect it reliably. Our first intuition was to pick small, fast models, expecting more errors in exchange for speed. It turned out the opposite: small models are trained to take no risk, they produce very short, cautious descriptions, and therefore hallucinate very little. In the end, Qwen2.5-VL-3B comes out on top on both ROC-AUC, at zero point six four five, and PR-AUC: the most reliable separation within the memory budget. It became our reference model, a choice made with numbers, not intuition.

One interesting trap here: the eight-billion-parameter model reaches a recall of zero point nine. Tempting. But it over-flags massively, and its runtime is prohibitive, for an AUC that is actually lower.

## S14 : [EN] Cross-dataset

Then I asked the question : does the detector travel across domains? [IND-1] Mostly, no, and that is the key finding of this internship. Trained on generalist images, tested on documents: zero point four eight, a coin flip. The other way around: zero point five one. But retrained inside the document domain, the same method jumps to zero point seven six five.

The probabilistic signature of a hallucination is domain-dependent: inventing a texture and misreading a word are two different failures. This is not a weakness of the method, it is a design rule: one detector per domain. And it tells us exactly where to invest next.

## S15 : [EN] Fabrication vs. context

But there is a deeper limitation: our score does not distinguish between two very different things: fabrication, and world knowledge. Here is a real case from our evaluation run: a fairground carousel. The model adds context: a popular attraction in many countries, with traditional European designs. That is world knowledge, and it is even correct: look closely, the painted panels show Venetian scenes. Yet our pipeline scores it one point zero. One hundred percent hallucination.

Why does this happen? Because our strict metric compares the generated words to a reference caption: whatever is not in the reference counts as hallucinated. World knowledge and historical context get punished just like a fabricated object would. [IND-1] And we made that choice deliberately: we push the model toward what the pixels strictly support. For compliance, that is the right bias. But for accessibility, describing an archive photo to a visually impaired user, that context is precisely the value. Same sentence, two verdicts: the definition of a hallucination itself must be part of the product conversation.

## S16 : [EN] Limits I stand behind

Let me state the limits plainly. An AUC of zero point six four five on generalist images is a moderate signal: useful for triage, not for truth. [IND-4] Each risk on this table has a concrete mitigation device, and you can read them: tunable threshold against over-flagging, keeping the safest sentences instead of deleting, retraining per domain.

[IND-1] My recommendation for the next iteration is therefore not a bigger model: it is domain-specific training, on document and accessibility corpora.

## S18 : Engagement éclairé [FR]

Ces limites posées, reste la question qu'on m'a posée en comité : qu'est-ce qu'on peut promettre à un client ? Ma réponse tient dans ce tableau, et vous pouvez le lire. [IND-3] En une phrase : c'est un outil de priorisation de la revue humaine, et c'est comme ça qu'il doit se vendre. Le jour où on le présente comme un label de vérité, on recrée exactement le problème qu'on voulait résoudre. Un engagement éclairé vaut mieux qu'une démo magique.

## S17 : Industrialiser : NeuralScope [FR]

Un résultat de recherche qui reste dans un notebook ne sert à personne. [IND-2] La deuxième moitié du stage, c'est NeuralScope : la plateforme qui unifie les trois PoC de l'équipe autour de nos trois principes : comprendre, corriger, piloter. Voici sa page d'accueil. Architecture en monolithe modulaire : une seule base déployable, mais des modules hermétiques par PoC, ce qui a permis à cinq stagiaires d'avancer sans se marcher dessus. FastAPI côté back, React TypeScript côté front, Docker pour la reproductibilité. J'étais responsable du module d'explicabilité de bout en bout.

## S17bis : NeuralScope : deux modes [FR]

Et surtout, la plateforme offre deux modes, que vous voyez à l'écran. À gauche, le mode métier : un jeu de détection d'hallucinations et des vues avant-après, pensés pour les non-techniciens. À droite, le mode développeur, pour inspecter les probabilités phrase par phrase et régler les seuils de correction. [IND-2] La valeur d'innovation est là : une surcouche légère et réutilisable, qu'un consultant Aubay peut brancher sur le modèle d'un client sans réentraînement.

## S19 : Choix responsables [FR]

Trois choix de conception que je défends comme des dispositifs concrets, pas comme un affichage. [IND-5] L'environnement d'abord : de la frugalité par conception. Des modèles de deux cent cinquante-six millions à trois milliards de paramètres, choisis par benchmark ; une correction à l'inférence qui évite le coût énergétique d'un réentraînement ; un repli automatique sur CPU et de la quantification. [IND-4] Ce sont mes dispositifs face au risque environnemental de la course aux modèles géants.

Les données ensuite : cent pour cent local, aucun appel d'API cloud, le dispositif qui neutralise le risque de fuite sur des données sensibles. La société enfin : le mode métier et le jeu pédagogique rendent le sujet accessible aux non-techniciens, et la perspective qui me tient à cœur, c'est la description d'images fiable pour les personnes malvoyantes.

[IND-5] Et j'insiste : la frugalité n'était pas une contrainte subie. J'aurais pu louer du GPU dans le cloud. J'ai choisi de faire tenir la solution sur le poste du client, c'est là qu'est la valeur.

## S20 : Produire en équipe [FR]

Un mot sur la fabrique. Nous avons travaillé dans un cadre Scrumban : des sprints d'une semaine hérités de Scrum, un flux Kanban sur Jira, du poker planning, des dailies, et nos comités hebdomadaires servaient de sprint reviews scientifiques. Le rôle de Scrum Master tournait chaque semaine. Le stage s'est conclu par la Journée des Stagiaires, où j'ai présenté NeuralScope aux collaborateurs d'Aubay, et par un article de blog interne.

Et mon axe de progrès, je l'assume devant vous : la synchronisation. Sur un travail en binôme, il m'est arrivé d'avancer trop vite seul. Les rituels agiles m'ont appris à exposer mes choix avant de les coder, c'est probablement l'apprentissage le plus durable du stage.

## S21 : Conclusion [FR]

Je conclus. Ce stage démontre trois choses. Un : il existe un signal d'incertitude gratuit dans les probabilités du modèle, exploitable par un simple classifieur. Deux : on peut détecter et corriger des hallucinations à l'inférence, sans réentraînement, sur huit gigas de mémoire. Trois : ce signal dépend du domaine, on l'a mesuré, et cela dicte les perspectives : des détecteurs spécialisés par domaine, la comparaison des trois régimes d'usage de la pipeline, et une définition de l'hallucination clarifiée usage par usage.

Ce que le stage laisse à Aubay tient dans ces trois mots-clés, et NeuralScope en est le produit concret, remis et réutilisable en mission. Ce qu'il a fait de moi, c'est un ingénieur qui défend ses choix avec des mesures, y compris quand la mesure dit « pas encore ».

## S22 : Merci / questions [FR]

Merci de votre attention, je suis ravi de répondre à vos questions.
