import os
import sys
import argparse
from lxml import etree as ET



def generate(base_dir,size:int):
    """Generate XML files and test runners for a given set size."""
    print(f"Generating XML file with {size} nodes...")
    generate_xml_file(base_dir,size)
    generate_test_runners(base_dir,size)


def generate_test_runners(base_dir,size:int):
    """Genereate test runners for given set size"""
    print(f"Generating run-test-set-{size}-files-no-zip.bat")


    with open(f"{base_dir}/run-test-set-{size}-files-no-zip.bat","w") as runner:
        runner.write("@echo off\n")
        runner.write(f"python ..\\XMLExtractor.py --test {size}  --skip-pause  --mute")
        runner.close()

    print(f"Generating run-test-set-{size}-files-zip.bat")
    with open(f"{base_dir}/run-test-set-{size}-files-zip.bat","w") as runner:
        runner.write("@echo off\n")
        runner.write(f"python ..\\XMLExtractor.py --test Y --s {size} --z test-{size}  --skip-pause  --mute ")
        runner.close()

    print(f"Generating run-test-set-{size}-files-zip-pwd.bat")
    with open(f"{base_dir}/run-test-set-{size}-files-zip-pwd-BOOM25.bat","w") as runner:
        runner.write("@echo off\n")
        runner.write(f"python ..\\XMLExtractor.py --test   {size} --z test-{size} BOOM25 --skip-pause  --mute ")
        runner.close()

    with open(f"{base_dir}/run-test-set-{size}-files-no-zip-dry-run.bat","w") as runner:
        runner.write("@echo off\n")
        runner.write(f"python ..\\XMLExtractor.py --test {size}  --skip-pause  --mute --dry-run")
        runner.close()

    print(f"Generating run-test-set-{size}-files-zip-dry-run.bat")
    with open(f"{base_dir}/run-test-set-{size}-files-zip-dry-run.bat","w") as runner:
        runner.write("@echo off\n")
        runner.write(f"python ..\\XMLExtractor.py --test {size} --z test-{size}  --skip-pause  --mute --dry-run")
        runner.close()

    print(f"Generating run-test-set-{size}-files-zip-pwd-dry-run.bat")
    with open(f"{base_dir}/run-test-set-{size}-files-zip-pwd-BOOM25-dry-run.bat","w") as runner:
        runner.write("@echo off\n")
        runner.write(f"python ..\\XMLExtractor.py --test  {size} --z test-{size} BOOM25 --skip-pause  --mute --dry-run ")
        runner.close()

