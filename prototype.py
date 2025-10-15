#!/usr/bin/env python3
"""
Pokemon Terminal - Esqueleto de jogo em terminal
Funcionalidades:
- Menu principal
- Gerenciamento de pokemons do jogador (ver, editar, curar, adicionar manual)
- Pokédex (espécies conhecidas)
- Bag: ver itens, adicionar/remover (manual)
- Exploração: escolher região/dificuldade, encontrar pokemons selvagens
- Batalha simples por turnos (Atacar / Usar Poção / Tentar Capturar / Fugir)
- Salvar / carregar em JSON
"""

import json
import random
import os
import time
from typing import List, Dict

SAVE_FILE = "save_game.json"

# -------------------------
# Dados básicos / compendium
# -------------------------
# Pequeno compêndio de espécies para demo
SPECIES_DB = {
    "Pikachu": {"type": "Electric", "base_hp": 60, "base_atk": 18, "base_def": 8},
    "Charmander": {"type": "Fire", "base_hp": 55, "base_atk": 20, "base_def": 6},
    "Squirtle": {"type": "Water", "base_hp": 58, "base_atk": 16, "base_def": 10},
    "Bulbasaur": {"type": "Grass", "base_hp": 62, "base_atk": 15, "base_def": 9},
    "Rattata": {"type": "Normal", "base_hp": 40, "base_atk": 10, "base_def": 6},
    "Pidgey": {"type": "Flying", "base_hp": 45, "base_atk": 12, "base_def": 7},
}

# -------------------------
# Classes principais
# -------------------------
class Pokemon:
    def __init__(self, species: str, level: int = 5, nickname: str = None):
        self.species = species
        self.level = max(1, level)
        self.nickname = nickname or species
        # derive stats from species base values and level (simple formula)
        spec = SPECIES_DB.get(species, {})
        base_hp = spec.get("base_hp", 50)
        base_atk = spec.get("base_atk", 10)
        base_def = spec.get("base_def", 8)
        self.hp_max = int(base_hp + (self.level - 1) * 3)
        self.hp = self.hp_max
        self.atk = int(base_atk + (self.level - 1) * 1.5)
        self.defense = int(base_def + (self.level - 1) * 1.2)
        self.type = spec.get("type", "Normal")

    def to_dict(self):
        return {
            "species": self.species,
            "level": self.level,
            "nickname": self.nickname,
            "hp": self.hp,
            "hp_max": self.hp_max,
            "atk": self.atk,
            "defense": self.defense,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, d):
        p = cls(d["species"], d.get("level", 5), d.get("nickname"))
        # override stats with saved values
        p.hp = d.get("hp", p.hp)
        p.hp_max = d.get("hp_max", p.hp_max)
        p.atk = d.get("atk", p.atk)
        p.defense = d.get("defense", p.defense)
        p.type = d.get("type", p.type)
        return p

    def is_fainted(self):
        return self.hp <= 0

    def heal_full(self):
        self.hp = self.hp_max

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def attack_target(self, target) -> int:
        # dano simples: atac - (def*0.3) +- aleatório
        base = self.atk - int(target.defense * 0.3)
        dano = max(1, int(base + random.randint(-3, 3)))
        target.take_damage(dano)
        return dano

class Trainer:
    def __init__(self, name="Player"):
        self.name = name
        self.pokemons: List[Pokemon] = []
        self.items: Dict[str, int] = {"Potion": 3, "Pokeball": 5}
        self.money = 500
        self.pokedex = set()  # espécies já vistas
        self.wins = 0

    def to_dict(self):
        return {
            "name": self.name,
            "pokemons": [p.to_dict() for p in self.pokemons],
            "items": self.items,
            "money": self.money,
            "pokedex": list(self.pokedex),
            "wins": self.wins,
        }

    @classmethod
    def from_dict(cls, d):
        t = cls(d.get("name", "Player"))
        t.pokemons = [Pokemon.from_dict(p) for p in d.get("pokemons", [])]
        t.items = d.get("items", {"Potion": 3, "Pokeball": 5})
        t.money = d.get("money", 0)
        t.pokedex = set(d.get("pokedex", []))
        t.wins = d.get("wins", 0)
        return t

