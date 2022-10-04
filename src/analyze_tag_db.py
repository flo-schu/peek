import pandas as pd
from matplotlib import pyplot as plt

tags = pd.read_csv("./data/tag_db.csv")
# remove duplicates
duplicates = tags.duplicated(subset=["id","img_id","img_date","area"], keep="last")
tags = tags.loc[~duplicates, :].copy()

# processing and querying
tags.loc[:, "lw_ratio"] = tags.loc[:, 'len_major'] / tags.loc[:, 'len_minor']
tags = tags.query("analysis == 'moving_edge'").copy()

tags.hist(column="lw_ratio", by="label")
plt.show()
# summarizing
tags = tags.groupby(['label'])
t_mean = tags.mean().loc[:,  ("height", "width","len_major", "len_minor","area","lw_ratio","angle")]
t_max = tags.max().loc[:,    ("height", "width","len_major", "len_minor","area","lw_ratio","angle")]
t_min = tags.min().loc[:,    ("height", "width","len_major", "len_minor","area","lw_ratio","angle")]
t_median = tags.median().loc[:, ("height", "width","len_major", "len_minor","area","lw_ratio","angle")]
t_q95 = tags.quantile(.80).loc[:, ("height", "width","len_major", "len_minor","area","lw_ratio","angle")]
t_q05 = tags.quantile(.20).loc[:, ("height", "width","len_major", "len_minor","area","lw_ratio","angle")]

