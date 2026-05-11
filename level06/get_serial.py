login = "DUCKING"

v4 = (ord(login[3]) ^ 0x1337) + 6221293

for char in login:
		val = ord(char)
		v4 += (v4 ^ val) % 0x539

print(v4)