from PySide6.QtWidgets import QMessageBox

from simulation.enums import AlgorithmEnum
from simulation.training.schema import TrainingConfigSchema, QLearningParamsSchema, RewardMultipliersSchema

from simulation.training.config import load_training_config, save_training_config

from simulation.config import load_config

from simulation.training.scripts.train_q_learning import train_q_learning
from simulation.training.agents.q_learning_agent import QLearningAgent, QLearningAgentsGroup


class ReinforcementPage:
    def __init__(self, window):
        self.window = window
        self._setup_algorithm_combo()
        self._connect_logic()
        self.load_settings()

    # --- PUBLIC API ---
    def connect_buttons(self):
        w = self.window
        w.startTrainingPushButton.clicked.connect(self.start_training)
        self.window.backButton_2.clicked.connect(w.show_main)
        w.saveConfigPushButton.clicked.connect(self.save_settings)

    # --- INITIAL SETUP ---
    def _setup_algorithm_combo(self):
        w = self.window
        w.RlAlgorithmComboBox.clear()

        for alg in AlgorithmEnum:
            # filtrujemy tylko RL
            if alg == AlgorithmEnum.Q_LEARNING:
                w.RlAlgorithmComboBox.addItem(alg.pretty, userData=alg)

    def _connect_logic(self):
        self.window.RlAlgorithmComboBox.currentIndexChanged.connect(
            self.on_algorithm_changed
        )

    def start_training(self):
        self.save_settings()
        general_config = load_config()
        rl_config = load_training_config()

        agents = []
        for _ in range(len(general_config.elevators)):
            agents.append(QLearningAgent(["UP", "DOWN", "STANDING"],
                                         alpha=rl_config.q_learning_params.alpha,
                                         gamma=rl_config.q_learning_params.gamma,
                                         epsilon=rl_config.q_learning_params.starting_epsilon))

        agents_group = QLearningAgentsGroup(agents)
        agents_group, mean_reward = train_q_learning(episodes=rl_config.episodes,
                                                     steps=rl_config.steps_per_episode,
                                                     agents_group=agents_group)
        save_path = agents_group.save(rl_config.save_name)

        QMessageBox.information(self.window, "Training finished",
                                f"The training has finished.\nTotal number of episodes: {rl_config.episodes},"
                                f"\nMean episode reward value: {mean_reward},\nSaved as {save_path}")

    # --- LOAD SETTINGS ---
    def load_settings(self):
        try:
            config = load_training_config()
        except Exception:
            return

        w = self.window

        # --- algorithm ---
        try:
            alg_enum = AlgorithmEnum(config.algorithm)
            idx = w.RlAlgorithmComboBox.findData(alg_enum)
            if idx >= 0:
                w.RlAlgorithmComboBox.setCurrentIndex(idx)
        except Exception:
            pass

        # --- file name ---
        w.saveModelAsLineEdit.setText(config.save_name)

        # --- episodes ---
        w.numberOfEpisodesSpinBox.setValue(config.episodes)

        # --- steps per episode ---
        w.stepsPerEpisodeSpinBox.setValue(config.steps_per_episode)

        # --- Q-learning params ---
        if config.q_learning_params:
            q = config.q_learning_params
            w.alphaSpinBox.setValue(q.alpha)
            w.gammaSpinBox.setValue(q.gamma)
            w.startingEpsilonSpinBox.setValue(q.starting_epsilon)
            w.epsilonDecaySpinBox.setValue(q.epsilon_decay)

        # --- reward multipliers ---
        rp = config.reward_params
        w.reward1SpinBox.setValue(rp.penalty_outside)
        w.reward2SpinBox.setValue(rp.penalty_inside)
        w.reward3SpinBox.setValue(rp.reward_pick_up)
        w.reward4SpinBox.setValue(rp.reward_delivery)

        self.on_algorithm_changed(w.RlAlgorithmComboBox.currentIndex())

    # --- UI LOGIC ---
    def on_algorithm_changed(self, index):
        alg = self.window.RlAlgorithmComboBox.itemData(index)
        w = self.window

        if alg == AlgorithmEnum.Q_LEARNING:
            w.stackedWidget_rl.setCurrentIndex(0)
        else:
            w.stackedWidget_rl.setCurrentIndex(0)

    def save_settings(self):
        w = self.window

        # --- algorithm ---
        alg_enum = w.RlAlgorithmComboBox.currentData()
        alg_enum = AlgorithmEnum(alg_enum)

        algorithm_value = alg_enum.value

        # --- save name ---
        save_name = w.saveModelAsLineEdit.text().strip()
        if not save_name:
            QMessageBox.warning(w, "Error", "Model save name cannot be empty.")
            return

        # --- episodes ---
        episodes = w.numberOfEpisodesSpinBox.value()

        # --- steps per episode ---
        steps_per_episode = w.stepsPerEpisodeSpinBox.value()

        # --- q-learning params ---
        q_params = None
        if alg_enum == AlgorithmEnum.Q_LEARNING:
            q_params = QLearningParamsSchema(
                alpha=w.alphaSpinBox.value(),
                gamma=w.gammaSpinBox.value(),
                starting_epsilon=w.startingEpsilonSpinBox.value(),
                epsilon_decay=w.epsilonDecaySpinBox.value()
            )

        # --- reward params ---
        reward_params = RewardMultipliersSchema(
            penalty_outside=w.reward1SpinBox.value(),
            penalty_inside=w.reward2SpinBox.value(),
            reward_pick_up=w.reward3SpinBox.value(),
            reward_delivery=w.reward4SpinBox.value()
        )

        # --- build config object ---
        config = TrainingConfigSchema(
            algorithm=algorithm_value,
            save_name=save_name,
            episodes=episodes,
            steps_per_episode=steps_per_episode,
            q_learning_params=q_params,
            reward_params=reward_params
        )

        # --- save ---
        save_training_config(config)

        QMessageBox.information(w, "Saved", "Training configuration saved successfully.")

