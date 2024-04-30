import random

a = []

for _ in range(0, 100):
    random_int = random.randint(0, 2000)
    if random_int not in a:
        a.append(random_int)

print(len(a))