
import plotly.express as px
import numpy as np
import pandas as pd
import statistics as st
from scipy.stats import norm
import plotly.graph_objects as go
df = pd.read_csv("keyboard_scores.csv")

# Add histogram data
x1, x2, x3, x4 = df[["First Session: Concordant - Score", "First Session: Discordant - Score", "Second Session: Concordant - Score", "Second Session: Discordant - Score"]]


# Group data together
hist_data = [x1, x2, x3, x4]


group_labels = ['Group 1', 'Group 2', 'Group 3', 'Group 4']

mean_first_conc = st.mean(df["First Session: Concordant - Score"])
sd_first_conc = st.stdev(df["First Session: Concordant - Score"])

sort_first_conc = np.sort(df["First Session: Concordant - Score"])
norm_first_conc = norm.pdf(sort_first_conc, mean_first_conc , sd_first_conc )
#plt.plot(sort_first_conc, norm_first_conc)


mean_first_dis = st.mean(df["First Session: Discordant - Score"])
sd_first_dis = st.stdev(df["First Session: Discordant - Score"])

sort_first_dis = np.sort(df["First Session: Discordant - Score"])
norm_first_dis = norm.pdf(sort_first_dis, mean_first_dis, sd_first_dis)
#plt.plot(sort_first_dis, norm_first_dis)


mean_second_conc = st.mean(df["Second Session: Concordant - Score"])
sd_second_conc = st.stdev(df["Second Session: Concordant - Score"])

sort_second_conc = np.sort(df["Second Session: Concordant - Score"])
norm_second_conc = norm.pdf(sort_second_conc, mean_second_conc, sd_second_conc)


mean_second_dis = st.mean(df["Second Session: Discordant - Score"])
sd_second_dis = st.stdev(df["Second Session: Discordant - Score"])

sort_second_dis = np.sort(df["Second Session: Discordant - Score"])
norm_second_dis = norm.pdf(sort_second_dis, mean_second_dis, sd_second_dis)

trace_first_conc = go.Scatter(x=sort_first_conc, y=norm_first_conc, marker=dict(opacity=0), name="First Session: Concordant")

trace_first_dis = go.Scatter(x=sort_first_dis, y=norm_first_dis, marker=dict(opacity=0), name="First Session: Discordant")
trace_second_conc = go.Scatter(x=sort_second_conc, y=norm_second_conc, marker=dict(opacity=0), name="Second Session: Concordant")
trace_second_dis = go.Scatter(x=sort_second_dis, y=norm_second_dis, marker=dict(opacity=0), name="Second Session: Discordant")
#fill='tozeroy'
data = [trace_first_conc, trace_first_dis, trace_second_conc, trace_second_dis]
fig = go.Figure(data=data, layout={"title":"Interference Score Distribution", "xaxis_title":"Reaction Time in ms", "yaxis_title":"Probability"})

fig.add_shape(x0=mean_first_conc, y0=0, x1=mean_first_conc, y1=norm_first_conc[len(norm_first_conc)//2+1], line_color="blue", line_width=1, opacity=0.75)
fig.add_shape(x0=mean_first_dis, y0=0, x1=mean_first_dis, y1=norm_first_dis[len(norm_first_dis)//2], line_color="red",line_width=1, opacity=0.75)
fig.add_shape(x0=mean_second_conc, y0=0, x1=mean_second_conc, y1=norm_second_conc[len(norm_second_conc)//2+1], line_color="green", line_width=1, opacity=0.75)
fig.add_shape(x0=mean_second_dis, y0=0, x1=mean_second_dis, y1=norm_second_dis[len(norm_second_dis)//2], line_color="purple",line_width=1, opacity=0.75)
fig.show()
