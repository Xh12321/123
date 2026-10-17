from Crypto.Util.number import *

with open('211111.scd', 'rb') as f:
    FLAG = f.read()
f.close()


def rotate_left(x, n, bits=32):
    n = n % bits 
    mask = (1 << bits) - 1 
    x &= mask
    return ((x << n) | (x >> (bits - n))) & mask

def rotate_right(x, n, bits=32):
    n = n % bits
    mask = (1 << bits) - 1
    x &= mask
    return ((x >> n) | (x << (bits - n))) & mask
def enc1(v, k):
    v0, v1 = v
    k0, k1, k2, k3 = k
    delta = 0x87654321
    sum = 0

    for _ in range(8):
        sum = (sum + delta) & 0xFFFFFFFF
        v0 = (v0 + ((rotate_left(v1 ,4) + k0) ^ (v1 + sum) ^ ((v1 >> 5) + k1))) & 0xFFFFFFFF
        v1 = (v1 + ((rotate_right(v0 ,4) + k2) ^ (v0 + sum) ^ ((v0 >> 5) + k3))) & 0xFFFFFFFF

    for _ in range(8):
        sum = (sum + delta) & 0xFFFFFFFF
        v0 = (v0 + ((rotate_left(v1 , 4) + k0) ^ (v1 + sum) ^ ((v1 >> 5) + k1))) & 0xFFFFFFFF
        v1 = (v1 + ((rotate_right(v0 , 4) + k2) ^ (v0 + sum) ^ ((v0 >> 5) + k3))) & 0xFFFFFFFF


    return v0, v1


def enc2(a, b, c, d):
    a = (a + b) ^ c
    b = (b - c) ^ d
    c = (c + d) ^ a
    d = (d - a) ^ b
    return a & 0xFFFFFFFF, b & 0xFFFFFFFF, c & 0xFFFFFFFF, d & 0xFFFFFFFF



def pad(data: bytes) -> bytes:
    padding_len = (24 - len(data) % 24) % 24
    return data + bytes([0]) * padding_len


FLAG=[pad(FLAG)[i:i+24] for i in range(0, len(pad(FLAG)), 24)]


with open('output.enc', 'w') as f:
    for i in FLAG:
        flag=[bytes_to_long(i[j*4:j*4+4]) for j in range(len(i)//4)]

        key = [flag[i+2] for i in range(4)]

        m1 = (flag[0], flag[1])
        e1 = enc1(m1, key)
        e2=enc2(*key)

        enc=(*e1, *e2)
        f.write(str(enc)+'\n')




