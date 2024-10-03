import tkinter as tk
import numpy as np
from scipy.optimize import minimize


MAX_RADIUS = 25  
MAX_SIGNAL = 100  
MIN_SIGNAL = -100  

anchors = []  
chip_position = None  
canvas_size = 400  
anchor_count = 3  

def signal_to_distance(signal):
    return MAX_RADIUS * (MAX_SIGNAL - signal) / (MAX_SIGNAL - MIN_SIGNAL)

def calculate_weights(signals):
    weights = np.abs(signals) / np.sum(np.abs(signals))
    return weights

def weighted_trilateration(anchors, estimated_distances, weights):
    def error_function(position):
        estimated_distances_from_position = np.linalg.norm(anchors - position, axis=1)
        weighted_errors = weights * (estimated_distances_from_position - estimated_distances) ** 2
        return np.sum(weighted_errors)

    initial_guess = np.array([canvas_size / 2, canvas_size / 2])
    result = minimize(error_function, initial_guess, method='BFGS')
    return result.x


def simulate_signal_strength(anchor, position):
    distance = np.linalg.norm(anchor - position)
    signal_strength = MAX_SIGNAL - (distance / MAX_RADIUS) * (MAX_SIGNAL - MIN_SIGNAL)
    return signal_strength


def place_point(event):
    global chip_position

    
    if len(anchors) < anchor_count:
        x, y = event.x, event.y
        anchors.append([x, y])
        canvas.create_oval(x-5, y-5, x+5, y+5, fill='blue')
        canvas.create_text(x+10, y, text=f"A{len(anchors)}", anchor=tk.W)
        
        
        canvas.create_oval(x - MAX_RADIUS*8, y - MAX_RADIUS*8, x + MAX_RADIUS*8, y + MAX_RADIUS*8, outline='blue', dash=(2, 2))

        if len(anchors) == anchor_count:
            status_label.config(text="Click anywhere to place the chip (red) and estimate the position.")

    
    else:
        if chip_position is not None:
            chip_position = None
        chip_position = np.array([event.x, event.y])

        canvas.create_oval(event.x-5, event.y-5, event.x+5, event.y+5, fill='red')
        canvas.create_text(event.x+10, event.y, text="Chip", anchor=tk.W)

        measured_signals = np.array([simulate_signal_strength(anchor, chip_position) for anchor in anchors])

        estimated_distances = np.array([signal_to_distance(signal) for signal in measured_signals])

        weights = calculate_weights(measured_signals)

        estimated_position = weighted_trilateration(np.array(anchors), estimated_distances, weights)

        canvas.create_oval(estimated_position[0]-5, estimated_position[1]-5, estimated_position[0]+5, estimated_position[1]+5, outline='green', width=2)
        canvas.create_text(estimated_position[0]+10, estimated_position[1], text="Estimated", anchor=tk.W, fill='green')

        status_label.config(text=f"Chip placed. Estimated position is in green.{estimated_position}")

def reset():
    global anchors, chip_position
    anchors = []
    chip_position = None
    canvas.delete("all")
    status_label.config(text="Place 3 machines (blue).")


root = tk.Tk()
root.title("Mod_trilateration_algorithm")


canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg='white')
canvas.pack()


canvas.bind("<Button-1>", place_point)  


instructions = tk.Label(root, text="Click to place 3 machines (blue). Than click to place the chip.")
instructions.pack()


status_label = tk.Label(root, text="Place 3 machines (blue).")
status_label.pack()


reset_button = tk.Button(root, text="Reset", command=reset)
reset_button.pack()


root.mainloop()
