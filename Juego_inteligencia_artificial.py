import random
import time
import math
from copy import deepcopy

# Config
SIZE = 7
SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

# Deck del tablero para mostrarlo del 1 al 12 random
def create_deck():
    deck = []
    for _ in range(2):
        for suit in SUITS:
            for rank in RANKS:
                deck.append(rank + suit)
    random.shuffle(deck)
    return deck

# Crear el tablero
def create_board(deck):
    board = []
    for i in range(SIZE):
        row = []
        for j in range(SIZE):
            row.append(deck.pop())
        board.append(row)
    return board

# ===== MOSTRAR TABLERO =====
def print_board(board, players, scores=None):
    print("\n" + "="*50)
    print("TABLERO:")
    for i in range(SIZE):
        for j in range(SIZE):
            cell = board[i][j]
            for idx, p in enumerate(players):
                if p["pos"] == (i, j):
                    cell = f"P{idx+1}"
            print(f"{cell:4}", end="")
        print()
    
    if scores:
        print("\nPUNTUACIONES:")
        for idx, score in enumerate(scores):
            print(f"Jugador {idx+1}: {score} puntos")
    print("="*50)

# ===== VALOR NUMÉRICO =====
def card_value(card):
    rank = card[:-1]
    if rank == "A":
        return 1
    elif rank == "J":
        return 11
    elif rank == "Q":
        return 12
    elif rank == "K":
        return 13
    else:
        return int(rank)

# ===== VALIDAR MOVIMIENTO =====
def is_valid_move(board, pos, direction, steps):
    x, y = pos
    dx, dy = 0, 0

    if direction == "w": dx = -1
    elif direction == "s": dx = 1
    elif direction == "a": dy = -1
    elif direction == "d": dy = 1
    else: return False

    for step in range(1, steps + 1):
        nx = x + dx * step
        ny = y + dy * step

        if not (0 <= nx < SIZE and 0 <= ny < SIZE):
            return False
        if board[nx][ny] == "XX":
            return False

    return True

# ===== OBTENER MOVIMIENTOS VÁLIDOS =====
def get_valid_moves(board, pos, steps):
    valid_moves = []
    directions = ["w", "a", "s", "d"]
    for direction in directions:
        if is_valid_move(board, pos, direction, steps):
            valid_moves.append(direction)
    return valid_moves

# ===== REALIZAR MOVIMIENTO =====
def move_player(board, player, direction, steps):
    x, y = player["pos"]
    dx, dy = 0, 0

    if direction == "w": dx = -1
    elif direction == "s": dx = 1
    elif direction == "a": dy = -1
    elif direction == "d": dy = 1

    for step in range(1, steps + 1):
        nx = x + dx * step
        ny = y + dy * step
        board[nx][ny] = "XX"

    player["pos"] = (x + dx * steps, y + dy * steps)

# ===== VERIFICAR SI EXISTE DIRECCIÓN VÁLIDA PARA UN NÚMERO =====
def has_valid_direction(board, pos, steps):
    for d in ["w", "a", "s", "d"]:
        if is_valid_move(board, pos, d, steps):
            return True
    return False

# ===== VERIFICAR SI EL JUGADOR ESTÁ COMPLETAMENTE ENCERRADO =====
def is_player_trapped(board, pos):
    for d in ["w", "a", "s", "d"]:
        if is_valid_move(board, pos, d, 1):
            return False
    return True

