import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QFileDialog, QMessageBox, QLabel, QHBoxLayout, QToolBar)
from PyQt6.QtGui import QPixmap, QKeyEvent, QAction, QKeySequence
from PyQt6.QtCore import Qt


class Annotator(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up full-screen window
        self.setWindowTitle("BEAST ANNOTATOR")
        self.showMaximized()  # Full-screen mode

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        select_folder_action = QAction("Select Image Folder", self)
        select_folder_action.setShortcut(QKeySequence("Ctrl+o"))
        select_folder_action.triggered.connect(self.select_image_folder)
        toolbar.addAction(select_folder_action)

        # Image display area
        self.image_label = QLabel("Select a folder to start")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.image_label, 10)

        # Image count display
        self.image_count_label = QLabel()
        self.image_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.image_count_label, 1)

        # Image tracking variables
        self.image_names = []
        self.current_image_index = 0
        self.current_images_folder_path = None


    def select_image_folder(self):
        """Open folder picker and validate image files"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Image Folder")

        if not folder_path:
            QMessageBox.warning(self, "Error", "No path selected")
            return

        self.current_images_folder_path = folder_path

        # Find .jpg files
        self.image_names = [f for f in os.listdir(folder_path)
                            if f.lower().endswith('.jpg')]

        # Validate image files
        if not self.image_names:
            QMessageBox.warning(self, "Error", "No JPG images found in the selected folder")
            return

        # Set first image
        self.current_image_index = 0
        self.display_image(self.current_image_index)

    def display_image(self, index: int):
        image_path = os.path.join(self.current_images_folder_path, self.image_names[index])
        pixmap = QPixmap(image_path)

        # Scale image to fit window while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)

        # Update image count label
        image_count_text = f"Image {self.current_image_index + 1} of {len(self.image_names)}"
        self.image_count_label.setText(image_count_text)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle left and right arrow key navigation"""
        if not self.image_names:
            return

        if event.key() == Qt.Key.Key_Left:
            # Move to previous image
            self.current_image_index = (self.current_image_index - 1) % len(self.image_names)
            self.display_image(self.current_image_index)

        elif event.key() == Qt.Key.Key_Right:
            # Move to next image
            self.current_image_index = (self.current_image_index + 1) % len(self.image_names)
            self.display_image(self.current_image_index)


def main():
    app = QApplication(sys.argv)
    window = Annotator()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()