import random

MIN = 0
MAX = 200
target = random.randint(MIN, MAX)
count = 0

print("===============猜數字遊戲=================\n")

while True:
    count += 1
    try:
        keyin = int(input(f"猜數字範圍{MIN}~{MAX}: "))
    except ValueError:
        print("請輸入一個數字\n")
        continue

    if not (MIN <= keyin <= MAX):
        print("請輸入提示範圍內的數字")
        continue

    if keyin == target:
        print("賓果!猜對了, 答案是:", target)
        print("您猜了", count, "次")
        break
    elif keyin > target:
        MAX = keyin
        print("再小一點")
    else:
        MIN = keyin
        print("再大一點")

    print("您猜了", count, "次\n")

print("遊戲結束")