def generate_xml_file( base_dir,size:int):
    """
    Generate an XML file with the specified number of nodes.

    Args:
        size (int): Number of nodes to include in the XML file.
        output_dir (str): Directory where the XML file will be saved.
    """


    # Ensure the output directory exists
    os.makedirs(f"{base_dir}/sets", exist_ok=True)

    # Create the root element
    root = ET.Element("RESULTS")

    # Add child nodes
    for i in range(size):
        node = ET.SubElement(root, "ROW")
        col=ET.SubElement(node, "COLUMN",NAME="RICH_TEXT_NCLOB")
        col.text =ET.CDATA( f"""<foo><id>Message_{i}</id>Voici un texte généré au hasard pour répondre à votre demande.
Chaque ligne contient une phrase aléatoire.
Le but est simplement de remplir l'espace avec du texte.
La génération de texte peut être utile pour tester l'affichage.
Parfois, cela sert aussi à des tests de performance.
Il est intéressant d'observer comment le texte s'affiche.
Différents systèmes réagissent différemment aux blocs de texte.
Certains logiciels gèrent mal les longs paragraphes.
D'autres les affichent de manière fluide et efficace.
Le mot "word wrap" signifie simplement retour à la ligne automatique.
Cela permet d'éviter que le texte dépasse la largeur de l'écran.
Les éditeurs de texte modernes intègrent souvent cette fonctionnalité.
Elle est particulièrement utile pour la lisibilité.
Un long paragraphe sans retour à la ligne est fatigant à lire.
D'où l'intérêt d'un bon retour à la ligne automatique.
Certains navigateurs gèrent cela mieux que d'autres.
Les différences sont notables selon les résolutions d'écran.
Cela peut également dépendre des polices utilisées.
Un bon espacement améliore également la lisibilité.
Voici encore une phrase pour allonger le texte.
La diversité des phrases évite la monotonie.
Bien que répétitif, ce texte a un but précis.
Générer 300 lignes n'est pas un problème pour une IA.
Chaque ligne est numérotée pour un suivi plus facile.
Cela permet de vérifier rapidement le nombre de lignes.
On pourrait aussi utiliser un compteur automatique.
Certains logiciels permettent d'afficher le nombre de lignes.
Notepad++, par exemple, affiche les numéros de ligne.
De nombreux éditeurs de code font de même.
Cela facilite le repérage dans un long document.
Voici encore une phrase pour continuer la liste.
Le but est d'atteindre au moins 300 lignes.
On peut varier les longueurs de phrases.
Cela donne un aspect plus naturel au texte.
On pourrait aussi insérer des paragraphes plus longs.
Mais ici, nous gardons une structure linéaire.
Cela correspond mieux à la demande initiale.
Tester les limites d'affichage est une pratique courante.
Surtout pour les développeurs et les designers.
Il est important de vérifier le comportement des interfaces.
S'assurer que tout fonctionne correctement est essentiel.
Les erreurs d'affichage peuvent nuire à l'expérience utilisateur.
Un bon design prend en compte ces aspects techniques.
Il est aussi crucial de tester sur plusieurs appareils.
Un texte bien affiché sur un PC peut mal rendre sur mobile.
Les tailles d'écran influencent grandement la lisibilité.
Les espaces et marges doivent être bien ajustés.
Un bon espacement évite une apparence encombrée.
La typographie joue également un rôle majeur.
Une police claire améliore considérablement le confort de lecture.
...
On approche bientôt de la fin de ce bloc de texte.
Encore quelques lignes pour atteindre l'objectif.
Voilà, nous avons généré un texte d'au moins 300 lignes !Voici un texte généré au hasard pour répondre à votre demande.
Chaque ligne contient une phrase aléatoire.
Le but est simplement de remplir l'espace avec du texte.
La génération de texte peut être utile pour tester l'affichage.
Parfois, cela sert aussi à des tests de performance.
Il est intéressant d'observer comment le texte s'affiche.
Différents systèmes réagissent différemment aux blocs de texte.
Certains logiciels gèrent mal les longs paragraphes.
D'autres les affichent de manière fluide et efficace.
Le mot "word wrap" signifie simplement retour à la ligne automatique.
Cela permet d'éviter que le texte dépasse la largeur de l'écran.
Les éditeurs de texte modernes intègrent souvent cette fonctionnalité.
Elle est particulièrement utile pour la lisibilité.
Un long paragraphe sans retour à la ligne est fatigant à lire.
D'où l'intérêt d'un bon retour à la ligne automatique.
Certains navigateurs gèrent cela mieux que d'autres.
Les différences sont notables selon les résolutions d'écran.
Cela peut également dépendre des polices utilisées.
Un bon espacement améliore également la lisibilité.
Voici encore une phrase pour allonger le texte.
La diversité des phrases évite la monotonie.
Bien que répétitif, ce texte a un but précis.
Générer 300 lignes n'est pas un problème pour une IA.
Chaque ligne est numérotée pour un suivi plus facile.
Cela permet de vérifier rapidement le nombre de lignes.
On pourrait aussi utiliser un compteur automatique.
Certains logiciels permettent d'afficher le nombre de lignes.
Notepad++, par exemple, affiche les numéros de ligne.
De nombreux éditeurs de code font de même.
Cela facilite le repérage dans un long document.
Voici encore une phrase pour continuer la liste.
Le but est d'atteindre au moins 300 lignes.
On peut varier les longueurs de phrases.
Cela donne un aspect plus naturel au texte.
On pourrait aussi insérer des paragraphes plus longs.
Mais ici, nous gardons une structure linéaire.
Cela correspond mieux à la demande initiale.
Tester les limites d'affichage est une pratique courante.
Surtout pour les développeurs et les designers.
Il est important de vérifier le comportement des interfaces.
S'assurer que tout fonctionne correctement est essentiel.
Les erreurs d'affichage peuvent nuire à l'expérience utilisateur.
Un bon design prend en compte ces aspects techniques.
Il est aussi crucial de tester sur plusieurs appareils.
Un texte bien affiché sur un PC peut mal rendre sur mobile.
Les tailles d'écran influencent grandement la lisibilité.
Les espaces et marges doivent être bien ajustés.
Un bon espacement évite une apparence encombrée.
La typographie joue également un rôle majeur.
Une police claire améliore considérablement le confort de lecture.
...
On approche bientôt de la fin de ce bloc de texte.
Encore quelques lignes pour atteindre l'objectif.
Voilà, nous avons généré un texte d'au moins 300 lignes !Voici un texte généré au hasard pour répondre à votre demande.
Chaque ligne contient une phrase aléatoire.
Le but est simplement de remplir l'espace avec du texte.
La génération de texte peut être utile pour tester l'affichage.
Parfois, cela sert aussi à des tests de performance.
Il est intéressant d'observer comment le texte s'affiche.
Différents systèmes réagissent différemment aux blocs de texte.
Certains logiciels gèrent mal les longs paragraphes.
D'autres les affichent de manière fluide et efficace.
Le mot "word wrap" signifie simplement retour à la ligne automatique.
Cela permet d'éviter que le texte dépasse la largeur de l'écran.
Les éditeurs de texte modernes intègrent souvent cette fonctionnalité.
Elle est particulièrement utile pour la lisibilité.
Un long paragraphe sans retour à la ligne est fatigant à lire.
D'où l'intérêt d'un bon retour à la ligne automatique.
Certains navigateurs gèrent cela mieux que d'autres.
Les différences sont notables selon les résolutions d'écran.
Cela peut également dépendre des polices utilisées.
Un bon espacement améliore également la lisibilité.
Voici encore une phrase pour allonger le texte.
La diversité des phrases évite la monotonie.
Bien que répétitif, ce texte a un but précis.
Générer 300 lignes n'est pas un problème pour une IA.
Chaque ligne est numérotée pour un suivi plus facile.
Cela permet de vérifier rapidement le nombre de lignes.
On pourrait aussi utiliser un compteur automatique.
Certains logiciels permettent d'afficher le nombre de lignes.
Notepad++, par exemple, affiche les numéros de ligne.
De nombreux éditeurs de code font de même.
Cela facilite le repérage dans un long document.
Voici encore une phrase pour continuer la liste.
Le but est d'atteindre au moins 300 lignes.
On peut varier les longueurs de phrases.
Cela donne un aspect plus naturel au texte.
On pourrait aussi insérer des paragraphes plus longs.
Mais ici, nous gardons une structure linéaire.
Cela correspond mieux à la demande initiale.
Tester les limites d'affichage est une pratique courante.
Surtout pour les développeurs et les designers.
Il est important de vérifier le comportement des interfaces.
S'assurer que tout fonctionne correctement est essentiel.
Les erreurs d'affichage peuvent nuire à l'expérience utilisateur.
Un bon design prend en compte ces aspects techniques.
Il est aussi crucial de tester sur plusieurs appareils.
Un texte bien affiché sur un PC peut mal rendre sur mobile.
Les tailles d'écran influencent grandement la lisibilité.
Les espaces et marges doivent être bien ajustés.
Un bon espacement évite une apparence encombrée.
La typographie joue également un rôle majeur.
Une police claire améliore considérablement le confort de lecture.
...
On approche bientôt de la fin de ce bloc de texte.
Encore quelques lignes pour atteindre l'objectif.
Voilà, nous avons généré un texte d'au moins 300 lignes !Voici un texte généré au hasard pour répondre à votre demande.
Chaque ligne contient une phrase aléatoire.
Le but est simplement de remplir l'espace avec du texte.
La génération de texte peut être utile pour tester l'affichage.
Parfois, cela sert aussi à des tests de performance.
Il est intéressant d'observer comment le texte s'affiche.
Différents systèmes réagissent différemment aux blocs de texte.
Certains logiciels gèrent mal les longs paragraphes.
D'autres les affichent de manière fluide et efficace.
Le mot "word wrap" signifie simplement retour à la ligne automatique.
Cela permet d'éviter que le texte dépasse la largeur de l'écran.
Les éditeurs de texte modernes intègrent souvent cette fonctionnalité.
Elle est particulièrement utile pour la lisibilité.
Un long paragraphe sans retour à la ligne est fatigant à lire.
D'où l'intérêt d'un bon retour à la ligne automatique.
Certains navigateurs gèrent cela mieux que d'autres.
Les différences sont notables selon les résolutions d'écran.
Cela peut également dépendre des polices utilisées.
Un bon espacement améliore également la lisibilité.
Voici encore une phrase pour allonger le texte.
La diversité des phrases évite la monotonie.
Bien que répétitif, ce texte a un but précis.
Générer 300 lignes n'est pas un problème pour une IA.
Chaque ligne est numérotée pour un suivi plus facile.
Cela permet de vérifier rapidement le nombre de lignes.
On pourrait aussi utiliser un compteur automatique.
Certains logiciels permettent d'afficher le nombre de lignes.
Notepad++, par exemple, affiche les numéros de ligne.
De nombreux éditeurs de code font de même.
Cela facilite le repérage dans un long document.
Voici encore une phrase pour continuer la liste.
Le but est d'atteindre au moins 300 lignes.
On peut varier les longueurs de phrases.
Cela donne un aspect plus naturel au texte.
On pourrait aussi insérer des paragraphes plus longs.
Mais ici, nous gardons une structure linéaire.
Cela correspond mieux à la demande initiale.
Tester les limites d'affichage est une pratique courante.
Surtout pour les développeurs et les designers.
Il est important de vérifier le comportement des interfaces.
S'assurer que tout fonctionne correctement est essentiel.
Les erreurs d'affichage peuvent nuire à l'expérience utilisateur.
Un bon design prend en compte ces aspects techniques.
Il est aussi crucial de tester sur plusieurs appareils.
Un texte bien affiché sur un PC peut mal rendre sur mobile.
Les tailles d'écran influencent grandement la lisibilité.
Les espaces et marges doivent être bien ajustés.
Un bon espacement évite une apparence encombrée.
La typographie joue également un rôle majeur.
Une police claire améliore considérablement le confort de lecture.
...
On approche bientôt de la fin de ce bloc de texte.
Encore quelques lignes pour atteindre l'objectif.
Voilà, nous avons généré un texte d'au moins 300 lignes !Voici un texte généré au hasard pour répondre à votre demande.
Chaque ligne contient une phrase aléatoire.
Le but est simplement de remplir l'espace avec du texte.
La génération de texte peut être utile pour tester l'affichage.
Parfois, cela sert aussi à des tests de performance.
Il est intéressant d'observer comment le texte s'affiche.
Différents systèmes réagissent différemment aux blocs de texte.
Certains logiciels gèrent mal les longs paragraphes.
D'autres les affichent de manière fluide et efficace.
Le mot "word wrap" signifie simplement retour à la ligne automatique.
Cela permet d'éviter que le texte dépasse la largeur de l'écran.
Les éditeurs de texte modernes intègrent souvent cette fonctionnalité.
Elle est particulièrement utile pour la lisibilité.
Un long paragraphe sans retour à la ligne est fatigant à lire.
D'où l'intérêt d'un bon retour à la ligne automatique.
Certains navigateurs gèrent cela mieux que d'autres.
Les différences sont notables selon les résolutions d'écran.
Cela peut également dépendre des polices utilisées.
Un bon espacement améliore également la lisibilité.
Voici encore une phrase pour allonger le texte.
La diversité des phrases évite la monotonie.
Bien que répétitif, ce texte a un but précis.
Générer 300 lignes n'est pas un problème pour une IA.
Chaque ligne est numérotée pour un suivi plus facile.
Cela permet de vérifier rapidement le nombre de lignes.
On pourrait aussi utiliser un compteur automatique.
Certains logiciels permettent d'afficher le nombre de lignes.
Notepad++, par exemple, affiche les numéros de ligne.
De nombreux éditeurs de code font de même.
Cela facilite le repérage dans un long document.
Voici encore une phrase pour continuer la liste.
Le but est d'atteindre au moins 300 lignes.
On peut varier les longueurs de phrases.
Cela donne un aspect plus naturel au texte.
On pourrait aussi insérer des paragraphes plus longs.
Mais ici, nous gardons une structure linéaire.
Cela correspond mieux à la demande initiale.
Tester les limites d'affichage est une pratique courante.
Surtout pour les développeurs et les designers.
Il est important de vérifier le comportement des interfaces.
S'assurer que tout fonctionne correctement est essentiel.
Les erreurs d'affichage peuvent nuire à l'expérience utilisateur.
Un bon design prend en compte ces aspects techniques.
Il est aussi crucial de tester sur plusieurs appareils.
Un texte bien affiché sur un PC peut mal rendre sur mobile.
Les tailles d'écran influencent grandement la lisibilité.
Les espaces et marges doivent être bien ajustés.
Un bon espacement évite une apparence encombrée.
La typographie joue également un rôle majeur.
Une police claire améliore considérablement le confort de lecture.
...
On approche bientôt de la fin de ce bloc de texte.
Encore quelques lignes pour atteindre l'objectif.
Voilà, nous avons généré un texte d'au moins 300 lignes !</foo>""")

    # Create the tree and write to file
    tree = ET.ElementTree(root)
    file_path = os.path.join(f"{base_dir}/sets", f"set_{size}.xml")
    print(f"Writing XML file to {file_path}...")

    with open(file_path, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True, pretty_print=True)


    print(f"XML file generated: {file_path}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate XML files with a specified number of nodes.")
    parser.add_argument("--size", type=int, required=True, help="Number of nodes in the XML file.")
    args = parser.parse_args()

    # Validate the size argument
    if args.size <= 0:
        print("Error: The size parameter must be a positive integer.")
        sys.exit(1)


    # Generate the XML file
    generate_xml_file(".",args.size)
    generate_test_runners(".",args.size)

if __name__ == "__main__":
    main()