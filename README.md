# Elevator Simulation – Reinforcement Learning Control of Elevators

Projekt **Elevator Simulation** to środowisko symulacyjne i interfejs graficzny umożliwiające badanie oraz trenowanie agentów **uczenia ze wzmocnieniem (Reinforcement Learning, RL)** do sterowania systemem wind w budynku wielopiętrowym.  
Celem projektu jest stworzenie platformy eksperymentalnej, która pozwala porównywać różne algorytmy sterowania – zarówno klasyczne (np. oparte na regułach), jak i nowoczesne metody oparte na uczeniu maszynowym.

---

## Idea projektu

Zarządzanie ruchem wind w budynkach o dużym natężeniu ruchu to problem decyzyjny o wysokiej złożoności.  
System sterowania musi w czasie rzeczywistym minimalizować czas oczekiwania pasażerów oraz optymalizować zużycie energii.  
Zastosowanie **uczenia ze wzmocnieniem (RL)** pozwala agentowi uczyć się optymalnych strategii poprzez interakcję ze środowiskiem — w tym przypadku z symulatorem wind.

W projekcie zastosowano klasyczne i nowoczesne algorytmy RL, takie jak:
- **Q-Learning**
- **Deep Q-Network (DQN)**
- **DRQN (Deep Recurrent Q-Network)** z warstwami LSTM dla pamięci sekwencyjnej

Środowisko zostało zaimplementowane w Pythonie i pozwala definiować parametry budynku, liczbę wind, strategię sterowania oraz obserwować efekty działania agenta w GUI.

---

## Struktura projektu

---

## ⚙️ Instrukcja uruchomienia

Aby uruchomić projekt lokalnie:

1. **Sklonuj repozytorium:**
   ```bash
   git clone https://github.com/matrochanowski/elevator-project.git
   cd elevator-simulation

2. **Utwórz i aktywuj środowisko wirtualne**:

    ```bash
    python -m venv venv
    source venv/bin/activate       # Linux/macOS
    venv\Scripts\activate          # Windows

3. **Zainstaluj wymagania**:

    ```bash
    pip install -r requirements.txt

4. Uruchom symulację z GUI:
    
    ```bash
    python simulation/gui/main.py
