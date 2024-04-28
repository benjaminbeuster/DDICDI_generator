#!/usr/bin/env python
# coding: utf-8
import pandas as pd
df = pd.read_parquet("https://ess-api.sikt.no/v1/data/10.21338/ess9e03_2?user_id=1234c034-4ff9-11e5-885d-feff819cdc9f")
df.head()


