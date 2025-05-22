   
  
import pygame
from random import randint, choice, random

# --- Initialization ---
pygame.init()

# --- Screen & Game Boy Settings ---
WIDTH, HEIGHT = 640, 576          # Window size (scaled view)
GBP_WIDTH, GBP_HEIGHT = 160, 144  # Native Game Boy resolution
SCALE_X, SCALE_Y = WIDTH // GBP_WIDTH, HEIGHT // GBP_HEIGHT
TILE_SIZE = 16

# --- Palette (DMG-style) ---
GBP_COLORS = {
    'white': (255, 255, 255),
    'light_gray': (180, 180, 180),
    'dark_gray': (64, 64, 64),
    'black': (0, 0, 0),
}

# -----------------------------------------------------------------------------
#  Core Data Classes
# -----------------------------------------------------------------------------

class Pokemon:
    def __init__(self, name, level, type_, max_hp, attack, defense, moves):
        self.name = name
        self.level = level
        self.type = type_
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.moves = moves


class Move:
    def __init__(self, name, power, accuracy, type_):
        self.name = name
        self.power = power
        self.accuracy = accuracy
        self.type = type_


class Player:
    def __init__(self):
        self.x = GBP_WIDTH // 2
        self.y = GBP_HEIGHT // 2
        self.direction = 'down'
        self.speed = 1  # 1 pixel per frame at native res
        self.pokemon = []
        self.items = {'Poke Ball': 5, 'Potion': 3}
        self.money = 1000


# -----------------------------------------------------------------------------
#  Game Engine
# -----------------------------------------------------------------------------

