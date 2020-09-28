import matplotlib.pyplot as plt

x = list(range(1985,2017))

y = [
76022,
100542,
123410,
148756,
194913,
186342,
181143,
154822,
137643,
129186,
128010,
127214,
126677,
130552,
135320,
136713,
174997,
182860,
201295,
261290,
269654,
280757,
313756,
299427,
284737,
266211,
255563,
253268,
257715,
262556,
289525,
323370
]

ax = plt.subplot(111)
ax.spines['top'].set_visible(False)    
ax.spines['bottom'].set_visible(False)    
ax.spines['right'].set_visible(False)    
ax.spines['left'].set_visible(False) 

ax.get_xaxis().tick_bottom()    
ax.get_yaxis().tick_left() 

# plt.ylim(min(flow_hist)-5, max(flow_hist)+5)    
# plt.xlim(-3, len(t) + 3)

# plt.tick_params(axis="both", which="both", bottom="off", top="off",    
#                 labelbottom="on", left="off", right="off", labelleft="on")

# plt.plot(range(len(t)), [0 for _ in t], '--', lw=0.5, color='black', alpha=0.8)



plt.ylabel('Total Value', fontsize=16)
plt.xlabel('Year', fontsize=16)

plt.plot(x, y, lw=1.5, color='#8B0000') 

plt.savefig('./vover.png', bbox_inches='tight')