# -------------------------
# Save / Load
# -------------------------
def save_game(trainer: Trainer, filename=SAVE_FILE):
    data = {"trainer": trainer.to_dict()}
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print("Jogo salvo.")

def load_game(filename=SAVE_FILE) -> Trainer:
    if not os.path.exists(filename):
        return Trainer()
    with open(filename, "r") as f:
        data = json.load(f)
    return Trainer.from_dict(data.get("trainer", {}))

# -------------------------
# Utilitários UI
# -------------------------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def press_enter():
    input("\n[Enter para continuar]")

def hp_bar(p: Pokemon, length=20):
    filled = int((p.hp / p.hp_max) * length) if p.hp_max else 0
    return "[" + "█" * filled + " " * (length - filled) + f"] {p.hp}/{p.hp_max}"

# -------------------------
# Menus principais
# -------------------------
def menu_main(trainer: Trainer):
    while True:
        clear_screen()
        print("=== POKÉMON TERMINAL BATTLE ===")
        print(f"Treinador: {trainer.name} | Money: ${trainer.money} | Wins: {trainer.wins}")
        print("1) Pokémons")
        print("2) Pokédex")
        print("3) Bag")
        print("4) Exploração")
        print("5) Perfil")
        print("6) Centro Pokémon (cura)")
        print("0) Salvar e Sair")
        choice = input("> ").strip()
        if choice == "1":
            menu_pokemons(trainer)
        elif choice == "2":
            menu_pokedex(trainer)
        elif choice == "3":
            menu_bag(trainer)
        elif choice == "4":
            menu_exploracao(trainer)
        elif choice == "5":
            menu_perfil(trainer)
        elif choice == "6":
            centro_pokemon(trainer)
        elif choice == "0":
            save_game(trainer)
            print("Saindo... até a próxima!")
            break
        else:
            print("Opção inválida.")
            press_enter()

# -------------------------
# Pokemons menu
# -------------------------
def menu_pokemons(trainer: Trainer):
    while True:
        clear_screen()
        print("=== POKÉMONS ===")
        if not trainer.pokemons:
            print("Você não possui pokémons ainda.")
        else:
            for i, p in enumerate(trainer.pokemons):
                print(f"{i+1}) {p.nickname} ({p.species}) Lv{p.level} | {hp_bar(p)}")
        print("\nA) Adicionar manualmente (debug)")
        print("E) Editar/Curar um pokémon")
        print("R) Remover pokémon")
        print("V) Voltar")
        choice = input("> ").strip().lower()
        if choice == "a":
            add_pokemon_manual(trainer)
        elif choice == "e":
            edit_pokemon(trainer)
        elif choice == "r":
            remove_pokemon(trainer)
        elif choice == "v":
            break
        else:
            print("Opção inválida.")
            press_enter()

def add_pokemon_manual(trainer: Trainer):
    print("Nome da espécie (ex: Pikachu):")
    sp = input("> ").strip()
    if sp not in SPECIES_DB:
        print("Espécie não encontrada no compêndio. Deseja adicioná-la mesmo assim? (s/N)")
        if input("> ").strip().lower() != "s":
            return
    lvl = int(input("Nível (padrão 5): ") or 5)
    nick = input("Apelido (opcional): ").strip() or None
    p = Pokemon(sp, lvl, nick)
    trainer.pokemons.append(p)
    trainer.pokedex.add(sp)
    print(f"{p.nickname} adicionado ao time!")
    press_enter()

