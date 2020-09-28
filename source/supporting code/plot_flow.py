import matplotlib.pyplot as plt
import json

with open('../resources/2016_cell_state.json', 'r') as f:
	state = json.load(f)

cell_to_plot = '4094'
flow_hist = state[cell_to_plot]['flow_hist']
t = list(range(len(flow_hist)))

ax = plt.subplot(111)
ax.spines['top'].set_visible(False)    
ax.spines['bottom'].set_visible(False)    
ax.spines['right'].set_visible(False)    
ax.spines['left'].set_visible(False) 

ax.get_xaxis().tick_bottom()    
ax.get_yaxis().tick_left() 

plt.ylim(min(flow_hist)-5, max(flow_hist)+5)    
plt.xlim(-3, len(t) + 3)

# plt.tick_params(axis="both", which="both", bottom="off", top="off",    
#                 labelbottom="on", left="off", right="off", labelleft="on")

plt.plot(range(len(t)), [0 for _ in t], '--', lw=0.5, color='black', alpha=0.8)



plt.ylabel('Flow', fontsize=16)
plt.xlabel('Epoch', fontsize=16)

plt.plot(t, flow_hist, lw=1.5, color='#8B0000') 

plt.savefig('../visuals/flow' + cell_to_plot + '.png', bbox_inches='tight')

# EOF