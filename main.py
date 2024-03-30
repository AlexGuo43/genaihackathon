# import TensorFlow library
import tensorflow as tf

# follow tutorial
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv('Churn.csv')
x = pd.get_dummies(df.drop(['Churn','Customer ID'], axis=1))
y = df['Churn'].apply(lambda x: 1 if x=='Yes' else 0)

x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=.2)
x_train.head()
y_train.head()

print('no bugs so far prayge')