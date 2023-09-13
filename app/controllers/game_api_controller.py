import sys
sys.append('../')



class game_api:
    def __init__(self):
        self.game = GameController()
        self.game.start_game(6)
        self.agents_list = []
        self.agents_list.append(simple_agent(self.game, 0.2, 0.0, 0.7, f'playerAzul', smart_attack=True))
        self.agents_list.append(simple_agent(self.game, 0.1, 0.0, 0.2, f'playerVermelho'))
        self.agents_list.append(simple_agent(self.game, 0.1, 0.0, 0.8, f'playerVerde'))
        self.agents_list.append(simple_agent(self.game, 0.1, 0.0, 0.1, f'playerRoxo'))
        self.agents_list.append(simple_agent(self.game, 0.05, 0.0, 0.1, f'playerAmarelo'))
        self.agents_list.append(simple_agent(self.game, 0.1, 0.0, 0.1, f'playerCinza'))

    def get_gamestate(self):
        return self.game.gamestate

    def get_gamestate_matrix(self):
        return self.game.gamestate_matrix

    def get_gamestate_matrix(self):
        return self.game.gamestate_matrix

    def get_current_player_index(self):
        return self.game.current_player_index

    def get_current_player(self):
        return self.game.current_player

    def get_current_phase(self):
        return self.game.current_phase

    def get_current_phase(self):
        return self.game.curr