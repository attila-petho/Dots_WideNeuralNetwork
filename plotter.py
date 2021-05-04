import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def scoreplot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.subplots_adjust(wspace=15)
    plt.clf()
    plt.subplot(211)
    plt.title('Training...')
    plt.ylabel('Red Score')
    plt.grid(True)
    plt.plot(scores[0])
    plt.plot(mean_scores[0])
    plt.ylim(ymin=0)
    plt.text(len(scores[0])-1, scores[0][-1], str(scores[0][-1]))
    plt.text(len(mean_scores[0])-1, mean_scores[0][-1], str(mean_scores[0][-1]))
    plt.show(block=False)
    plt.pause(.1)

    plt.subplot(212)
    plt.xlabel('Number of Episodes')
    plt.ylabel('Yellow Score')
    plt.grid(True)
    plt.plot(scores[1])
    plt.plot(mean_scores[1])
    plt.ylim(ymin=0)
    plt.text(len(scores[1]) - 1, scores[1][-1], str(scores[1][-1]))
    plt.text(len(mean_scores[1]) - 1, mean_scores[1][-1], str(mean_scores[1][-1]))
    plt.show(block=False)
    plt.pause(.1)