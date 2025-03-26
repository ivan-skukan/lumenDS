import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

class BasicWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Basic Qt Window")
        self.setGeometry(100, 100, 800, 600)  # (x, y, width, height)

        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create buttons
        left_button = QPushButton("Left")
        right_button = QPushButton("Right")

        # Add buttons to the layout
        layout.addWidget(left_button)
        layout.addWidget(right_button)

        # Connect buttons to slots (optional)
        left_button.clicked.connect(lambda: print("Left button clicked"))
        right_button.clicked.connect(lambda: print("Right button clicked"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BasicWindow()
    window.show()
    sys.exit(app.exec())