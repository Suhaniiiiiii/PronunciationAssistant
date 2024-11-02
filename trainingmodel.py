import os
import numpy as np
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split

# Load the dataset
data_dir = 'C:/Users/Suhani Gupta/Downloads/LJSpeech-1.1/wavs'

if os.path.exists(data_dir):
    print(f"Success: The path {data_dir} exists. Proceeding with loading files.")
else:
    raise ValueError(f"Error: The path {data_dir} does not exist.")

# Mock data loading function (replace this with actual data loading logic)
# Assuming you have extracted features from your audio files into a numpy array format
# X should be the features, y should be the labels
X = np.random.rand(1000, 100)  # Example feature array (1000 samples, 100 features each)
y = np.random.randint(2, size=(1000,))  # Example binary labels (0 or 1)

# Split data into training and testing sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the model
model = Sequential()

# Input layer and hidden layers
model.add(Dense(128, activation='relu', input_shape=(X_train.shape[1],)))
model.add(Dropout(0.5))  # Prevent overfitting
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))

# Output layer with sigmoid for binary classification
model.add(Dense(1, activation='sigmoid'))

# Compile the model with binary crossentropy loss and Adam optimizer
model.compile(optimizer=Adam(learning_rate=0.001), 
              loss='binary_crossentropy', 
              metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, 
          validation_data=(X_val, y_val), 
          epochs=10, 
          batch_size=32)

# Save the model in the recommended Keras format
model.save('pronunciation_model.keras')

print("Model training complete and saved as 'pronunciation_model.keras'")
