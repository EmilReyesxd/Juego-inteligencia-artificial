# Collapsi de consola 

SIZE = 5
EMPTY = "."
MAX_PIECES = 5

board = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]
pieces_left = {"X": MAX_PIECES, "O": MAX_PIECES}

def print_board():
    print("\n  " + " ".join(str(i) for i in range(SIZE)))
    for i, row in enumerate(board):
        print(f"{i} " + " ".join(row))
    print()

def in_bounds(x, y):
    return 0 <= x < SIZE and 0 <= y < SIZE

def neighbors(x, y):
    return [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]

def collapse(opponent):
    removed = True
    while removed:
        removed = False
        to_remove = []
        for x in range(SIZE):
            for y in range(SIZE):
                if board[x][y] == opponent:
                    attackers = 0
                    for nx, ny in neighbors(x, y):
                        if in_bounds(nx, ny) and board[nx][ny] not in (opponent, EMPTY):
                            attackers += 1
                    if attackers >= 2:
                        to_remove.append((x, y))
        for x, y in to_remove:
            board[x][y] = EMPTY
            removed = True

def count_pieces(player):
    return sum(row.count(player) for row in board)

players = ["X", "O"]
turn = 0

print("🎮 COLLASPI - Consola")
print(f"Límite de fichas por jugador: {MAX_PIECES}")

while True:
    print_board()
    player = players[turn]
    opponent = players[1 - turn]

    if pieces_left[player] == 0:
        print(f"El jugador {player} no tiene más fichas para colocar.")
        turn = 1 - turn
        continue

    print(f"Turno del jugador {player} | Fichas restantes: {pieces_left[player]}")
    try:
        x, y = map(int, input("Fila Columna: ").split())
    except:
        print("Entrada inválida.")
        continue

    if not in_bounds(x, y) or board[x][y] != EMPTY:
        print("Movimiento inválido.")
        continue

    opponent_pieces_before = count_pieces(opponent)

    board[x][y] = player
    pieces_left[player] -= 1
    collapse(opponent)

    if opponent_pieces_before >= 2 and count_pieces(opponent) == 0:
        print_board()
        print(f"🏆 ¡Gana el jugador {player}!")
        break

    if pieces_left["X"] == 0 and pieces_left["O"] == 0:
        print_board()
        x_count = count_pieces("X")
        o_count = count_pieces("O")
        print("🔚 Ambos jugadores sin fichas")
        print(f"X: {x_count} | O: {o_count}")
        if x_count > o_count:
            print("🏆 Gana X")
        elif o_count > x_count:
            print("🏆 Gana O")
        else:
            print("🤝 Empate")
        break

    turn = 1 - turn
