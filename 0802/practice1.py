# 學生成績管理系統範例
# 涵蓋：list、dict、function、class、條件判斷、迴圈、例外處理

# ── 1. 資料定義 ──────────────────────────────────────────────
students_data = [
    {"name": "小明", "scores": {"國文": 85, "數學": 92, "英文": 78, "自然": 88}},
    {"name": "小華", "scores": {"國文": 70, "數學": 65, "英文": 90, "自然": 72}},
    {"name": "小美", "scores": {"國文": 95, "數學": 88, "英文": 94, "自然": 91}},
    {"name": "小強", "scores": {"國文": 60, "數學": 55, "英文": 62, "自然": 58}},
    {"name": "小芳", "scores": {"國文": 78, "數學": 80, "英文": 75, "自然": 82}},
]


# ── 2. 計算函式 ──────────────────────────────────────────────
def calculate_average(scores: dict) -> float:
    """計算各科平均分數"""
    return sum(scores.values()) / len(scores)


def get_grade(average: float) -> str:
    """根據平均分數回傳等第"""
    if average >= 90:
        return "A（優秀）"
    elif average >= 80:
        return "B（良好）"
    elif average >= 70:
        return "C（普通）"
    elif average >= 60:
        return "D（待加強）"
    else:
        return "F（不及格）"


def find_best_subject(scores: dict) -> tuple:
    """找出最高分的科目"""
    best = max(scores, key=scores.get)
    return best, scores[best]


def find_worst_subject(scores: dict) -> tuple:
    """找出最低分的科目"""
    worst = min(scores, key=scores.get)
    return worst, scores[worst]


# ── 3. 學生類別 ──────────────────────────────────────────────
class Student:
    def __init__(self, name: str, scores: dict):
        self.name = name
        self.scores = scores
        self.average = calculate_average(scores)
        self.grade = get_grade(self.average)

    def report(self):
        """印出個人成績單"""
        print(f"\n{'='*40}")
        print(f"  學生姓名：{self.name}")
        print(f"{'='*40}")
        for subject, score in self.scores.items():
            bar = "█" * (score // 10) + "░" * (10 - score // 10)
            print(f"  {subject:4s}：{score:3d} 分  [{bar}]")
        print(f"{'─'*40}")
        print(f"  平均分數：{self.average:.1f} 分")
        print(f"  等　　第：{self.grade}")
        best, best_score = find_best_subject(self.scores)
        worst, worst_score = find_worst_subject(self.scores)
        print(f"  最強科目：{best}（{best_score} 分）")
        print(f"  最弱科目：{worst}（{worst_score} 分）")


# ── 4. 班級統計 ──────────────────────────────────────────────
def class_statistics(students: list):
    """計算全班各科統計資料"""
    print(f"\n{'='*40}")
    print("  全班成績統計")
    print(f"{'='*40}")

    subjects = list(students[0].scores.keys())
    for subject in subjects:
        all_scores = [s.scores[subject] for s in students]
        avg = sum(all_scores) / len(all_scores)
        highest = max(all_scores)
        lowest = min(all_scores)
        print(f"  {subject:4s} → 平均:{avg:.1f}  最高:{highest}  最低:{lowest}")

    averages = [s.average for s in students]
    print(f"{'─'*40}")
    print(f"  全班平均：{sum(averages)/len(averages):.1f} 分")

    # 排名
    ranked = sorted(students, key=lambda s: s.average, reverse=True)
    print(f"\n  班級排名：")
    for rank, s in enumerate(ranked, start=1):
        print(f"    第 {rank} 名：{s.name}（{s.average:.1f} 分，{s.grade}）")


# ── 5. 查詢功能 ──────────────────────────────────────────────
def search_student(students: list, name: str):
    """依姓名查詢學生"""
    result = next((s for s in students if s.name == name), None)
    if result:
        result.report()
    else:
        print(f"\n  找不到學生「{name}」，請確認姓名是否正確。")


# ── 6. 主程式 ────────────────────────────────────────────────
if __name__ == "__main__":
    # 建立學生物件
    students = [Student(d["name"], d["scores"]) for d in students_data]

    # 印出每位學生成績單
    print("\n【個人成績單】")
    for student in students:
        student.report()

    # 全班統計
    print("\n【班級統計】")
    class_statistics(students)

    # 查詢示範
    print("\n【查詢示範】")
    search_student(students, "小美")
    search_student(students, "小龍")  # 不存在的學生
