import random

def get_number(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("請輸入一個整數\n")

def choose_difficulty():
    print("\n請選擇難度:")
    print("1. 簡單 (1~50)")
    print("2. 普通 (1~100)")
    print("3. 困難 (1~500)")
    choice = get_number("請輸入選項 (1/2/3): ")
    if choice == 1:
        return 1, 50
    elif choice == 3:
        return 1, 500
    return 1, 100

def play_once():
    low, high = choose_difficulty()
    target = random.randint(low, high)
    count = 0
    print(f"\n===============猜數字遊戲 ({low}~{high}) =================\n")

    while True:
        count += 1
        guess = get_number(f"猜數字範圍{low}~{high}: ")

        if not (low <= guess <= high):
            print("請輸入提示範圍內的數字\n")
            continue

        if guess == target:
            print(f"賓果!猜對了, 答案是: {target}")
            print(f"您猜了 {count} 次\n")
            return count
        elif guess > target:
            high = guess - 1
            print("再小一點")
        else:
            low = guess + 1
            print("再大一點")
        print(f"您猜了 {count} 次\n")

def main():
    best_score = None
    while True:
        moves = play_once()
        if best_score is None or moves < best_score:
            best_score = moves
            print(f"🎉 新紀錄! 最少 {best_score} 次猜中")
        else:
            print(f"目前最佳紀錄: {best_score} 次")

        again = input("再玩一次? (y/n): ").strip().lower()
        if again != "y":
            break
    print("遊戲結束, 期待下次再戰!")

if __name__ == "__main__":
    main()
