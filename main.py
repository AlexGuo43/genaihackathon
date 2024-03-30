# import TensorFlow library
import tensorflow as tf

# follow tutorial
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv('Churn.csv')
X = pd.get_dummies(df.drop(['Churn','Customer ID'], axis=1))
y = df['Churn'].apply(lambda x: 1 if x=='Yes' else 0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)
X_train.head()
print(y_train.head())

# import dependencies
from tensorflow.keras.models import Sequential, load_model  # sequential: core model class; load_model: reload model from memory later on
from tensorflow.keras.layers import Dense   # fully connected layer in our neural network
from sklearn.metrics import accuracy_score  # accuracy score is metric we use to measure how well our metric is performing

# # build & compile model
# model = Sequential()    #instantiating sequential class
# model.add(Dense(units=32, activation='relu', input_dim=len(X_train.columns)))   # two hidden layers --> first one has 32 neurons, relu activation converts output to a min of zero & unlim upward value, input_dim is same # of dimensions in dataframe 
# model.add(Dense(units=64, activation='relu'))
# model.add(Dense(units=1, activation='sigmoid')) # sigmoid: takes output of this layer and converts between 1 or 0

# model.compile(loss='binary_crossentropy', optimizer='sgd', metrics=['accuracy'])    # tell tensorflow how we wanna train our model (battleship): loss-->sum of how far our estimations are from sinking a battleship, optimizer-->how we choose to search through & find battleships, metrics--> determins how well model performs

# # fit, predict & evaluate
# model.fit(X_train, y_train, epochs=200, batch_size=32) # epoch setting: high epoch = training for long means more accurate model but can lead to overfitting

# y_hat = model.predict(X_test)
# y_hat = [0 if val < 0.5 else 1 for val in y_hat] # set output to produce 0 or 1

# print(y_hat)
# print(accuracy_score(y_test, y_hat))

# # save & reload
# model.summary()
# model.save('tfmodel.keras')
# del model
# model = load_model('tfmodel.keras')

model = load_model('tfmodel.keras')
y_hat = model.predict(X_test)
y_hat = [0 if val < 0.5 else 1 for val in y_hat] # set output to produce 0 or 1

print(y_hat)
print(accuracy_score(y_test, y_hat))
print(model.summary())