def edit_pokemon(trainer: Trainer):
    if not trainer.pokemons:
        print("Sem pokémons.")
        press_enter(); return
    for i, p in enumerate(trainer.pokemons):
        print(f"{i+1}) {p.nickname} ({p.species}) Lv{p.level} | HP: {p.hp}/{p.hp_max}")
    idx = int(input("Escolha o número: ") or 0) - 1
    if idx < 0 or idx >= len(trainer.pokemons):
        print("Índice inválido."); press_enter(); return
    p = trainer.pokemons[idx]
    print("1) Curar totalmente")
    print("2) Aumentar nível")
    print("3) Trocar apelido")
    print("4) Voltar")
    c = input("> ").strip()
    if c == "1":
        p.heal_full()
        print(f"{p.nickname} curado.")
    elif c == "2":
        add = int(input("Quantos níveis aumentar? ") or 1)
        p.level += add
        # recalcular stats (simples)
        spec = SPECIES_DB.get(p.species, {})
        p.hp_max = int(spec.get("base_hp", 50) + (p.level - 1) * 3)
        p.atk = int(spec.get("base_atk", 10) + (p.level - 1) * 1.5)
        p.defense = int(spec.get("base_def", 8) + (p.level - 1) * 1.2)
        p.hp = p.hp_max
        print(f"{p.nickname} agora é Lv{p.level}.")
    elif c == "3":
        new = input("Novo apelido: ").strip()
        if new:
            p.nickname = new
            print("Apelido alterado.")
    press_enter()

def remove_pokemon(trainer: Trainer):
    if not trainer.pokemons:
        print("Sem pokémons.")
        press_enter(); return
    for i, p in enumerate(trainer.pokemons):
        print(f"{i+1}) {p.nickname} ({p.species})")
    idx = int(input("Escolha o nº para remover: ") or 0) - 1
    if 0 <= idx < len(trainer.pokemons):
        removed = trainer.pokemons.pop(idx)
        print(f"{removed.nickname} removido.")
    else:
        print("Índice inválido.")
    press_enter()

# -------------------------
# Pokédex menu
# -------------------------
def menu_pokedex(trainer: Trainer):
    clear_screen()
    print("=== POKEDEX ===")
    known = sorted(trainer.pokedex)
    if not known:
        print("Você não registrou nenhuma espécie ainda.")
    else:
        for s in known:
            data = SPECIES_DB.get(s, {})
            print(f"- {s} | Tipo: {data.get('type', '?')} | HP base: {data.get('base_hp','?')}")
    press_enter()

# -------------------------
# Bag menu
# -------------------------
def menu_bag(trainer: Trainer):
    while True:
        clear_screen()
        print("=== BAG ===")
        if not trainer.items:
            print("Sem itens.")
        else:
            for item, qty in trainer.items.items():
                print(f"- {item}: {qty}")
        print("\nA) Adicionar item manualmente")
        print("U) Usar item")
        print("V) Voltar")
        c = input("> ").strip().lower()
        if c == "a":
            name = input("Nome do item: ").strip()
            qty = int(input("Quantidade: ") or 1)
            trainer.items[name] = trainer.items.get(name, 0) + qty
            print("Item adicionado.")
            press_enter()
        elif c == "u":
            usar_item(trainer)
        elif c == "v":
            break
        else:
            print("Inválido."); press_enter()

def usar_item(trainer: Trainer):
    if not trainer.items:
        print("Sem itens.")
        press_enter(); return
    print("Escolha item:")
    items = list(trainer.items.items())
    for i, (it, qty) in enumerate(items):
        print(f"{i+1}) {it} x{qty}")
    idx = int(input("> ") or 0) - 1
    if idx < 0 or idx >= len(items):
        print("Índice inválido."); press_enter(); return
    item, qty = items[idx]
    # efeito simples: Potion cura o primeiro pokémon não desmaiado do time
    if item.lower() == "potion":
        target = next((p for p in trainer.pokemons if not p.is_fainted()), None)
        if not target:
            print("Nenhum pokémon apto para usar a poção.")
        else:
            heal = min(20, target.hp_max - target.hp)
            target.hp += heal
            print(f"{target.nickname} recuperou {heal} HP.")
            trainer.items[item] -= 1
            if trainer.items[item] <= 0:
                del trainer.items[item]
    else:
        print("Item sem efeito implementado.")
    press_enter()

