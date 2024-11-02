class Tournament:
    stage_labels = {0: 'final', 1: 'semi-final', 2: 'quarter-final', 3: 'round of 16'}

    @staticmethod
    def get_label(n_stage, previous_stage=1):
        return Tournament.stage_labels[n_stage - previous_stage]
