from dots_env import Dotsgame_env
from agent import Agent
from plotter import scoreplot, saveplot

def train():
    maxsteps = 1000     # Max lépés/epizód (Tanítás: 1000)
    save_freq = 20      # Mentés gyakorisága
    load_model = False  # Mentett model betöltése
    env = Dotsgame_env(max_steps=maxsteps, show_horizon=True)
    red_agent = Agent()
    yellow_agent = Agent()
    epoch = 1
    if load_model:
        red_epoch = red_agent.load(path='models/red_model_ep_.pth')             #'red_model_ep_{}.pth'.format(n_episodes)
        yellow_epoch = yellow_agent.load(path='models/yellow_model_ep_.pth')    #'yellow_model_ep_{}.pth'.format(n_episodes)
        epoch = red_epoch
    plot_red_scores = []
    plot_yellow_scores = []
    plot_red_mean_scores = []
    plot_yellow_mean_scores = []
    total_red_score = 0.0
    total_yellow_score = 0.0
    red_record = 0.0
    yellow_record = 0.0
    episode_lengths = []
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
        red_state_new = state_new[0]
        yellow_state_new = state_new[1]
        red_reward = reward[0]
        yellow_reward = reward[1]
        red_score = score[0]
        yellow_score = score[1]

        # train short memory: state_old, final_move, reward, state_new, game_over
        red_agent.train_short_memory(red_state_old, red_final_move, red_reward, red_state_new, game_over)
        yellow_agent.train_short_memory(yellow_state_old, yellow_final_move, yellow_reward, yellow_state_new, game_over)

        # Memóriába: state_old, final_move, reward, state_new, game_over
        red_agent.remember(red_state_old, red_final_move, red_reward, red_state_new, game_over)
        yellow_agent.remember(yellow_state_old, yellow_final_move, yellow_reward, yellow_state_new, game_over)

        if game_over:
            # train long memory (Experience replay)
            env.reset()
            episode_lengths.append(iteration)
            avg_length = round(sum(episode_lengths) / n_episodes, 0)
            red_agent.n_episodes = yellow_agent.n_episodes = n_episodes
            red_agent.train_long_memory()
            yellow_agent.train_long_memory()

            # X epizódonként elmentjük a modelleket és az ábrát
            if n_episodes % save_freq == 0:
                red_agent.save(epoch, file_name='red_model_ep_{}.pth'.format(n_episodes))
                yellow_agent.save(epoch, file_name='yellow_model_ep_{}.pth'.format(n_episodes))
                saveplot(n_episodes)

            # Epoch növelése
            if n_episodes % 100 == 0:
                epoch += 1

            # Frissítjük a rekordokat
            if red_score > red_record:
                red_record = red_score
            if yellow_score > yellow_record:
                yellow_record = yellow_score

            # Az epizód végén kiiratjuk az infókat
            print('Epoch: ', epoch, ' Episode: ', n_episodes, ' Red Score: ', red_score, ' Red Record: ', red_record,
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
    train()