# -------------------------
# Exploração / encontros
# -------------------------
REGIONS = {
    "Route 1": {"possible": ["Rattata", "Pidgey"], "lvl_range": (3, 6)},
    "Forest": {"possible": ["Pidgey", "Bulbasaur", "Squirtle"], "lvl_range": (4, 8)},
    "Volcano": {"possible": ["Charmander"], "lvl_range": (6, 12)},
}

def menu_exploracao(trainer: Trainer):
    while True:
        clear_screen()
        print("=== EXPLORAÇÃO ===")
        print("Regiões disponíveis:")
        for i, (name, info) in enumerate(REGIONS.items()):
            print(f"{i+1}) {name} (Lv {info['lvl_range'][0]}-{info['lvl_range'][1]})")
        print("V) Voltar")
        c = input("> ").strip().lower()
        if c == "v":
            break
        try:
            idx = int(c) - 1
            region = list(REGIONS.keys())[idx]
        except Exception:
            print("Opção inválida."); press_enter(); continue
        explore_region(trainer, region)

def explore_region(trainer: Trainer, region_name: str):
    info = REGIONS[region_name]
    print(f"Você explora a região: {region_name}...")
    # gerar encontro aleatório
    if random.random() < 0.7:  # chance de encontro
        species = random.choice(info["possible"])
        lvl = random.randint(info["lvl_range"][0], info["lvl_range"][1])
        wild = Pokemon(species, lvl)
        trainer.pokedex.add(species)
        print(f"Um {wild.species} selvagem apareceu! (Lv{wild.level})")
        press_enter()
        # batalha selvagem
        battle_result = battle_wild(trainer, wild)
        if battle_result == "caught":
            print(f"Você capturou {wild.species}!")
            trainer.pokemons.append(wild)
        elif battle_result == "fled":
            print("Você fugiu do encontro.")
        elif battle_result == "win":
            print(f"Você venceu e derrotou o {wild.species}!")
            trainer.money += 20
            trainer.wins += 1
        elif battle_result == "lose":
            print("Todos seus pokémons desmaiaram. Você foi curado no Centro automaticamente.")
            for p in trainer.pokemons:
                p.heal_full()
        press_enter()
    else:
        print("Nenhum encontro desta vez.")
        press_enter()

# -------------------------
# Batalha (simples)
# -------------------------
def choose_active_pokemon(trainer: Trainer) -> int:
    available = [p for p in trainer.pokemons if not p.is_fainted()]
    if not available:
        return -1
    print("Escolha seu pokémon ativo:")
    for i, p in enumerate(trainer.pokemons):
        status = "(Fainted)" if p.is_fainted() else ""
        print(f"{i+1}) {p.nickname} ({p.species}) Lv{p.level} {status}")
    idx = int(input("> ") or 1) - 1
    if idx < 0 or idx >= len(trainer.pokemons) or trainer.pokemons[idx].is_fainted():
        print("Escolha inválida. Usando o primeiro apto.")
        for i, p in enumerate(trainer.pokemons):
            if not p.is_fainted():
                return i
        return -1
    return idx

