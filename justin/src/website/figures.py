# figures.py

# Makes figures using matplotlib and pandas for display on website. In particular
# boxplots for showing distributions of trip times.

import matplotlib
matplotlib.use("Agg")           # prevents python rocketship
import matplotlib.pyplot as plt

def multi_boxplot(quantiles_list,quantile_labels,start,end,day):

    fig, ax = plt.subplots(figsize=(.7*len(quantiles_list)+1,6))

    bp = ax.boxplot(quantiles_list, widths=.5)
    plt.setp(bp['boxes'], color='steelblue')
    plt.setp(bp['whiskers'], color='steelblue',linestyle='-')
    plt.setp(bp['fliers'], color='steelblue', marker='')
    plt.setp(bp['caps'], color='steelblue', marker='')
    
    boxColors = 'steelblue'
    numBoxes = len(quantiles_list)
    medians = range(numBoxes)
    for i in range(numBoxes):
      box = bp['boxes'][i]
      boxX = []
      boxY = []
      for j in range(5):
          boxX.append(box.get_xdata()[j])
          boxY.append(box.get_ydata()[j])
      boxCoords = zip(boxX,boxY)
      boxPolygon = matplotlib.patches.Polygon(boxCoords, facecolor=boxColors)
      ax.add_patch(boxPolygon)

      med = bp['medians'][i]
      medianX = []
      medianY = []
      for j in range(2):
          medianX.append(med.get_xdata()[j])
          medianY.append(med.get_ydata()[j])
          plt.plot(medianX, medianY, 'k',color='white')
          medians[i] = medianY[0]

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

    ax.yaxis.set_label_text('Trip time in minutes', size=12)
    ax.yaxis.set_tick_params(labelsize=12)
    
    ax.xaxis.set_label_text(day, size=12)

    max_value = max([max(elt) for elt in quantiles_list])
    upper_bound = int(max(max_value*4/3,max_value+2))

    plt.yticks(range(0,upper_bound,max(upper_bound/5,1)))
    plt.tight_layout()
    newlabels = [quantile_labels[i] if i%2 == 0 else ' ' for i in range(len(quantile_labels))]
    ax.xaxis.set_ticklabels(newlabels)
    ax.xaxis.set_tick_params(labelsize=12)
    fig.suptitle('Times from '+start+' to '+end+'.',size=16)
    
#     fig.text(.99, .5,'testtesttesttesttest',transform=fig.gca().transAxes, size=8)
    return fig