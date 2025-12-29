# API Документация

## Базовый URL

```
http://127.0.0.1:8000
```

## Endpoints

### Character

#### GET /api/characters/{character_id}
Получить информацию о персонаже.

**Response:**
```json
{
  "id": 1,
  "name": "TestCharacter",
  "level": 1,
  "experience": 0,
  "strength": 10,
  "agility": 10,
  "intelligence": 10,
  "endurance": 10,
  "wisdom": 10,
  "luck": 10,
  "character_class": "adventurer",
  "location_id": 1
}
```

#### GET /api/characters/{character_id}/stats
Получить персонажа с рассчитанными характеристиками.

**Response:**
```json
{
  "character": {...},
  "stats": {
    "physical_damage": {"min": 15, "max": 22},
    "magical_damage": {"min": 16, "max": 20},
    "physical_defense": 15,
    "magical_defense": 8.0,
    "crit_chance": 1.5,
    "speed": 7
  },
  "max_hp": 120,
  "max_mp": 85
}
```

### Combat

#### POST /api/combat/attack
Атаковать моба.

**Request:**
```json
{
  "character_id": 1,
  "monster_id": 1,
  "skill_id": null
}
```

**Response:**
```json
{
  "damage": 25,
  "is_crit": false,
  "monster_hp": 55,
  "monster_max_hp": 80,
  "message": "Вы нанесли 25 урона"
}
```

### Location

#### GET /api/locations
Получить список всех локаций.

#### GET /api/locations/{location_id}
Получить информацию о локации.

**Response:**
```json
{
  "id": 1,
  "name": "Гнилостные Топи",
  "description": "...",
  "travel_time": 5,
  "connected_locations": [2],
  "monsters": [...]
}
```

#### POST /api/locations/travel
Переместиться в локацию.

**Request:**
```json
{
  "character_id": 1,
  "target_location_id": 2
}
```

### Inventory

#### GET /api/inventory/{character_id}
Получить инвентарь персонажа.

#### GET /api/inventory/{character_id}/equipment
Получить экипировку персонажа.

#### POST /api/inventory/equip
Надеть предмет.

**Request:**
```json
{
  "character_id": 1,
  "item_id": 1
}
```

### Skills

#### GET /api/skills
Получить список всех навыков.

#### GET /api/skills/{character_id}/learned
Получить изученные навыки персонажа.

#### POST /api/skills/learn
Изучить навык.

**Request:**
```json
{
  "character_id": 1,
  "skill_id": 1
}
```

### Market

#### GET /api/market/orders
Получить ордера на рынке.

**Query Parameters:**
- `item_id` (optional)
- `order_type` (optional): "buy" or "sell"
- `status` (optional): "pending", "filled", "cancelled", "partial"

#### POST /api/market/orders
Создать ордер на рынке.

**Request:**
```json
{
  "character_id": 1,
  "item_id": 4,
  "order_type": "sell",
  "price": 1000.0,
  "quantity": 5
}
```

### Crafting

#### POST /api/crafting/check
Проверить возможность крафта.

**Request:**
```json
{
  "character_id": 1,
  "recipe": {
    "result_item_id": 5,
    "core_item_id": 3,
    "shell_items": [{"item_id": 4, "quantity": 5}]
  }
}
```

#### POST /api/crafting/craft
Создать предмет.

**Request:**
```json
{
  "character_id": 1,
  "recipe": {...}
}
```

## Автоматическая документация

Swagger UI доступен по адресу: `http://127.0.0.1:8000/docs`

