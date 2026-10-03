> **Playable single-player prototype:** this branch connects the screen to the
> Python engine and tactical bot. Follow [the game setup instructions](frontend/README.md).
> The original proposal below is historical: multiplayer, accounts, database
> persistence, special effects, and simultaneous turns are not implemented in
> this prototype. Battles use alternating turns; types are currently labels only.

# Pokemon-Style-Game
Two players battle using teams of creatures with different moves, stats, abilities, and status effects.

# BattleLab

*A multiplayer turn-based battle engine built with Python.*

BattleLab is a backend-focused game systems project inspired by turn-based monster battlers. Instead of recreating an existing game, the focus is on building the underlying **battle engine**, **multiplayer networking**, and **server architecture** that power online turn-based games.

The project is designed as a **3-person CS portfolio project**, prioritising algorithms, software engineering, networking and backend development over complex graphics.

## Demo

> *(Add screenshots or a GIF once the project is playable.)*

## Features

* Online multiplayer battles using WebSockets
* Server-authoritative battle engine
* Turn-based combat with simultaneous move selection
* Custom creatures, moves and abilities
* Type effectiveness system
* Status effects (Burn, Poison, Freeze, etc.)
* Priority-based turn resolution
* Player accounts and team management
* Match history stored in a database
* Docker support for easy deployment

## Tech Stack

| Component       | Technology            |
| --------------- | --------------------- |
| Backend         | Python                |
| API             | FastAPI               |
| Multiplayer     | WebSockets            |
| Database        | PostgreSQL            |
| Frontend        | HTML, CSS, JavaScript |
| Testing         | Pytest                |
| Containers      | Docker                |
| Version Control | Git                   |

## System Architecture

```text
Browser Client
      │
      │ WebSocket
      ▼
 FastAPI Server
      │
 ┌────┴─────────┐
 │              │
Battle Engine  PostgreSQL
 │
 ├── Turn Resolution
 ├── Damage System
 ├── Status Effects
 ├── Type Chart
 └── Match State
```

The server is the single source of truth. Clients only send player actions, while all battle calculations happen on the backend.

## How Battles Work

Each player selects a move.

The server waits until both players have locked in their actions.

The battle engine then resolves the turn using a deterministic sequence.

```text
Start Turn
    ↓
Receive both moves
    ↓
Determine move order
    ↓
Apply attacks
    ↓
Apply status effects
    ↓
Check knockouts
    ↓
End Turn
```

This prevents cheating and keeps every client synchronised.

## Battle Engine

Every creature is represented as structured data.

Example:

```json
{
  "name": "Rockling",
  "hp": 120,
  "attack": 80,
  "defense": 95,
  "speed": 30
}
```

Moves are also data-driven.

```json
{
  "name": "Boulder Toss",
  "power": 70,
  "accuracy": 90,
  "type": "Rock",
  "priority": 0
}
```

The engine combines these values with modifiers such as critical hits, type effectiveness and status effects to calculate damage.

## Type Effectiveness

Rather than hard-coding every interaction, BattleLab stores effectiveness values in a lookup table.

| Attacker | Defender | Multiplier |
| -------- | -------- | ---------- |
| Fire     | Grass    | 2×         |
| Fire     | Water    | 0.5×       |
| Fire     | Fire     | 0.5×       |

This makes adding new creature types straightforward.

## Status System

Status effects are managed as persistent battle states.

Example:

```text
Rockling

HP: 82
Status: Burn
Turns Remaining: 3
```

Each turn the engine automatically updates active effects before continuing.

Supported statuses include:

* Burn
* Poison
* Freeze
* Paralysis *(planned)*
* Sleep *(planned)*

## Multiplayer

BattleLab uses WebSockets for real-time communication.

```text
Player A
   │
   ▼
FastAPI Server
   ▲
   │
Player B
```

Players never calculate damage locally.

The server validates every move before updating both clients.

## Database

Persistent data includes:

* Users
* Teams
* Creatures
* Match History
* Win/Loss Statistics

Example schema:

```text
users
teams
creatures
matches
```

## Project Structure

```text
battlelab/
│
├── backend/
│   ├── api/
│   ├── engine/
│   ├── models/
│   ├── services/
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── database/
│
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Getting Started

### Clone

```bash
git clone https://github.com/yourusername/battlelab.git
cd battlelab
```

### Install

```bash
pip install -r requirements.txt
```

### Run

```bash
python -m uvicorn backend.main:app
```

Battles are held in server memory. Restarting the server ends active battles;
leave automatic reload off while playtesting. Restart manually after backend edits.

Or with Docker:

```bash
docker compose up --build
```

## Development Roadmap

### Phase 1

* Creature system
* Move system
* Turn engine
* Damage calculation

### Phase 2

* Type chart
* Status effects
* Switching creatures
* Win conditions

### Phase 3

* WebSocket multiplayer
* Matchmaking
* Database integration

### Phase 4

* Polish
* Battle animations
* Replay system
* Ranked ladder

## Team Responsibilities

### Member 1 – Battle Engine

* Damage calculations
* Turn order
* Status effects
* Battle rules

### Member 2 – Backend

* FastAPI
* WebSockets
* Database
* Docker

### Member 3 – Frontend

* Battle interface
* Animations
* Menus
* Player experience

## What This Project Demonstrates

This project was intentionally built to demonstrate software engineering concepts commonly required for backend and software internships.

* Python development
* REST APIs
* WebSocket networking
* State management
* Data structures
* Algorithms
* Docker
* PostgreSQL
* Git workflows
* Testing

Rather than focusing on graphics, BattleLab focuses on building the systems that make online games work.
