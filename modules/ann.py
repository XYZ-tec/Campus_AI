"""
modules/ann.py
==============
ANN Priority Prediction module.

The Perceptron is the binary baseline (urgent / not_urgent). The MLP is the
operational four-class model (low / normal / high / urgent). The training
examples are synthetic teaching examples generated from transparent scoring
rules because the handout does not provide a real labelled campus dataset.
ANN estimates priority only; Logic_KB remains responsible for permission.
"""

import math
import random

from core.constants import (
    CATEGORY_ENCODING, ROLE_ENCODING, PRIORITY_BINARY_LABELS,
    PRIORITY_CLASS_LABELS, FEATURE_ORDER,
)
from data.campus_graph import build_graph
from modules.search import ucs

TARGET_ROOMS = {
    "AI_Lab_Support": "AI_Lab",
    "Viva": "Seminar_Room",
    "Access": "AI_Lab",
    "Maintenance": "Science_Block",
    "Emergency_Help": "Medical_Center",
}


def sigmoid(value):
    """Convert a numeric value into a value between zero and one."""
    if value < -60:
        return 0.0
    if value > 60:
        return 1.0
    return 1.0 / (1.0 + math.exp(-value))


def estimate_distance(request):
    """Estimate walking distance from the user's location to the service area."""
    source = request.get("current_location", "")
    destination = TARGET_ROOMS.get(request.get("category", ""), "AI_Lab")
    graph = build_graph(weighted=True)
    if source not in graph or destination not in graph:
        return 1
    result = ucs(graph, source, destination)
    return result["cost"] if result["path"] else 10


def build_feature_vector(request, eligibility=True):
    """Encode request information in the fixed handout feature order."""
    role = ROLE_ENCODING.get(request.get("role", "student"), 0)
    request_type = CATEGORY_ENCODING.get(request.get("category", "AI_Lab_Support"), 0)
    severity = int(request.get("severity", 1) or 1)
    time_sensitivity = int(request.get("time_sensitivity", 1) or 1)
    crowd_level = int(request.get("crowd_level", 1) or 1)
    distance = estimate_distance(request)
    vector = [role, request_type, severity, time_sensitivity,
              crowd_level, distance, 1 if eligibility else 0]
    return vector


def normalize_features(vector):
    """Scale encoded features to a similar numeric range for ANN training."""
    return [
        vector[0] / 2.0,
        vector[1] / 4.0,
        vector[2] / 10.0,
        vector[3] / 10.0,
        vector[4] / 10.0,
        min(vector[5], 15) / 15.0,
        float(vector[6]),
    ]


def priority_score(vector):
    """Create a transparent synthetic training label from urgency indicators."""
    severity = vector[2]
    time_sensitivity = vector[3]
    crowd_level = vector[4]
    distance = vector[5]
    return (0.38 * severity + 0.32 * time_sensitivity
            + 0.15 * crowd_level + 0.10 * min(distance, 10)
            + 0.05 * vector[1])


def make_training_data():
    """Generate reproducible synthetic examples for the demonstration models."""
    random.seed(17)
    features = []
    binary_labels = []
    class_labels = []
    for index in range(600):
        role = random.randint(0, 2)
        category = random.randint(0, 4)
        severity = random.randint(1, 10)
        time_sensitivity = random.randint(1, 10)
        crowd_level = random.randint(1, 10)
        distance = random.randint(1, 12)
        eligibility = random.randint(0, 1)
        vector = [role, category, severity, time_sensitivity,
                  crowd_level, distance, eligibility]
        score = priority_score(vector)
        class_label = 0 if score < 3.6 else 1 if score < 5.2 else 2 if score < 7.5 else 3
        features.append(normalize_features(vector))
        class_labels.append(class_label)
        binary_labels.append(1 if score >= 6.5 else 0)
    return features, binary_labels, class_labels


class Perceptron:
    """A small binary perceptron trained with the perceptron update rule."""

    def __init__(self, input_size=7):
        self.weights = [0.0] * input_size
        self.bias = 0.0

    def predict_value(self, features):
        """Return the weighted sum used by the binary decision boundary."""
        return sum(self.weights[i] * features[i] for i in range(len(features))) + self.bias

    def predict(self, features):
        """Return 1 for urgent and 0 for not urgent."""
        return 1 if self.predict_value(features) >= 0 else 0

    def train(self, features, labels, epochs=30, learning_rate=0.08):
        """Adjust weights whenever a training example is classified incorrectly."""
        for epoch in range(epochs):
            for row, expected in zip(features, labels):
                predicted = self.predict(row)
                error = expected - predicted
                for index in range(len(self.weights)):
                    self.weights[index] += learning_rate * error * row[index]
                self.bias += learning_rate * error


