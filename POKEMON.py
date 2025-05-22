 
import os
import pygame
import tkinter as tk
from random import randint, choice, random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640, 576
TILE_SIZE = 32
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

class Pokemon:
    def __init__(self, name, level, type, max_hp, attack, defense, moves):
        self.name = name
        self.level = level
        self.type = type
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.moves = moves

class Move:
    def __init__(self, name, power, accuracy, type):
        self.name = name
        self.power = power
        self.accuracy = accuracy
        self.type = type

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.direction = 'down'
        self.speed = 5
        self.pokemon = []
        self.items = {'Poke Ball': 5, 'Potion': 3}
        self.money = 1000

class GameEngine:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.in_battle = False
        self.in_menu = False
        self.current_opponent = None
        self.encounter_rate = 0.1
        self.npcs = [
            {'name': 'Professor Oak', 'x': 100, 'y': 100, 'dialog': [
                "Hello there! Welcome to the world of Pokémon!",
                "My name is Oak! People call me the Pokémon Professor!"
            ]}
        ]
        
        # Initialize some Pokémon and moves
        self.pokemon_db = {
            'Pikachu': {'type': 'Electric', 'base_hp': 35, 'base_attack': 55, 'base_defense': 40},
            'Charmander': {'type': 'Fire', 'base_hp': 39, 'base_attack': 52, 'base_defense': 43}
        }
        
        self.move_db = {
            'Thunder Shock': {'power': 40, 'accuracy': 100, 'type': 'Electric'},
            'Ember': {'power': 40, 'accuracy': 100, 'type': 'Fire'}
        }

    def create_wild_pokemon(self):
        name = choice(list(self.pokemon_db.keys()))
        level = randint(2, 5)
        stats = self.pokemon_db[name]
        moves = [Move('Tackle', 40, 100, 'Normal')]
        if name in self.move_db:
            moves.append(Move(list(self.move_db.keys())[0], 
                           self.move_db[list(self.move_db.keys())[0]]['power'],
                           self.move_db[list(self.move_db.keys())[0]]['accuracy'],
                           self.move_db[list(self.move_db.keys())[0]]['type']))
        return Pokemon(
            name=name,
            level=level,
            type=stats['type'],
            max_hp=stats['base_hp'] + level,
            attack=stats['base_attack'] + level,
            defense=stats['base_defense'] + level,
            moves=moves
        )

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if not self.in_battle and not self.in_menu:
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

            # Check for random encounters
            if random() < self.encounter_rate:
                self.start_battle()

    def start_battle(self):
        self.in_battle = True
        self.current_opponent = self.create_wild_pokemon()
        print(f"Wild {self.current_opponent.name} appeared!")

    def battle_turn(self, player_move):
        # Simple damage calculation
        damage = (player_move.power * self.player.pokemon[0].attack) // self.current_opponent.defense
        self.current_opponent.current_hp -= damage
        print(f"{self.player.pokemon[0].name} used {player_move.name}!")
        print(f"It did {damage} damage!")

        if self.current_opponent.current_hp <= 0:
            print(f"Wild {self.current_opponent.name} fainted!")
            self.in_battle = False
            return

        # Opponent's turn
        opponent_move = choice(self.current_opponent.moves)
        damage = (opponent_move.power * self.current_opponent.attack) // self.player.pokemon[0].defense
        self.player.pokemon[0].current_hp -= damage
        print(f"Wild {self.current_opponent.name} used {opponent_move.name}!")
        print(f"It did {damage} damage!")

        if self.player.pokemon[0].current_hp <= 0:
            print(f"{self.player.pokemon[0].name} fainted!")
            self.in_battle = False

    def draw_battle(self):
        self.screen.fill(WHITE)
        # Draw player Pokémon
        pygame.draw.rect(self.screen, RED, (50, HEIGHT-150, 100, 100))
        # Draw opponent Pokémon
        pygame.draw.rect(self.screen, BLACK, (WIDTH-150, 50, 100, 100))
        
        # Draw battle menu
        menu_rect = pygame.Rect(0, HEIGHT-100, WIDTH, 100)
        pygame.draw.rect(self.screen, BLACK, menu_rect)
        
        font = pygame.font.SysFont('monospace', 24)
        text = font.render(f"Wild {self.current_opponent.name} Lv{self.current_opponent.level}", True, WHITE)
        self.screen.blit(text, (10, 10))
        
        # Draw battle options
        options = ["Fight", "Bag", "Pokemon", "Run"]
        for i, option in enumerate(options):
            text = font.render(option, True, WHITE)
            self.screen.blit(text, (50 + i*150, HEIGHT-80))

    def draw_overworld(self):
        self.screen.fill(BLACK)
        # Draw simple grid
        for x in range(0, WIDTH, TILE_SIZE):
            for y in range(0, HEIGHT, TILE_SIZE):
                pygame.draw.rect(self.screen, (50, 50, 50), (x, y, TILE_SIZE-1, TILE_SIZE-1))
        
        # Draw player
        pygame.draw.rect(self.screen, RED, (self.player.x, self.player.y, 20, 20))
        
        # Draw NPCs
        for npc in self.npcs:
            pygame.draw.rect(self.screen, WHITE, (npc['x'], npc['y'], 20, 20))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif self.in_battle:
                        if event.key == pygame.K_1:
                            self.battle_turn(self.player.pokemon[0].moves[0])
                        elif event.key == pygame.K_4:
                            self.in_battle = False

            self.handle_input()
            
            if self.in_battle:
                self.draw_battle()
            else:
                self.draw_overworld()

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()

# Initialize the game
if __name__ == "__main__":
    engine = GameEngine()
    
    # Add starter Pokémon
    starter = engine.create_wild_pokemon()
    starter.name = "Charmander"
    starter.level = 5
    engine.player.pokemon.append(starter)
    
    engine.run()
 
