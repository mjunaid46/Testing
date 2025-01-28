import pickle
from pprint import pprint  # For pretty printing large or nested data

# Specify the path to your .pkl file
file_path = "C:/Users/dell/Desktop/task/order_state.pkl"

# Load and display the .pkl file content
try:
    with open(file_path, "rb") as file:
        data = pickle.load(file)
    print("Type of data:", type(data))
    print("\nContent:")
    pprint(data)
except Exception as e:
    print("Error while reading the .pkl file:", e)
