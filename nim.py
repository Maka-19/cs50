import random

class Nim:
    """
    Nim game environment.
    """

    def __init__(self, piles):
        self.piles = piles.copy()
        self.player = 0
        self.winner = None

    @staticmethod
    def available_actions(piles):
        actions = set()
        for i, pile in enumerate(piles):
            for j in range(1, pile + 1):
                actions.add((i, j))
        return actions

    @staticmethod
    def other_player(player):
        return 1 - player

    def switch_player(self):
        self.player = Nim.other_player(self.player)

    def move(self, action):
        pile, count = action
        self.piles[pile] -= count
        self.switch_player()
        if all(pile == 0 for pile in self.piles):
            self.winner = self.player


class NimAI:
    """
    Q-Learning AI for Nim.
    """

    def __init__(self, alpha=0.5, epsilon=0.1):
        self.q = dict()
        self.alpha = alpha
        self.epsilon = epsilon

    def get_q_value(self, state, action):
        """
        Return Q-value for (state, action) pair.
        Default to 0 if missing.
        """
        state = tuple(state)
        return self.q.get((state, action), 0)

    def update_q_value(self, state, action, old_q, reward, future_rewards):
        """
        Apply Q-learning update.
        Q <- old + α * (reward + future - old)
        """
        new_value_estimate = reward + future_rewards
        updated = old_q + self.alpha * (new_value_estimate - old_q)

        state = tuple(state)
        self.q[(state, action)] = updated

    def best_future_reward(self, state):
        """
        Return max Q-value among all actions in this state.
        If none exist, return 0.
        """
        state = tuple(state)
        actions = Nim.available_actions(list(state))

        if not actions:
            return 0

        max_reward = 0
        for action in actions:
            q = self.get_q_value(state, action)
            if q > max_reward:
                max_reward = q

        return max_reward

    def choose_action(self, state, epsilon=True):
        """
        Choose an action using ε-greedy or greedy strategy.
        """
        actions = list(Nim.available_actions(state))

        if not epsilon:
            # greedy
            best = None
            best_q = float("-inf")
            for action in actions:
                q = self.get_q_value(state, action)
                if q > best_q:
                    best_q = q
                    best = action
            return best

        # ε-greedy
        if random.random() < self.epsilon:
            return random.choice(actions)

        # otherwise greedy
        best = None
        best_q = float("-inf")
        for action in actions:
            q = self.get_q_value(state, action)
            if q > best_q:
                best_q = q
                best = action

        return best


def train(n):
    """
    Train an AI by playing `n` games of Nim.
    """
    ai = NimAI()

    for _ in range(n):
        game = Nim([1, 3, 5, 7])
        last = {0: {"state": None, "action": None},
                1: {"state": None, "action": None}}

        while True:
            state = game.piles.copy()
            action = ai.choose_action(state)

            last_state = last[game.player]["state"]
            last_action = last[game.player]["action"]

            game.move(action)
            new_state = game.piles.copy()

            if last_state is not None:
                reward = 0
                future = ai.best_future_reward(new_state)
                old_q = ai.get_q_value(last_state, last_action)
                ai.update_q_value(last_state, last_action,
                                  old_q, reward, future)

            last[game.player]["state"] = state
            last[game.player]["action"] = action

            if game.winner is not None:
                ai.update_q_value(state, action,
                                  ai.get_q_value(state, action),
                                  1, 0)

                other = Nim.other_player(game.player)

                if last[other]["state"] is not None:
                    ai.update_q_value(
                        last[other]["state"],
                        last[other]["action"],
                        ai.get_q_value(last[other]["state"],
                                       last[other]["action"]),
                        -1,
                        0
                    )
                break

    return ai


def play(ai):
    """
    Play Nim against the trained AI.
    """
    game = Nim([1, 3, 5, 7])

    while True:
        print("Piles:", game.piles)

        if game.player == 0:
            pile = int(input("Choose pile: "))
            count = int(input("Choose count: "))
            action = (pile, count)
        else:
            action = ai.choose_action(game.piles, epsilon=False)
            print("AI chose:", action)

        game.move(action)

        if game.winner is not None:
            print("Winner:", game.winner)
            return