def battle_wild(trainer: Trainer, wild: Pokemon):
    if not trainer.pokemons:
        print("Você não tem pokémons para lutar!")
        return "fled"
    active_idx = choose_active_pokemon(trainer)
    if active_idx == -1:
        print("Sem pokémons aptos.")
        return "fled"
    player_p = trainer.pokemons[active_idx]
    opponent = wild

    while True:
        clear_screen()
        print(f"Você: {player_p.nickname} Lv{player_p.level} | {hp_bar(player_p)}")
        print(f"Selvagem: {opponent.species} Lv{opponent.level} | {hp_bar(opponent)}")
        print("\nAções:")
        print("1) Atacar")
        print("2) Usar Poção")
        print("3) Tentar Capturar")
        print("4) Fugir")
        choice = input("> ").strip()
        if choice == "1":
            dano = player_p.attack_target(opponent)
            print(f"{player_p.nickname} causou {dano} de dano!")
        elif choice == "2":
            if trainer.items.get("Potion", 0) > 0:
                heal = min(20, player_p.hp_max - player_p.hp)
                player_p.hp += heal
                trainer.items["Potion"] -= 1
                if trainer.items["Potion"] <= 0:
                    del trainer.items["Potion"]
                print(f"Usou uma Poção em {player_p.nickname} (+{heal} HP).")
            else:
                print("Sem Poções.")
        elif choice == "3":
            # chance simples: base 40% + (nivel pokeball effect)
            balls = trainer.items.get("Pokeball", 0)
            if balls <= 0:
                print("Sem Pokébolas.")
            else:
                trainer.items["Pokeball"] -= 1
                catch_chance = 0.4 + (0.02 * (player_p.level - opponent.level))
                catch_chance = max(0.05, min(0.95, catch_chance))
                roll = random.random()
                if roll < catch_chance:
                    return "caught"
                else:
                    print("A captura falhou!")
        elif choice == "4":
            if random.random() < 0.7:
                return "fled"
            else:
                print("Não conseguiu fugir!")
        else:
            print("Inválido.")

        time.sleep(0.8)
        # checar se o selvagem desmaiou
        if opponent.is_fainted():
            return "win"
        # turno do selvagem
        print(f"\n{opponent.species} ataca!")
        dano = opponent.attack_target(player_p)
        print(f"Causou {dano} de dano em {player_p.nickname}!")
        if player_p.is_fainted():
            print(f"{player_p.nickname} desmaiou!")
            # procurar outro pokémon apto automaticamente
            idx_next = next((i for i, pk in enumerate(trainer.pokemons) if not pk.is_fainted()), -1)
            if idx_next == -1:
                return "lose"
            else:
                print("Escolha outro pokémon para continuar (automatico).")
                player_p = trainer.pokemons[idx_next]
        press_enter()

# -------------------------
# Perfil / Centro
# -------------------------
def menu_perfil(trainer: Trainer):
    clear_screen()
    print("=== PERFIL ===")
    print(f"Nome: {trainer.name}")
    print(f"Dinheiro: ${trainer.money}")
    print(f"Vitórias: {trainer.wins}")
    print(f"Pokédex registrada: {len(trainer.pokedex)} espécies")
    print("Pokémons no time:", ", ".join([p.nickname for p in trainer.pokemons]) or "Nenhum")
    press_enter()

def centro_pokemon(trainer: Trainer):
    print("Bem-vindo ao Centro Pokémon! Todos os seus pokémons foram curados gratuitamente.")
    for p in trainer.pokemons:
        p.heal_full()
    press_enter()

# -------------------------
# Inicialização principal
# -------------------------
def main():
    trainer = load_game()
    if not trainer.pokemons:
        # primeiro jogo: dar um pokemon inicial
        print("Bem-vindo! Escolha seu Pokémon inicial:")
        inicial = ["Pikachu", "Charmander", "Squirtle"]
        for i, s in enumerate(inicial):
            print(f"{i+1}) {s}")
        c = int(input("> ") or 1) - 1
        choice = inicial[c] if 0 <= c < len(inicial) else inicial[0]
        p = Pokemon(choice, level=5)
        trainer.pokemons.append(p)
        trainer.pokedex.add(choice)
        print(f"Você recebeu {p.nickname}!")
        time.sleep(1)
    menu_main(trainer)

if __name__ == "__main__":
    main()
