import math
import copy
import random
import time

SIZE = 5
EMPTY = "."
MAX_PIECES = 5
players = ["X", "O"]

nodes_expanded = 0
max_depth_reached = 0


# =========================================
# ESTADO DEL JUEGO
# =========================================
class GameState:
    def __init__(self, board, pieces_left, turn):
        self.board = board
        self.pieces_left = pieces_left
        self.turn = turn

    def clone(self):
        return GameState(copy.deepcopy(self.board), self.pieces_left.copy(), self.turn)

    def in_bounds(self, x, y):
        return 0 <= x < SIZE and 0 <= y < SIZE

    def neighbors(self, x, y):
        return [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]

    def collapse(self, opponent):
        removed_any = False
        removed = True
        while removed:
            removed = False
            to_remove = []
            for x in range(SIZE):
                for y in range(SIZE):
                    if self.board[x][y] == opponent:
                        attackers = 0
                        for nx, ny in self.neighbors(x, y):
                            if self.in_bounds(nx, ny) and self.board[nx][ny] not in (opponent, EMPTY):
                                attackers += 1
                        if attackers >= 2:
                            to_remove.append((x,y))

            for x,y in to_remove:
                self.board[x][y] = EMPTY
                removed = True
                removed_any = True

        return removed_any

    def count(self, player):
        return sum(row.count(player) for row in self.board)

    def get_moves(self):
        moves = []
        player = players[self.turn]
        if self.pieces_left[player] == 0:
            return moves
        for x in range(SIZE):
            for y in range(SIZE):
                if self.board[x][y] == EMPTY:
                    moves.append((x,y))
        return moves

    def apply_move(self, move):
        new_state = self.clone()
        player = players[self.turn]
        opponent = players[1 - self.turn]

        x,y = move
        new_state.board[x][y] = player
        new_state.pieces_left[player] -= 1

        collapsed = new_state.collapse(opponent)

        new_state.turn = 1 - self.turn
        return new_state, collapsed

    def is_terminal(self):
        total = self.count("X") + self.count("O")

        if total == 0:
            return False

        if self.pieces_left["X"] == 0 and self.pieces_left["O"] == 0:
            return True

        return False

    def evaluate(self, heuristic=1):
        x = self.count("X")
        o = self.count("O")

        if heuristic == 1:
            return x - o
        elif heuristic == 2:
            return (x - o) + (self.pieces_left["X"] - self.pieces_left["O"])
        elif heuristic == 3:
            return (x*2 - o*2)
        elif heuristic == 4:
            return (x - o) + random.uniform(-0.5, 0.5)
        elif heuristic == 5:
            return (x - o) * 3 + len(self.get_moves())
        return x - o


# =========================================
# MINIMAX + PODA ALFA BETA
# =========================================
def minimax(state, depth, alpha, beta, maximizing, heuristic, current_depth=0):
    global nodes_expanded, max_depth_reached
    nodes_expanded += 1
    max_depth_reached = max(max_depth_reached, current_depth)

    if depth == 0 or state.is_terminal():
        return state.evaluate(heuristic)

    if maximizing:
        value = -math.inf
        for move in state.get_moves():
            child, _ = state.apply_move(move)
            value = max(value, minimax(child, depth-1, alpha, beta, False, heuristic, current_depth+1))
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value
    else:
        value = math.inf
        for move in state.get_moves():
            child, _ = state.apply_move(move)
            value = min(value, minimax(child, depth-1, alpha, beta, True, heuristic, current_depth+1))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value


def iterative_deepening(state, max_time, heuristic):
    start = time.time()
    best_move = None
    depth = 1

    while time.time() - start < max_time:
        best_val = -math.inf
        for move in state.get_moves():
            child, _ = state.apply_move(move)
            val = minimax(child, depth, -math.inf, math.inf, False, heuristic)
            if val > best_val:
                best_val = val
                best_move = move
        depth += 1

    return best_move


# =========================================
# JUGADORES
# =========================================
def random_player(state):
    return random.choice(state.get_moves())

def greedy_player(state):
    best = None
    best_val = -math.inf
    for m in state.get_moves():
        child, _ = state.apply_move(m)
        val = child.evaluate(1)
        if val > best_val:
            best_val = val
            best = m
    return best

def worst_player(state):
    worst = None
    worst_val = math.inf
    for m in state.get_moves():
        child, _ = state.apply_move(m)
        val = child.evaluate(1)
        if val < worst_val:
            worst_val = val
            worst = m
    return worst

def minimax_player(state, heuristic=1, time_limit=2):
    return iterative_deepening(state, time_limit, heuristic)

def human_player(state):
    print("Ingresa fila y columna (ej: 2 3):")
    x, y = map(int, input().split())
    return (x, y)


# =========================================
# IMPRESIÓN
# =========================================
def print_board(board):
    print("\n  " + " ".join(str(i) for i in range(SIZE)))
    for i,row in enumerate(board):
        print(f"{i} " + " ".join(row))
    print()