class MLP:
    """Neural network from the MLP diagram: 7 inputs, hidden layer 1 (4 neurons),
    hidden layer 2 (3 neurons) and 4 outputs (low / normal / high / urgent)."""

    def __init__(self, sizes=(7, 4, 3, 4)):
        random.seed(29)
        self.weights = []
        self.biases = []
        for layer in range(len(sizes) - 1):
            self.weights.append([[random.uniform(-0.5, 0.5) for _ in range(sizes[layer])]
                                 for _ in range(sizes[layer + 1])])
            self.biases.append([0.0] * sizes[layer + 1])

    def layer_totals(self, layer, inputs):
        """Weighted sum plus bias for every neuron in one layer."""
        totals = []
        for neuron, weights in enumerate(self.weights[layer]):
            total = sum(weights[i] * inputs[i] for i in range(len(inputs)))
            totals.append(total + self.biases[layer][neuron])
        return totals

    def forward(self, features):
        """Pass the features through both hidden layers (sigmoid) and the
        output layer (softmax). Returns every layer's outputs."""
        hidden1 = [sigmoid(value) for value in self.layer_totals(0, features)]
        hidden2 = [sigmoid(value) for value in self.layer_totals(1, hidden1)]
        logits = self.layer_totals(2, hidden2)
        maximum = max(logits)
        exponents = [math.exp(value - maximum) for value in logits]
        probabilities = [value / sum(exponents) for value in exponents]
        return [features, hidden1, hidden2, probabilities]

    def predict_probabilities(self, features):
        """Return the four priority-class probabilities."""
        return self.forward(features)[-1]

    def predict(self, features):
        """Return the index of the most likely priority class."""
        probabilities = self.predict_probabilities(features)
        return max(range(len(probabilities)), key=lambda index: probabilities[index])

    def train(self, features, labels, epochs=150, learning_rate=0.3):
        """Train with backpropagation and cross-entropy: compute each layer's
        error from the output backwards, then update weights and biases."""
        for epoch in range(epochs):
            for row, label in zip(features, labels):
                outputs = self.forward(row)
                errors = list(outputs[-1])
                errors[label] -= 1.0                     # softmax + cross-entropy error
                for layer in range(len(self.weights) - 1, -1, -1):
                    inputs = outputs[layer]
                    previous_errors = [0.0] * len(inputs)
                    for neuron in range(len(errors)):
                        for i in range(len(inputs)):
                            previous_errors[i] += errors[neuron] * self.weights[layer][neuron][i]
                            self.weights[layer][neuron][i] -= learning_rate * errors[neuron] * inputs[i]
                        self.biases[layer][neuron] -= learning_rate * errors[neuron]
                    errors = [previous_errors[i] * inputs[i] * (1 - inputs[i])   # sigmoid derivative
                              for i in range(len(inputs))]


_TRAINING_FEATURES, _BINARY_LABELS, _CLASS_LABELS = make_training_data()
_TRAINING_FEATURES = _TRAINING_FEATURES
PERCEPTRON = Perceptron()
PERCEPTRON.train(_TRAINING_FEATURES, _BINARY_LABELS)
MLP_MODEL = MLP()
MLP_MODEL.train(_TRAINING_FEATURES, _CLASS_LABELS)


def predict_priority(request, eligibility=True):
    """Return Perceptron baseline and MLP operational priority predictions."""
    raw_vector = build_feature_vector(request, eligibility)
    features = normalize_features(raw_vector)
    binary = PERCEPTRON.predict(features)
    probabilities = MLP_MODEL.predict_probabilities(features)
    final_class = max(range(4), key=lambda index: probabilities[index])
    return {
        "binary_priority": PRIORITY_BINARY_LABELS[binary],
        "final_priority": PRIORITY_CLASS_LABELS[final_class],
        "confidence": round(probabilities[final_class], 2),
        "feature_order": list(FEATURE_ORDER),
        "feature_vector": raw_vector,
        "model": "MLP",
    }
