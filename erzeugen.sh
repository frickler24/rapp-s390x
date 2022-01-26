#!/bin/bash

# Entpacke geladenes ZIP-File

rm -rf /tmp/Einzelbriefe
unzip ~/Downloads/Einzelbriefe.zip -d /tmp/Einzelbriefe
(
    # und erzeuge die pdfs von den LaTeX-Quellen
    cd /tmp/Einzelbriefe
    for i in *.tex ; do echo -n $i... ; pdflatex $i > /dev/null; echo; done
    echo "es wurden" $(ls -1 *.pdf | wc -l) "Dateien erzeugt."
)