# ===== CALCULAR DISTANCIA ENTRE JUGADORES =====
def distance_between_players(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

# ===== CONTAR ESPACIOS VECINOS VÁLIDOS =====
def count_valid_neighbors(board, pos):
    count = 0
    for d in ["w", "a", "s", "d"]:
        if is_valid_move(board, pos, d, 1):
            count += 1
    return count

# ===== CALCULAR PUNTUACIÓN =====
def calculate_score(board, players):
    scores = []
    for player in players:
        score = 0
        # Puntos por espacios alrededor
        score += count_valid_neighbors(board, player["pos"]) * 10
        
        # Puntos por posición central
        x, y = player["pos"]
        center_dist = abs(x - SIZE//2) + abs(y - SIZE//2)
        score += (SIZE - center_dist) * 5
        
        scores.append(score)
    return scores

# ===== HEURÍSTICAS PARA LA IA =====
class Heuristics:
    def __init__(self, weights=None):
        # Pesos por defecto para las heurísticas
        if weights is None:
            self.weights = {
                'movilidad': 1.0,
                'centralidad': 1.0,
                'distancia_oponente': 1.0,
                'espacios_ocupados': 1.0,
                'potencial_futuro': 1.0
            }
        else:
            self.weights = weights
    
    def movilidad(self, board, pos):
        """Heurística 1: Evalúa la movilidad del jugador"""
        total_mobility = 0
        for steps in range(1, 4):  # Evaluar movimientos de 1-3 pasos
            moves = get_valid_moves(board, pos, steps)
            total_mobility += len(moves) * (4 - steps)  # Mayor peso a movimientos cortos
        return total_mobility
    
    def centralidad(self, board, pos):
        """Heurística 2: Evalúa qué tan cerca del centro está el jugador"""
        x, y = pos
        center_x, center_y = SIZE // 2, SIZE // 2
        distance = abs(x - center_x) + abs(y - center_y)
        return (SIZE - distance) * 2
    
    def distancia_oponente(self, board, pos, opponent_pos):
        """Heurística 3: Evalúa la distancia al oponente"""
        dist = distance_between_players(pos, opponent_pos)
        # Preferir estar cerca del oponente para atraparlo
        return (SIZE * 2 - dist) * 3
    
    def espacios_ocupados(self, board, pos):
        """Heurística 4: Evalúa cuántos espacios alrededor están ocupados"""
        x, y = pos
        occupied = 0
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < SIZE and 0 <= ny < SIZE:
                if board[nx][ny] == "XX":
                    occupied += 1
        return occupied * 5
    
    def potencial_futuro(self, board, pos):
        """Heurística 5: Evalúa el potencial de movimientos futuros"""
        potential = 0
        x, y = pos
        # Revisar en todas las direcciones
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            for step in range(1, 4):
                nx, ny = x + dx * step, y + dy * step
                if 0 <= nx < SIZE and 0 <= ny < SIZE:
                    if board[nx][ny] != "XX":
                        potential += 1
        return potential
    
    def evaluate(self, board, player_idx, players):
        """Evalúa el estado actual del juego para un jugador"""
        player_pos = players[player_idx]["pos"]
        opponent_pos = players[1 - player_idx]["pos"]
        
        score = 0
        score += self.weights['movilidad'] * self.movilidad(board, player_pos)
        score += self.weights['centralidad'] * self.centralidad(board, player_pos)
        score += self.weights['distancia_oponente'] * self.distancia_oponente(board, player_pos, opponent_pos)
        score += self.weights['espacios_ocupados'] * self.espacios_ocupados(board, player_pos)
        score += self.weights['potencial_futuro'] * self.potencial_futuro(board, player_pos)
        
        return score

# ===== AGENTE IA CON MINIMAX =====
class MinimaxAgent:
    def __init__(self, player_idx, max_time=3, weights=None):
        self.player_idx = player_idx
        self.max_time = max_time
        self.heuristics = Heuristics(weights)
        self.nodes_expanded = 0
        self.max_depth_reached = 0
        self.start_time = 0
    
    def get_action(self, board, players, draw_deck):
        """Obtiene la mejor acción usando minimax con poda alpha-beta e IDS"""
        self.start_time = time.time()
        self.nodes_expanded = 0
        self.max_depth_reached = 0
        
        best_action = None
        depth = 1
        
        try:
            while time.time() - self.start_time < self.max_time:
                # Intentar con profundidad actual
                action = self.ids_minimax(board, players, draw_deck, depth)
                if action:
                    best_action = action
                depth += 1
        except TimeoutError:
            pass
        
        return best_action
    
    def ids_minimax(self, board, players, draw_deck, max_depth):
        """Minimax con profundidad iterativa"""
        alpha = -math.inf
        beta = math.inf
        
        # Obtener carta actual
        if not draw_deck:
            return None
        
        current_card = draw_deck[-1]
        steps = card_value(current_card)
        valid_moves = get_valid_moves(board, players[self.player_idx]["pos"], steps)
        
        if not valid_moves:
            return None
        
        best_value = -math.inf
        best_move = valid_moves[0]
        
        for move in valid_moves:
            # Simular movimiento
            new_board = deepcopy(board)
            new_players = deepcopy(players)
            
            move_player(new_board, new_players[self.player_idx], move, steps)
            
            value = self.min_value(new_board, new_players, draw_deck[:-1], 
                                  alpha, beta, 1, max_depth)
            
            if value > best_value:
                best_value = value
                best_move = move
            
            alpha = max(alpha, best_value)
        
        return best_move
    
    def max_value(self, board, players, draw_deck, alpha, beta, depth, max_depth):
        """Función MAX del minimax"""
        self.nodes_expanded += 1
        self.max_depth_reached = max(self.max_depth_reached, depth)
        
        # Verificar timeout
        if time.time() - self.start_time > self.max_time:
            raise TimeoutError()
        
        # Verificar estado terminal
        if self.is_terminal(board, players, draw_deck):
            return self.evaluate_terminal(board, players, self.player_idx, draw_deck)
        
        if depth >= max_depth:
            return self.heuristics.evaluate(board, self.player_idx, players)
        
        # Obtener carta actual
        if not draw_deck:
            return self.heuristics.evaluate(board, self.player_idx, players)
        
        current_card = draw_deck[-1]
        steps = card_value(current_card)
        valid_moves = get_valid_moves(board, players[self.player_idx]["pos"], steps)
        
        if not valid_moves:
            return self.heuristics.evaluate(board, self.player_idx, players)
        
        value = -math.inf
        for move in valid_moves:
            new_board = deepcopy(board)
            new_players = deepcopy(players)
            
            move_player(new_board, new_players[self.player_idx], move, steps)
            
            value = max(value, self.min_value(new_board, new_players, draw_deck[:-1],
                                             alpha, beta, depth + 1, max_depth))
            
            if value >= beta:
                return value
            alpha = max(alpha, value)
        
        return value
    
    def min_value(self, board, players, draw_deck, alpha, beta, depth, max_depth):
        """Función MIN del minimax"""
        self.nodes_expanded += 1
        self.max_depth_reached = max(self.max_depth_reached, depth)
        
        # Verificar timeout
        if time.time() - self.start_time > self.max_time:
            raise TimeoutError()
        
        # Verificar estado terminal
        if self.is_terminal(board, players, draw_deck):
            return self.evaluate_terminal(board, players, 1 - self.player_idx, draw_deck)
        
        if depth >= max_depth:
            return self.heuristics.evaluate(board, 1 - self.player_idx, players)
        
        # Obtener carta actual
        if not draw_deck:
            return self.heuristics.evaluate(board, 1 - self.player_idx, players)
        
        current_card = draw_deck[-1]
        steps = card_value(current_card)
        valid_moves = get_valid_moves(board, players[1 - self.player_idx]["pos"], steps)
        
        if not valid_moves:
            return self.heuristics.evaluate(board, 1 - self.player_idx, players)
        
        value = math.inf
        for move in valid_moves:
            new_board = deepcopy(board)
            new_players = deepcopy(players)
            
            move_player(new_board, new_players[1 - self.player_idx], move, steps)
            
            value = min(value, self.max_value(new_board, new_players, draw_deck[:-1],
                                             alpha, beta, depth + 1, max_depth))
            
            if value <= alpha:
                return value
            beta = min(beta, value)
        
        return value
    
    def is_terminal(self, board, players, draw_deck):
        """Verifica si el juego ha terminado"""
        # Verificar si algún jugador está atrapado
        for player in players:
            if is_player_trapped(board, player["pos"]):
                return True
        
        # Verificar si no hay cartas
        if not draw_deck:
            return True
        
        return False
    
    def evaluate_terminal(self, board, players, player_idx, draw_deck):
        """Evalúa un estado terminal"""
        if is_player_trapped(board, players[player_idx]["pos"]):
            return -1000  # Jugador actual pierde
        elif is_player_trapped(board, players[1 - player_idx]["pos"]):
            return 1000   # Jugador actual gana
        elif not draw_deck:
            return 0      # Empate
        return 0

# ===== JUGADORES ALEATORIOS, GREEDY, ETC =====
class RandomPlayer:
    def __init__(self, player_idx):
        self.player_idx = player_idx
    
    def get_action(self, board, players, draw_deck):
        if not draw_deck:
            return None
        
        current_card = draw_deck[-1]
        steps = card_value(current_card)
        valid_moves = get_valid_moves(board, players[self.player_idx]["pos"], steps)
        
        if valid_moves:
            return random.choice(valid_moves)
        return None

class GreedyPlayer:
    def __init__(self, player_idx):
        self.player_idx = player_idx
        self.heuristics = Heuristics()
    
    def get_action(self, board, players, draw_deck):
        if not draw_deck:
            return None
        
        current_card = draw_deck[-1]
        steps = card_value(current_card)
        valid_moves = get_valid_moves(board, players[self.player_idx]["pos"], steps)
        
        if not valid_moves:
            return None
        
        best_move = valid_moves[0]
        best_value = -math.inf
        
        for move in valid_moves:
            new_board = deepcopy(board)
            new_players = deepcopy(players)
            
            move_player(new_board, new_players[self.player_idx], move, steps)
            
            value = self.heuristics.evaluate(new_board, self.player_idx, new_players)
            
            if value > best_value:
                best_value = value
                best_move = move
        
        return best_move

class WorstPlayer:
    def __init__(self, player_idx):
        self.player_idx = player_idx
        self.heuristics = Heuristics()
    
    def get_action(self, board, players, draw_deck):
        if not draw_deck:
            return None
        
        current_card = draw_deck[-1]
        steps = card_value(current_card)
        valid_moves = get_valid_moves(board, players[self.player_idx]["pos"], steps)
        
        if not valid_moves:
            return None
        
        worst_move = valid_moves[0]
        worst_value = math.inf
        
        for move in valid_moves:
            new_board = deepcopy(board)
            new_players = deepcopy(players)
            
            move_player(new_board, new_players[self.player_idx], move, steps)
            
            value = self.heuristics.evaluate(new_board, self.player_idx, new_players)
            
            if value < worst_value:
                worst_value = value
                worst_move = move
        
        return worst_move

# ===== JUEGO PRINCIPAL =====
def play_game(players_config, num_games=1):
    """
    players_config: Lista de diccionarios con configuración de cada jugador
    Ejemplo: [{"type": "human"}, {"type": "ai", "max_time": 3, "weights": {...}}]
    """
    results = []
    
    for game_num in range(num_games):
        print(f"\n{'='*60}")
        print(f"PARTIDA {game_num + 1} DE {num_games}")
        print('='*60)
        
        # Inicializar juego
        deck = create_deck()
        board_deck = deck[:SIZE*SIZE]
        draw_deck = deck[SIZE*SIZE:]
        board = create_board(board_deck)
        
        players = [
            {"pos": (0, 0)},
            {"pos": (SIZE-1, SIZE-1)}
        ]
        
        # Crear agentes según configuración
        agents = []
        for idx, config in enumerate(players_config):
            if config["type"] == "human":
                agents.append(None)
            elif config["type"] == "ai":
                agents.append(MinimaxAgent(idx, config.get("max_time", 3), config.get("weights")))
            elif config["type"] == "random":
                agents.append(RandomPlayer(idx))
            elif config["type"] == "greedy":
                agents.append(GreedyPlayer(idx))
            elif config["type"] == "worst":
                agents.append(WorstPlayer(idx))
        
        current = 0
        game_result = {
            "game_num": game_num + 1,
            "winner": None,
            "scores": None,
            "nodes_expanded": 0,
            "max_depth": 0,
            "execution_time": 0
        }
        
        start_time = time.time()
        
        while True:
            print_board(board, players)
            
            # Verificar condiciones de victoria
            if is_player_trapped(board, players[0]["pos"]):
                print("¡Jugador 1 está encerrado! Jugador 2 gana.")
                game_result["winner"] = 2
                break
            elif is_player_trapped(board, players[1]["pos"]):
                print("¡Jugador 2 está encerrado! Jugador 1 gana.")
                game_result["winner"] = 1
                break
            
            if not draw_deck:
                print("No quedan cartas. ¡Empate!")
                game_result["winner"] = 0
                break
            
            player = players[current]
            agent = agents[current]
            
            # Mostrar carta actual
            current_card = draw_deck[-1]
            steps = card_value(current_card)
            
            print(f"\nTurno del Jugador {current + 1}")
            print(f"Carta actual: {current_card} (movimiento de {steps} espacios)")
            
            # Obtener movimiento según tipo de jugador
            if agent is None:  # Jugador humano
                valid_moves = get_valid_moves(board, player["pos"], steps)
                
                if not valid_moves:
                    print("¡No hay movimientos válidos! Se descarta la carta.")
                    draw_deck.pop()
                    current = 1 - current
                    continue
                
                while True:
                    direction = input("Dirección (w=↑ s=↓ a=← d=→): ").lower()
                    if direction in valid_moves:
                        move_player(board, player, direction, steps)
                        draw_deck.pop()  # Descartar carta usada
                        break
                    else:
                        print("Dirección inválida. Intenta otra.")
            else:  # Jugador IA
                print("La IA está pensando...")
                
                move_start = time.time()
                direction = agent.get_action(board, players, draw_deck)
                move_time = time.time() - move_start
                
                if direction:
                    print(f"La IA elige moverse hacia: {direction}")
                    print(f"Tiempo de decisión: {move_time:.2f} segundos")
                    
                    # SOLO mostrar y acumular estadísticas si es un agente Minimax
                    if isinstance(agent, MinimaxAgent):
                        print(f"Nodos expandidos en esta jugada: {agent.nodes_expanded}")
                        print(f"Profundidad máxima alcanzada: {agent.max_depth_reached}")
                        game_result["nodes_expanded"] += agent.nodes_expanded
                        game_result["max_depth"] = max(game_result["max_depth"], agent.max_depth_reached)
                    
                    move_player(board, player, direction, steps)
                    draw_deck.pop()  # Descartar carta usada
                else:
                    print("La IA no tiene movimientos válidos. Se descarta la carta.")
                    draw_deck.pop()
            
            current = 1 - current
        
        game_result["execution_time"] = time.time() - start_time
        game_result["scores"] = calculate_score(board, players)
        
        results.append(game_result)
        
        # Mostrar resultado de la partida
        print(f"\nRESULTADO PARTIDA {game_num + 1}:")
        if game_result["winner"] == 0:
            print("¡EMPATE!")
        else:
            print(f"¡GANA JUGADOR {game_result['winner']}!")
        print(f"Puntuaciones: Jugador 1: {game_result['scores'][0]}, Jugador 2: {game_result['scores'][1]}")
        print(f"Nodos totales expandidos: {game_result['nodes_expanded']}")
        print(f"Profundidad máxima: {game_result['max_depth']}")
        print(f"Tiempo total de partida: {game_result['execution_time']:.2f} segundos")
    
    return results

# ===== BENCHMARK MEJORADO (TODAS LAS COMBINACIONES) =====
def run_benchmark():
    """Ejecuta el benchmark con TODAS las combinaciones para no dejar celdas vacías"""
    
    print("\n" + "="*80)
    print("BENCHMARK COMPLETO - TODAS LAS COMBINACIONES")
    print("="*80)
    print("\nEste benchmark probará TODAS las configuraciones contra TODOS los oponentes")
    print("para que no queden celdas vacías en las tablas.")
    print("\nEsto puede tomar MUCHO tiempo (varios minutos u horas)...")
    
    confirm = input("\n¿Estás seguro de continuar? (s/n): ")
    if confirm.lower() != 's':
        print("Benchmark cancelado.")
        return
    
    benchmark_results = []
    
    # Configuraciones de pesos
    weight_configs = [
        {"name": "Config1 - Pesos balanceados", "weights": {'movilidad': 1.0, 'centralidad': 1.0, 'distancia_oponente': 1.0, 'espacios_ocupados': 1.0, 'potencial_futuro': 1.0}},
        {"name": "Config2 - Énfasis en movilidad", "weights": {'movilidad': 3.0, 'centralidad': 1.0, 'distancia_oponente': 1.0, 'espacios_ocupados': 1.0, 'potencial_futuro': 1.0}},
    ]
    
    # Diferentes números de heurísticas
    heuristic_configs = [
        {"name": "1 heurística (solo movilidad)", "weights": {'movilidad': 1.0, 'centralidad': 0, 'distancia_oponente': 0, 'espacios_ocupados': 0, 'potencial_futuro': 0}},
        {"name": "2 heurísticas (movilidad + centralidad)", "weights": {'movilidad': 1.0, 'centralidad': 1.0, 'distancia_oponente': 0, 'espacios_ocupados': 0, 'potencial_futuro': 0}},
        {"name": "3 heurísticas (movilidad + centralidad + distancia)", "weights": {'movilidad': 1.0, 'centralidad': 1.0, 'distancia_oponente': 1.0, 'espacios_ocupados': 0, 'potencial_futuro': 0}},
        {"name": "4 heurísticas (movilidad + centralidad + distancia + espacios)", "weights": {'movilidad': 1.0, 'centralidad': 1.0, 'distancia_oponente': 1.0, 'espacios_ocupados': 1.0, 'potencial_futuro': 0}},
        {"name": "5 heurísticas (todas)", "weights": {'movilidad': 1.0, 'centralidad': 1.0, 'distancia_oponente': 1.0, 'espacios_ocupados': 1.0, 'potencial_futuro': 1.0}},
    ]
    
    # Configuraciones de tiempo
    time_configs = [1, 3, 10]
    
    # Tipos de oponentes (TODOS)
    opponents = [
        {"type": "random", "name": "Random"},
        {"type": "greedy", "name": "Greedy"},
        {"type": "worst", "name": "Worst"},
        {"type": "ai", "name": "Otra IA"}
    ]
    
    total_tests = 0
    total_tests += len(weight_configs) * len(opponents)
    total_tests += len(heuristic_configs) * len(opponents)
    total_tests += len(time_configs) * len(opponents)
    
    print(f"\nTotal de configuraciones a probar: {total_tests} (cada una con 3 partidas)")
    print(f"Total de partidas: {total_tests * 3}")
    
    input("\nPresiona Enter para comenzar...")
    
    # 1. Probar configuraciones de pesos contra TODOS los oponentes
    print("\n" + "="*80)
    print("1. CONFIGURACIONES DE PESOS VS TODOS LOS OPONENTES")
    print("="*80)
    
    for weight_config in weight_configs:
        for opponent in opponents:
            print(f"\n--- Probando {weight_config['name']} vs {opponent['name']} ---")
            
            if opponent["type"] == "ai":
                # Contra otra IA (misma configuración)
                config = [
                    {"type": "ai", "max_time": 3, "weights": weight_config["weights"]},
                    {"type": "ai", "max_time": 3, "weights": weight_config["weights"]}
                ]
            else:
                config = [
                    {"type": "ai", "max_time": 3, "weights": weight_config["weights"]},
                    {"type": opponent["type"]}
                ]
            
            results = play_game(config, num_games=3)
            benchmark_results.append({
                "config_type": "pesos",
                "config_name": weight_config["name"],
                "opponent": opponent["name"],
                "results": results
            })
    
    # 2. Probar diferentes números de heurísticas contra TODOS los oponentes
    print("\n" + "="*80)
    print("2. DIFERENTES HEURÍSTICAS VS TODOS LOS OPONENTES")
    print("="*80)
    
    for heuristic_config in heuristic_configs:
        for opponent in opponents:
            print(f"\n--- Probando {heuristic_config['name']} vs {opponent['name']} ---")
            
            if opponent["type"] == "ai":
                # Contra otra IA (usando mismas heurísticas)
                config = [
                    {"type": "ai", "max_time": 3, "weights": heuristic_config["weights"]},
                    {"type": "ai", "max_time": 3, "weights": heuristic_config["weights"]}
                ]
            else:
                config = [
                    {"type": "ai", "max_time": 3, "weights": heuristic_config["weights"]},
                    {"type": opponent["type"]}
                ]
            
            results = play_game(config, num_games=3)
            benchmark_results.append({
                "config_type": "heuristica",
                "config_name": heuristic_config["name"],
                "opponent": opponent["name"],
                "results": results
            })
    
    # 3. Probar diferentes tiempos contra TODOS los oponentes
    print("\n" + "="*80)
    print("3. DIFERENTES TIEMPOS VS TODOS LOS OPONENTES")
    print("="*80)
    
    for max_time in time_configs:
        for opponent in opponents:
            print(f"\n--- Probando Tiempo: {max_time}s vs {opponent['name']} ---")
            
            if opponent["type"] == "ai":
                # Contra otra IA (mismo tiempo)
                config = [
                    {"type": "ai", "max_time": max_time},
                    {"type": "ai", "max_time": max_time}
                ]
            else:
                config = [
                    {"type": "ai", "max_time": max_time},
                    {"type": opponent["type"]}
                ]
            
            results = play_game(config, num_games=3)
            benchmark_results.append({
                "config_type": "tiempo",
                "config_name": f"Tiempo: {max_time}s",
                "opponent": opponent["name"],
                "results": results
            })
    
    # Mostrar resultados en formato tabla
    mostrar_resultados_benchmark(benchmark_results)

def mostrar_resultados_benchmark(benchmark_results):
    """Muestra los resultados del benchmark en formato de tablas"""
    
    print("\n" + "="*100)
    print("RESULTADOS DEL BENCHMARK - TODAS LAS COMBINACIONES")
    print("="*100)
    
    # Agrupar resultados por tipo de configuración
    resultados_pesos = [r for r in benchmark_results if r["config_type"] == "pesos"]
    resultados_heuristicas = [r for r in benchmark_results if r["config_type"] == "heuristica"]
    resultados_tiempos = [r for r in benchmark_results if r["config_type"] == "tiempo"]
    
    # TABLA 1: Configuraciones de pesos vs Todos los oponentes
    print("\n" + "-"*100)
    print("TABLA 1: CONFIGURACIONES DE PESOS VS TODOS LOS OPONENTES")
    print("-"*100)
    print(f"{'Configuración':<30} {'Oponente':<15} {'V-D-E':<15} {'Puntos IA':<12} {'Nodos':<15} {'Prof.':<8} {'Tiempo':<10}")
    print("-"*100)
    
    for r in resultados_pesos:
        for game in r["results"]:
            wins = 1 if game["winner"] == 1 else 0
            losses = 1 if game["winner"] == 2 else 0
            draws = 1 if game["winner"] == 0 else 0
            vde = f"{wins}-{losses}-{draws}"
            puntos = game["scores"][0]
            print(f"{r['config_name']:<30} {r['opponent']:<15} {vde:<15} {puntos:<12} {game['nodes_expanded']:<15} {game['max_depth']:<8.1f} {game['execution_time']:<10.2f}")
    
    # TABLA 2: Heurísticas vs Todos los oponentes
    print("\n" + "-"*100)
    print("TABLA 2: DIFERENTES HEURÍSTICAS VS TODOS LOS OPONENTES")
    print("-"*100)
    print(f"{'Configuración':<40} {'Oponente':<15} {'V-D-E':<15} {'Puntos IA':<12} {'Nodos':<15} {'Prof.':<8} {'Tiempo':<10}")
    print("-"*100)
    
    for r in resultados_heuristicas:
        for game in r["results"]:
            wins = 1 if game["winner"] == 1 else 0
            losses = 1 if game["winner"] == 2 else 0
            draws = 1 if game["winner"] == 0 else 0
            vde = f"{wins}-{losses}-{draws}"
            puntos = game["scores"][0]
            print(f"{r['config_name']:<40} {r['opponent']:<15} {vde:<15} {puntos:<12} {game['nodes_expanded']:<15} {game['max_depth']:<8.1f} {game['execution_time']:<10.2f}")
    
    # TABLA 3: Tiempos vs Todos los oponentes
    print("\n" + "-"*100)
    print("TABLA 3: DIFERENTES TIEMPOS VS TODOS LOS OPONENTES")
    print("-"*100)
    print(f"{'Configuración':<20} {'Oponente':<15} {'V-D-E':<15} {'Puntos IA':<12} {'Nodos':<15} {'Prof.':<8} {'Tiempo':<10}")
    print("-"*100)
    
    for r in resultados_tiempos:
        for game in r["results"]:
            wins = 1 if game["winner"] == 1 else 0
            losses = 1 if game["winner"] == 2 else 0
            draws = 1 if game["winner"] == 0 else 0
            vde = f"{wins}-{losses}-{draws}"
            puntos = game["scores"][0]
            print(f"{r['config_name']:<20} {r['opponent']:<15} {vde:<15} {puntos:<12} {game['nodes_expanded']:<15} {game['max_depth']:<8.1f} {game['execution_time']:<10.2f}")
    
    # Resumen estadístico por configuración
    print("\n" + "="*100)
    print("RESUMEN ESTADÍSTICO POR CONFIGURACIÓN")
    print("="*100)
    
    configs_resumen = {}
    for r in benchmark_results:
        key = f"{r['config_name']} vs {r['opponent']}"
        wins = sum(1 for game in r["results"] if game["winner"] == 1)
        losses = sum(1 for game in r["results"] if game["winner"] == 2)
        draws = sum(1 for game in r["results"] if game["winner"] == 0)
        avg_nodes = sum(game["nodes_expanded"] for game in r["results"]) / len(r["results"])
        avg_depth = sum(game["max_depth"] for game in r["results"]) / len(r["results"])
        avg_time = sum(game["execution_time"] for game in r["results"]) / len(r["results"])
        avg_puntos = sum(game["scores"][0] for game in r["results"]) / len(r["results"])
        
        configs_resumen[key] = {
            "wins": wins, "losses": losses, "draws": draws,
            "avg_nodes": avg_nodes, "avg_depth": avg_depth,
            "avg_time": avg_time, "avg_puntos": avg_puntos
        }
    
    print(f"\n{'Configuración vs Oponente':<50} {'V-D-E':<15} {'Puntos':<10} {'Nodos':<15} {'Prof.':<8} {'Tiempo':<10}")
    print("-"*100)
    
    for key, stats in configs_resumen.items():
        vde = f"{stats['wins']}-{stats['losses']}-{stats['draws']}"
        print(f"{key:<50} {vde:<15} {stats['avg_puntos']:<10.1f} {stats['avg_nodes']:<15.0f} {stats['avg_depth']:<8.1f} {stats['avg_time']:<10.2f}")

# Menù Principal 
def main_menu():
    while True:
        print("\n" + "="*50)
        print("COLLAPSI - PROYECTO IA")
        print("="*50)
        print("1. Jugar partida simple (Humano vs IA - 3s)")
        print("2. Configurar y jugar")
        print("3. Ejecutar benchmark completo")
        print("4. Salir")
        
        option = input("\nSelecciona una opción: ")
        
        if option == "1":
            # Partida simple: Humano vs IA por defecto
            print("\n--- PARTIDA SIMPLE: HUMANO VS IA ---")
            print("IA con tiempo de 3 segundos por movimiento")
            config = [
                {"type": "human"},
                {"type": "ai", "max_time": 3}
            ]
            play_game(config, num_games=1)
            
        elif option == "2":
            # Configuración personalizada
            print("\n--- CONFIGURACIÓN DE PARTIDA ---")
            
            players_config = []
            
            for i in range(2):
                print(f"\nConfiguración del Jugador {i+1}:")
                print("1. Humano")
                print("2. IA (Minimax)")
                print("3. Aleatorio")
                print("4. Greedy")
                print("5. Peor jugador")
                
                choice = input("Selecciona tipo: ")
                
                if choice == "1":
                    players_config.append({"type": "human"})
                elif choice == "2":
                    max_time = float(input("Tiempo máximo para pensar (segundos): "))
                    
                    # Preguntar si quiere configurar pesos personalizados
                    print("\n¿Deseas configurar pesos personalizados?")
                    print("1. Usar pesos por defecto")
                    print("2. Configurar pesos personalizados")
                    
                    weight_choice = input("Selecciona opción: ")
                    
                    if weight_choice == "2":
                        print("\nConfiguración de pesos (0-3):")
                        movilidad = float(input("Peso para movilidad: ") or "1.0")
                        centralidad = float(input("Peso para centralidad: ") or "1.0")
                        distancia = float(input("Peso para distancia: ") or "1.0")
                        espacios = float(input("Peso para espacios ocupados: ") or "1.0")
                        potencial = float(input("Peso para potencial futuro: ") or "1.0")
                        
                        weights = {
                            'movilidad': movilidad,
                            'centralidad': centralidad,
                            'distancia_oponente': distancia,
                            'espacios_ocupados': espacios,
                            'potencial_futuro': potencial
                        }
                        players_config.append({"type": "ai", "max_time": max_time, "weights": weights})
                    else:
                        players_config.append({"type": "ai", "max_time": max_time})
                        
                elif choice == "3":
                    players_config.append({"type": "random"})
                elif choice == "4":
                    players_config.append({"type": "greedy"})
                elif choice == "5":
                    players_config.append({"type": "worst"})
            
            num_games = int(input("\nNúmero de partidas a jugar: "))
            play_game(players_config, num_games=num_games)
            
        elif option == "3":
            # Ejecutar benchmark completo
            run_benchmark()
            
        elif option == "4":
            print("¡Hasta luego!")
            break

if __name__ == "__main__":
    main_menu()