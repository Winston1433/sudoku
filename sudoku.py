import copy
import random

SIZE = 9
BOX = 3


# ---------------------------------------------------------------------------
# 基本邏輯：合法性檢查
# ---------------------------------------------------------------------------

def is_valid(board, row, col, num):
    """檢查在 board[row][col] 填入 num 是否符合數獨規則"""
    # 檢查同一列、同一欄
    for i in range(SIZE):
        if board[row][i] == num or board[i][col] == num:
            return False

    # 檢查所屬的 3x3 小九宮格
    box_row, box_col = (row // BOX) * BOX, (col // BOX) * BOX
    for r in range(box_row, box_row + BOX):
        for c in range(box_col, box_col + BOX):
            if board[r][c] == num:
                return False

    return True


def find_empty(board):
    """找出下一個空格 (值為 0)，回傳 (row, col)；找不到就回傳 None"""
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                return r, c
    return None


# ---------------------------------------------------------------------------
# 解題器（backtracking），同時用於「產生完整解答」與「解答目前盤面」
# ---------------------------------------------------------------------------

def solve(board, randomize=False):
    """
    使用回溯法解數獨。
    randomize=True 時每次候選數字順序隨機，用來產生隨機的完整解答。
    """
    empty = find_empty(board)
    if not empty:
        return True  # 全部填滿，成功

    row, col = empty
    nums = list(range(1, 10))
    if randomize:
        random.shuffle(nums)

    for num in nums:
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve(board, randomize):
                return True
            board[row][col] = 0  # 回溯

    return False


def count_solutions(board, limit=2):
    """計算盤面解的數量，數到 limit 就提早停止（用來檢查唯一解）"""
    empty = find_empty(board)
    if not empty:
        return 1

    row, col = empty
    count = 0
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            count += count_solutions(board, limit)
            board[row][col] = 0
            if count >= limit:
                break
    return count


# ---------------------------------------------------------------------------
# 產生題目
# ---------------------------------------------------------------------------

def generate_full_board():
    """產生一個隨機且完整的合法數獨解答"""
    board = [[0] * SIZE for _ in range(SIZE)]
    solve(board, randomize=True)
    return board


DIFFICULTY_HOLES = {
    "1": ("簡單", 35),   # 挖掉的格數
    "2": ("中等", 45),
    "3": ("困難", 55),
}


def generate_puzzle(difficulty="1"):
    """
    產生題目：先做出完整解答，再挖空格子。
    挖空時會檢查是否仍為唯一解，確保題目有且只有一個答案。
    """
    _, holes = DIFFICULTY_HOLES.get(difficulty, DIFFICULTY_HOLES["1"])

    solution = generate_full_board()
    puzzle = copy.deepcopy(solution)

    cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(cells)

    removed = 0
    for r, c in cells:
        if removed >= holes:
            break

        backup = puzzle[r][c]
        puzzle[r][c] = 0

        # 複製一份確認是否仍為唯一解
        test_board = copy.deepcopy(puzzle)
        if count_solutions(test_board, limit=2) != 1:
            puzzle[r][c] = backup  # 還原，這格不能挖
        else:
            removed += 1

    return puzzle, solution


# ---------------------------------------------------------------------------
# 顯示盤面
# ---------------------------------------------------------------------------

def print_board(board, original=None):
    """
    印出數獨盤面。
    若提供 original（題目原始盤面），玩家自己填的數字會用括號標示，
    方便和題目原本就有的數字做區分。
    """
    print()
    for r in range(SIZE):
        if r % BOX == 0 and r != 0:
            print("-" * 21)
        row_str = ""
        for c in range(SIZE):
            if c % BOX == 0 and c != 0:
                row_str += "| "
            val = board[r][c]
            if val == 0:
                row_str += ". "
            else:
                row_str += f"{val} "
        print(row_str)
    print()


# ---------------------------------------------------------------------------
# 遊戲主流程
# ---------------------------------------------------------------------------

def print_help():
    print(
        "指令說明：\n"
        "  直接輸入「列 欄 數字」來填格，例如：3 5 7 表示在第3列第5欄填入7\n"
        "  h  -> 提示（自動填入一格正解）\n"
        "  c  -> 檢查目前是否有錯誤\n"
        "  s  -> 直接顯示完整解答\n"
        "  r  -> 重新開始（重新出題）\n"
        "  q  -> 離開遊戲\n"
        "  ?  -> 顯示這個說明\n"
        "  （列、欄座標範圍為 1~9）\n"
    )


def choose_difficulty():
    print("請選擇難度：")
    for key, (name, holes) in DIFFICULTY_HOLES.items():
        print(f"  {key}. {name}（挖空 {holes} 格）")
    choice = input("輸入選項 (預設 1): ").strip()
    if choice not in DIFFICULTY_HOLES:
        choice = "1"
    return choice


def check_board(board, solution):
    """比對玩家目前盤面與正確解答，回傳是否完全正確與是否已經填滿"""
    filled = all(board[r][c] != 0 for r in range(SIZE) for c in range(SIZE))
    correct = all(
        board[r][c] == 0 or board[r][c] == solution[r][c]
        for r in range(SIZE)
        for c in range(SIZE)
    )
    return correct, filled


def give_hint(board, original, solution):
    """找一個目前是空格的位置，直接填入正解"""
    empty_cells = [
        (r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] == 0
    ]
    if not empty_cells:
        print("盤面已經填滿囉！")
        return
    r, c = random.choice(empty_cells)
    board[r][c] = solution[r][c]
    print(f"提示：第 {r + 1} 列、第 {c + 1} 欄 填入 {solution[r][c]}")


def play():
    print("=" * 40)
    print("       歡迎來玩終端機數獨！")
    print("=" * 40)
    print_help()

    difficulty = choose_difficulty()
    puzzle, solution = generate_puzzle(difficulty)
    board = copy.deepcopy(puzzle)

    while True:
        print_board(board)
        user_input = input("請輸入指令（輸入 ? 查看說明）: ").strip().lower()

        if user_input == "q":
            print("感謝遊玩，掰掰！")
            break

        elif user_input == "?":
            print_help()

        elif user_input == "r":
            difficulty = choose_difficulty()
            puzzle, solution = generate_puzzle(difficulty)
            board = copy.deepcopy(puzzle)
            print("已重新出題！")

        elif user_input == "s":
            print("完整解答：")
            print_board(solution)

        elif user_input == "h":
            give_hint(board, puzzle, solution)

        elif user_input == "c":
            correct, filled = check_board(board, solution)
            if not correct:
                print("目前盤面有錯誤，請再檢查一下！")
            elif filled:
                print("恭喜！完全正確，你解出這個數獨了！🎉")
            else:
                print("目前為止都正確，繼續加油！")

        else:
            parts = user_input.split()
            if len(parts) != 3:
                print("輸入格式錯誤，請輸入「列 欄 數字」，例如：3 5 7")
                continue

            try:
                row, col, num = (int(x) for x in parts)
            except ValueError:
                print("請輸入數字，例如：3 5 7")
                continue

            if not (1 <= row <= 9 and 1 <= col <= 9 and 1 <= num <= 9):
                print("列、欄、數字都必須介於 1~9 之間")
                continue

            r, c = row - 1, col - 1
            if puzzle[r][c] != 0:
                print("這一格是題目原本就給的數字，不能修改")
                continue

            board[r][c] = num

            correct, filled = check_board(board, solution)
            if filled and correct:
                print_board(board)
                print("恭喜！完全正確，你解出這個數獨了！🎉")
                break


if __name__ == "__main__":
    play()