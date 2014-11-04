import matplotlib.pyplot as plt

# Makes a reasonable looking boxplot. Idea is to input [10,25,50,75,90] percentiles
# to have that be the boxplot (even though the function is returning min and max instead
# of 10th and 90th percentiles respectively).

def make_boxplot(data):
    
    # define "figure" and "axes" objects, where the "axes" is really my figure and
    # "figure" is the thing containing my figure. Annoying.
    
    fig, ax = plt.subplots()
    fig.set_size_inches(5,1)
    
    # Make the boxplot and get rid of borders I don't want.
    
    ax.boxplot(data,vert=False,widths=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Get rid of ticks.

    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    
    # Set scale of plot as roughly [0,(4/3)*max]

    upper_bound = max(data)*4/3
    
    # Scale the plot
    
    plt.xticks(range(0,upper_bound,upper_bound/7))
    
    # Maybe not necessary, but seems to make things look better for now
    
    plt.tight_layout()
    
    # Remove pointless y-axis labels in a hacky way
    
    ax.yaxis.set_ticklabels(' ')
    
    # Save the figure (untested)
    # Relevant: http://stackoverflow.com/questions/20107414/passing-a-matplotlib-figure-to-html-flask
        
    plt.savefig('figure.png',bbox_inches='tight')