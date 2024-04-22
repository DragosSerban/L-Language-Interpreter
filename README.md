Interpreter pentru limbajul funcțional L

Acest proiect reprezintă un interpretor pentru un limbaj de programare funcțional simplificat,
care împrumută anumite concepte din Lisp. Interpretorul poate analiza și executa codul scris în acest limbaj,
oferind suport pentru expresii regulate, operatori funcționali și controlul fluxului.

Structura codului

Parserul: Implementează analiza sintactică și semantică a expresiilor din codul sursă.
Parserul transformă textul codului într-o structură de date pe care interpretorul o poate utiliza pentru execuție.
Transformarea expresiilor regulate în automate finite nedeterministe (NFA): Un modul responsabil de convertirea expresiilor regulate în NFA-uri.
Acest lucru se realizează prin aplicarea algoritmilor adecvați pentru generarea automatelor finite.
Construcția automatelor finite deterministe (DFA): Modulele responsabile de construcția automatelor finite deterministe din NFA-uri generate de expresiile regulate.
Acest proces de optimizare permite interpretorului să analizeze lexical codul sursă mai eficient.
Lexerul: Implementează analiza lexicală a codului sursă, transformând cuvintele din cod în token-uri.
Acest modul utilizează automatul finit determinist pentru a identifica și clasifica componentele individuale ale programului.
Interpretorul: Execută codul sursă, interpretând expresiile și efectuând operațiile specificate de utilizator.
Acest modul utilizează structura de date generată de parser pentru a evalua și a executa instrucțiunile.

Analiza sintactică și semantică: Parserul analizează codul sursă și verifică dacă acesta respectă regulile limbajului.
Dacă există erori sintactice sau semantice, se afișează mesaje corespunzătoare.
Transformarea expresiilor regulate: Expresiile regulate din codul sursă sunt transformate în NFA-uri, care reprezintă automatul finit nedeterminist corespunzător.
Construcția automatelor finite deterministe: NFA-urile generate sunt convertite în DFA-uri utilizând algoritmul construcției subsetului.
Acest lucru permite interpretorului să optimizeze analiza lexicală.
Analiza lexicală: Lexerul utilizează DFA-ul generat pentru a împărți cuvintele din codul sursă în token-uri.
Fiecare token reprezintă o componentă individuală a programului, cum ar fi un identificator, un operator sau o constantă.
Interpretarea și execuția: Interpretorul primește token-urile de la lexer și le evaluează pentru a determina acțiunea corespunzătoare.
Acesta execută instrucțiunile din codul sursă și afișează rezultatele sau mesajele de eroare în funcție de necesități.
