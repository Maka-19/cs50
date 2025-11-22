class NimAI:

    def __init__(self, alpha=0.5, epsilon=0.1):
        self.q = dict()
        self.alpha = alpha
        self.epsilon = epsilon


    def get_q_value(self, state, action):
        """
        Return Q-value for (state, action).
        If not present, return 0.
        """
        state = tuple(state)

        if (state, action) not in self.q:
            return 0

        return self.q[(state, action)]


    def update_q_value(self, state, action, old_q, reward, future_rewards):
        """
        Update Q-value using Q-learning formula:
        Q(s,a) ← old + α * ((reward + future) - old)
        """
        new_value_estimate = reward + future_rewards
        updated_q = old_q + self.alpha * (new_value_estimate - old_q)

        state = tuple(state)
        self.q[(state, action)] = updated_q


    def best_future_reward(self, state):
        """
        Return the highest Q-value across all actions for this state.
        If no actions or Q-values, return 0.
        """
        state = tuple(state)
        actions = Nim.available_actions(state)

        if not actions:
            return 0

        best = 0
        for action in actions:
            q = self.get_q_value(state, action)
            if q > best:
                best = q

        return best


    def choose_action(self, state, epsilon=True):
        """
        Choose action using epsilon-greedy or greedy strategy.
        """
        state = tuple(state)
        actions = list(Nim.available_actions(state))

        if not actions:
            return None

        # If epsilon-greedy is ON
        if epsilon and random.random() < self.epsilon:
            return random.choice(actions)

        # GREEDY: choose action with highest Q-value
        best_q = float("-inf")
        best_actions = []

        for action in actions:
            q = self.get_q_value(state, action)

            if q > best_q:
                best_q = q
                best_actions = [action]
            elif q == best_q:
                best_actions.append(action)

        return random.choice(best_actions)
