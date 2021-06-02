import json	
import numpy as np
import matplotlib.pyplot as plt
import datetime

f = open('reduced.json', 'r')
db = json.load(f)

dates = [entry['date'] for entry in db]
userpw = [entry['passwords'][0]['username'] + ':' + entry['passwords'][0]['password'] for entry in db]
count = [entry['passwords'][0]['count'] for entry in db]
"""
plt.gcf().subplots_adjust(bottom=0.15)
plt.tight_layout()
plt.autoscale()


fig = plt.figure()
ax = fig.add_axes([0,0,1,1])

plt.xlabel("Date", 
           family='serif', 
           color='r', 
           weight='normal', 
           size = 16,
           labelpad = 6)
plt.ylabel("Count", 
           family='serif', 
           color='r', 
           weight='normal', 
           size = 16,
           labelpad = 6)

ax.bar(dates, count)
plt.show()
"""
print(userpw)
labels = dates
men_means = count
# women_means = [25, 32, 34, 20, 25]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()

for elem in userpw:
	rects = ax.bar(x - width/2, men_means, width, label=elem)
	ax.bar_label(rects, padding=3)
# rects2 = ax.bar(x + width/2, women_means, width, label='Women')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Count')
ax.set_title('Password density by date')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

# ax.bar_label(rects2, padding=3)

fig.tight_layout()

plt.show()

"""
data = [[30, 25, 50, 20],
[40, 23, 51, 17],
[35, 22, 45, 19]]
X = np.arange(4)
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.bar(X + 0.00, data[0], color = 'b', width = 0.25)
ax.bar(X + 0.25, data[1], color = 'g', width = 0.25)
ax.bar(X + 0.50, data[2], color = 'r', width = 0.25)

plt.show()
"""