# =========================================
# MOTOR DE PARTIDA
# =========================================
def play_game(player_X, player_O, visual=True):
    global nodes_expanded, max_depth_reached
    nodes_expanded = 0
    max_depth_reached = 0

    board = [[EMPTY]*SIZE for _ in range(SIZE)]
    pieces = {"X": MAX_PIECES, "O": MAX_PIECES}
    state = GameState(board, pieces, 0)

    if visual:
        print("\n🎮 INICIANDO PARTIDA\n")

    while not state.is_terminal():
        if visual:
            print_board(state.board)

        player = players[state.turn]

        if player == "X":
            move = player_X(state)
        else:
            move = player_O(state)

        if move is None:
            break

        if visual:
            print(f"➡️ {player} juega en {move}")

        state, collapsed = state.apply_move(move)

        if collapsed and visual:
            print("💥 ¡Colapso de fichas!")

    if visual:
        print_board(state.board)
        print("\n🏁 FIN DEL JUEGO")
        print("Resultado:", state.evaluate())

    return state   


# =========================================
# BENCHMARK AUTOMÁTICO
# =========================================
def run_benchmark():
    global nodes_expanded, max_depth_reached

    opponents = [
        ("Random", random_player),
        ("Greedy", greedy_player),
        ("Worst", worst_player),
        ("Self", lambda s: minimax_player(s, heuristic=1, time_limit=2))
    ]

    heuristics = [1, 2, 3, 4, 5]
    times = [1, 3, 10]

    results = []

    print("\n==============================")
    print("🚀 INICIANDO BENCHMARK")
    print("==============================\n")

    for h in heuristics:
        for t in times:
            for name, opponent in opponents:

                nodes_expanded = 0
                max_depth_reached = 0

                start_time = time.time()

                state = play_game(
                    lambda s: minimax_player(s, heuristic=h, time_limit=t),
                    opponent,
                    visual=False
                )

                end_time = time.time()

                exec_time = end_time - start_time
                final_score = state.evaluate()

                winner = "Empate"
                if final_score > 0:
                    winner = "Minimax (X)"
                elif final_score < 0:
                    winner = name + " (O)"

                result_row = {
                    "heuristic": h,
                    "time_limit": t,
                    "opponent": name,
                    "winner": winner,
                    "score": final_score,
                    "nodes": nodes_expanded,
                    "depth": max_depth_reached,
                    "time": round(exec_time, 4)
                }

                results.append(result_row)

                print(f"✔ H{h} | T={t}s | vs {name} -> {winner} | score={final_score} | nodes={nodes_expanded} | depth={max_depth_reached} | time={round(exec_time,2)}s")

    print("\n==============================")
    print("📊 RESULTADOS FINALES")
    print("==============================\n")

    for r in results:
        print(r)

    return results


# =========================================
# MENÚ PRINCIPAL
# =========================================
def menu_partidas():
    print("\n=== MODO PARTIDA INDIVIDUAL ===")
    print("Selecciona el tipo de oponente:")
    print("1 - Contra jugador aleatorio")
    print("2 - Contra jugador greedy")
    print("3 - Contra jugador worst (peor decisión)")
    print("4 - Contra humano experto")
    print("5 - Contra otra IA (Minimax)")

    op = input("Opción: ")

    print("\nConfiguración de IA:")
    heuristic = int(input("Selecciona heurística (1-5): "))
    time_limit = int(input("Tiempo límite en segundos (1 / 3 / 10): "))

    ia_player = lambda s: minimax_player(s, heuristic=heuristic, time_limit=time_limit)

    if op == "1":
        opponent = random_player
    elif op == "2":
        opponent = greedy_player
    elif op == "3":
        opponent = worst_player
    elif op == "4":
        opponent = human_player
    elif op == "5":
        opponent = ia_player
    else:
        print("Opción inválida")
        return

    # IA vs oponente
    play_game(opponent, ia_player, visual=True)


# =========================================
# MENÚ PRINCIPAL
# =========================================
def menu_partidas():
    print("\n=== MODO PARTIDA INDIVIDUAL ===")
    print("Selecciona el tipo de oponente:")
    print("1 - Contra jugador aleatorio")
    print("2 - Contra jugador greedy")
    print("3 - Contra jugador worst (peor decisión)")
    print("4 - Contra humano experto")
    print("5 - Contra otra IA (Minimax)")

    op = input("Opción: ")

    print("\nConfiguración de IA:")
    heuristic = int(input("Selecciona heurística (1-5): "))
    time_limit = int(input("Tiempo límite en segundos (1 / 3 / 10): "))

    ia_player = lambda s: minimax_player(s, heuristic=heuristic, time_limit=time_limit)

    if op == "1":
        opponent = random_player
    elif op == "2":
        opponent = greedy_player
    elif op == "3":
        opponent = worst_player
    elif op == "4":
        opponent = human_player
    elif op == "5":
        opponent = ia_player
    else:
        print("Opción inválida")
        return

    # IA vs oponente
    play_game(opponent, ia_player, visual=True)


# =========================================
# MENÚ PRINCIPAL
# =========================================
print("1 - Ver partidas una por una (Worst, Greedy, etc.)")
print("2 - Ejecutar Benchmark")

op = input("Selecciona opción: ")

if op == "1":
    menu_partidas()
elif op == "2":
    run_benchmark()
else:
    print("Opción inválida")


input("\nPresiona ENTER para cerrar...")