class GameEngine:
    def __init__(self):
        # Surfaces
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.viewport = pygame.Surface((GBP_WIDTH, GBP_HEIGHT))
        pygame.display.set_caption("Pokémon-Like Demo")

        # Timing
        self.clock = pygame.time.Clock()

        # Entities & State
        self.player = Player()
        self.in_battle = False
        self.in_menu = False
        self.current_opponent: Pokemon | None = None
        self.encounter_rate = 0.1  # 10 % chance per movement frame

        # Simple NPC list
        self.npcs = [
            {
                'name': 'Professor Oak',
                'x': 10,
                'y': 10,
                'dialog': [
                    "Hello there! Welcome to the world of Pokémon!",
                    "My name is Oak! People call me the Pokémon Professor!",
                ],
            }
        ]

        # --- Databases --------------------------------------------------------
        self.pokemon_db = {
            'Pikachu':  {'type': 'Electric', 'base_hp': 35, 'base_attack': 55, 'base_defense': 40},
            'Charmander': {'type': 'Fire',    'base_hp': 39, 'base_attack': 52, 'base_defense': 43},
        }

        self.move_db = {
            'Thunder Shock': {'power': 40, 'accuracy': 100, 'type': 'Electric'},
            'Ember':          {'power': 40, 'accuracy': 100, 'type': 'Fire'},
        }

    # -------------------------------------------------------------------------
    #  Utility Helpers
    # -------------------------------------------------------------------------

    def create_wild_pokemon(self) -> Pokemon:
        name = choice(list(self.pokemon_db.keys()))
        level = randint(2, 5)
        stats = self.pokemon_db[name]

        # Base moveset always has Tackle; add signature move if available.
        moves = [Move('Tackle', 40, 100, 'Normal')]
        sig = next((m for m in self.move_db if m.lower().startswith(name.lower()[0])), None)
        if sig:
            data = self.move_db[sig]
            moves.append(Move(sig, data['power'], data['accuracy'], data['type']))

        return Pokemon(
            name=name,
            level=level,
            type_=stats['type'],
            max_hp=stats['base_hp'] + level,
            attack=stats['base_attack'] + level,
            defense=stats['base_defense'] + level,
            moves=moves,
        )

    # -------------------------------------------------------------------------
    #  Input Handling
    # -------------------------------------------------------------------------

    def handle_overworld_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.x -= self.player.speed
            self.player.direction = 'left'
        if keys[pygame.K_RIGHT]:
            self.player.x += self.player.speed
            self.player.direction = 'right'
        if keys[pygame.K_UP]:
            self.player.y -= self.player.speed
            self.player.direction = 'up'
        if keys[pygame.K_DOWN]:
            self.player.y += self.player.speed
            self.player.direction = 'down'

        # Random encounter check
        if random() < self.encounter_rate:
            self.start_battle()

    # -------------------------------------------------------------------------
    #  Battle Logic
    # -------------------------------------------------------------------------

    def start_battle(self):
        self.in_battle = True
        self.current_opponent = self.create_wild_pokemon()
        print(f"Wild {self.current_opponent.name} appeared!")

    def battle_turn(self, player_move: Move):
        # Player attacks
        damage = max(1, (player_move.power * self.player.pokemon[0].attack) // self.current_opponent.defense)
        self.current_opponent.current_hp -= damage
        print(f"{self.player.pokemon[0].name} used {player_move.name}! ({damage} DMG)")

        if self.current_opponent.current_hp <= 0:
            print(f"Wild {self.current_opponent.name} fainted!")
            self.in_battle = False
            return

        # Opponent counter-attacks
        opponent_move = choice(self.current_opponent.moves)
        damage = max(1, (opponent_move.power * self.current_opponent.attack) // self.player.pokemon[0].defense)
        self.player.pokemon[0].current_hp -= damage
        print(f"Wild {self.current_opponent.name} used {opponent_move.name}! ({damage} DMG)")

        if self.player.pokemon[0].current_hp <= 0:
            print(f"{self.player.pokemon[0].name} fainted!")
            self.in_battle = False

    # -------------------------------------------------------------------------
    #  Rendering
    # -------------------------------------------------------------------------

    def draw_overworld(self):
        self.viewport.fill(GBP_COLORS['black'])

        # Grid (debug visual)
        for x in range(0, GBP_WIDTH, TILE_SIZE):
            for y in range(0, GBP_HEIGHT, TILE_SIZE):
                pygame.draw.rect(self.viewport, GBP_COLORS['dark_gray'], (x, y, TILE_SIZE-1, TILE_SIZE-1), 1)

        # Player sprite (placeholder)
        pygame.draw.rect(self.viewport, GBP_COLORS['white'], (self.player.x, self.player.y, 8, 8))

        # NPCs
        for npc in self.npcs:
            pygame.draw.rect(self.viewport, GBP_COLORS['light_gray'], (npc['x'], npc['y'], 8, 8))

    def draw_battle(self):
        self.viewport.fill(GBP_COLORS['black'])

        # Player Pokémon sprite (placeholder box)
        pygame.draw.rect(self.viewport, GBP_COLORS['white'], (20, 96, 32, 32), 0)
        pygame.draw.rect(self.viewport, GBP_COLORS['dark_gray'], (20, 96, 32, 32), 1)

        # Opponent Pokémon sprite
        pygame.draw.rect(self.viewport, GBP_COLORS['white'], (GBP_WIDTH - 52, 16, 32, 32), 0)
        pygame.draw.rect(self.viewport, GBP_COLORS['dark_gray'], (GBP_WIDTH - 52, 16, 32, 32), 1)

        # Simple text (name + level)
        font = pygame.font.SysFont('monospace', 8)
        text = font.render(f"Wild {self.current_opponent.name} Lv{self.current_opponent.level}", False, GBP_COLORS['white'])
        self.viewport.blit(text, (4, 4))

        # Battle options
        options = ["1: Fight", "2: Bag", "3: Pokémon", "4: Run"]
        for i, option in enumerate(options):
            txt = font.render(option, False, GBP_COLORS['white'])
            self.viewport.blit(txt, (4, GBP_HEIGHT - 32 + i * 8))

    # -------------------------------------------------------------------------
    #  Main Loop
    # -------------------------------------------------------------------------

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif self.in_battle and event.key == pygame.K_1:
                        self.battle_turn(self.player.pokemon[0].moves[0])
                    elif self.in_battle and event.key == pygame.K_4:
                        self.in_battle = False

            if not self.in_battle and not self.in_menu:
                self.handle_overworld_input()

            # Draw scene
            if self.in_battle:
                self.draw_battle()
            else:
                self.draw_overworld()

            # Blit viewport to window, scaled
            scaled = pygame.transform.scale(self.viewport, (WIDTH, HEIGHT))
            self.window.blit(scaled, (0, 0))
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()


# -----------------------------------------------------------------------------
#  Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    engine = GameEngine()

    # Give player a starter (Charmander)
    starter = engine.create_wild_pokemon()
    starter.name = "Charmander"
    starter.level = 5
    engine.player.pokemon.append(starter)

    engine.run()
