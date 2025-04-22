from numpy import loadtxt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras import Input


# load the dataset
dataset = loadtxt('simplekerasexample/pima-indians-diabetes.csv', delimiter=',')

# split into input (X) and output (y) variablesde
X = dataset[:,0:8]
y = dataset[:,8]

# define the keras model
model = Sequential([
    Input(shape=(8,)),
    Dense(12, activation='relu'),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')
])

# compile the keras model
model.compile(
    loss=BinaryCrossentropy(),
    optimizer=Adam(),
    metrics=["accuracy"]
)

# fit the keras model on the dataset
model.fit(X, y, epochs=10, batch_size=10, verbose=1)

# evaluate the keras model
_, accuracy = model.evaluate(X, y, verbose=1)
print('Accuracy: %.2f' % (accuracy*100))

# make class predictions with the model
predictions = (model.predict(X, verbose=0) > 0.5).astype(int)

# summarize the first 5 cases
for i in range(5):
    pred = int(predictions[i].item())
    expected = int(y[i])
    print(f"{X[i].tolist()} => {pred} (expected {expected})")
