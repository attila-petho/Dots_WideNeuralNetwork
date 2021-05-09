from dots_env import Dotsgame_env
from agent import Agent
from plotter import scoreplot

def demo():
    maxsteps = 500  # Max lépés/epizód (Tanítás: 1000)
    env = Dotsgame_env(max_steps=maxsteps, FPS = 20, show_horizon=True)
    red_agent = Agent(max_epsilon=0)
    yellow_agent = Agent(max_epsilon=0)
    red_agent.load(path='models/red_model_ep_300.pth')        # 'red_model_ep_{}.pth'.format(n_episodes)
    yellow_agent.load(path='models/yellow_model_ep_300.pth')  # 'yellow_model_ep_{}.pth'.format(n_episodes)
    plot_red_scores = []
    plot_yellow_scores = []
    plot_red_mean_scores = []
    plot_yellow_mean_scores = []
    total_red_score = 0.0
    total_yellow_score = 0.0
    red_record = 0.0
    yellow_record = 0.0
    total_episode_lengths = 0.0
    n_episodes = 1

    while True:
        # Régi állapot
        state_old = env.get_state()
        red_state_old = state_old[0]
        yellow_state_old = state_old[1]

        # Döntés a cselekvésről
        red_final_move = red_agent.get_action(red_state_old)
        yellow_final_move = yellow_agent.get_action(yellow_state_old)

        # Cselekvés végrehajtása és az új állapot megfigyelése
        state_new, reward, score, iteration, game_over = env.step(red_final_move, yellow_final_move)
        red_score = score[0]
        yellow_score = score[1]

        if game_over:
            env.reset()
            total_episode_lengths += iteration
            avg_length = round(total_episode_lengths / n_episodes, 0)
            red_agent.n_episodes = yellow_agent.n_episodes = n_episodes

            # Frissítjük a rekordokat
            if red_score > red_record:
                red_record = red_score
            if yellow_score > yellow_record:
                yellow_record = yellow_score

            # Az epizód végén kiiratjuk az infókat
            print('Episode: ', n_episodes, ' Red Score: ', red_score, ' Red Record: ', red_record,
                  ' Yellow Score: ', yellow_score, ' Yellow Record: ', yellow_record, ' Average episode length: ', avg_length)

            # Eltároljuk a szerzett pontokat és kirajzoljuk az ábrákat
            plot_red_scores.append(red_score)
            plot_yellow_scores.append(yellow_score)
            total_red_score += red_score
            total_yellow_score += yellow_score
            red_mean_score = round(total_red_score/n_episodes, 1)
            yellow_mean_score = round(total_yellow_score/n_episodes, 1)
            plot_red_mean_scores.append(red_mean_score)
            plot_yellow_mean_scores.append(yellow_mean_score)
            plot_scores = [plot_red_scores, plot_yellow_scores]
            plot_mean_scores = [plot_red_mean_scores, plot_yellow_mean_scores]
            scoreplot(plot_scores, plot_mean_scores)
            n_episodes += 1

if __name__ == '__main__':
    demo()