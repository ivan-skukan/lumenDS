import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QKeyEvent, QAction, QKeySequence, QPainter
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QStyle,
                             QWidget, QFileDialog, QMessageBox, QLabel, QHBoxLayout, QToolBar, QStyleOption)
from typing import Union, Optional, Callable

# Monk Skin Tone Color Palette (10 squares)
monk_skin_tone_colors = [
    "#8D5524",  # Darkest brown
    "#A76C4E",  # Dark brown
    "#C68642",  # Medium brown
    "#E0A060",  # Light brown
    "#F1C27D",  # Light skin
    "#FFDBAC",  # Lightest skin
    "#F6CEB9",  # Pale skin
    "#E7C697",  # Beige
    "#D2B48C",  # Tan
    "#C2B280"  # Warm beige
]
# Fitzpatrick Skin Type Color Palette (6 squares)
fitzpatrick_colors = [
    "#FFE5B4",  # Type I: Very pale, always burns
    "#F4A460",  # Type II: Fair, burns easily
    "#D2691E",  # Type III: Medium, sometimes tans
    "#8B4513",  # Type IV: Olive, rarely burns
    "#5D4037",  # Type V: Dark brown, never burns
    "#3E2723"  # Type VI: Very dark brown/black, never burns
]

class ColorWidget(QWidget):
    def __init__(self, color_hex, onColorClick: Callable[["ColorWidget"], None], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.onColorClick = onColorClick
        self.is_selected = False
        self.color_hex = color_hex  # Store color reference
        self.setMinimumHeight(100)

        self.update_style()

    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, o, p, self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_selected = not self.is_selected
            self.update_style()
            self.onColorClick(self)

    def update_style(self):
        if self.is_selected:
            # More prominent selection indication
            style = f"""
               background-color: {self.color_hex};
               border: 4px solid white;
               outline: 3px solid black;
               """
        else:
            style = f"""
               background-color: {self.color_hex};
               border: 1px solid black;
               """
        self.setStyleSheet(style)

    def select(self):
        self.is_selected = True
        self.update_style()

    def deselect(self):
        self.is_selected = False
        self.update_style()


class ColorSamplesLayout(QHBoxLayout):
    def __init__(self, colors, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.color_widgets = []
        self.selected_widget = None

        for color_hex in colors:
            color_widget = ColorWidget(color_hex, self.handle_color_click)
            self.color_widgets.append(color_widget)
            self.addWidget(color_widget)

    def handle_color_click(self, clicked_widget):
        for widget in self.color_widgets:
            if widget != clicked_widget:
                widget.deselect()

        self.selected_widget = clicked_widget

    def get_selected_index(self) -> Optional[int]:
        if not self.selected_widget:
            return None

        return self.color_widgets.index(self.selected_widget)

    def reset(self):
        self.selected_widget = None
        for w in self.color_widgets:
            w.deselect()

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

        select_folder_action = QAction("Select &Image Folder", self)
        select_folder_action.setShortcut(QKeySequence("Ctrl+i"))
        select_folder_action.triggered.connect(self.select_image_folder)
        toolbar.addAction(select_folder_action)

        create_annotations_file_action = QAction("Create Annotations File", self)
        create_annotations_file_action.setShortcut(QKeySequence("Ctrl+c"))
        create_annotations_file_action.triggered.connect(self.create_annotations_file)
        toolbar.addAction(create_annotations_file_action)

        open_annotations_file_action = QAction("Open Annotations File", self)
        open_annotations_file_action.setShortcut(QKeySequence("Ctrl+o"))
        open_annotations_file_action.triggered.connect(self.open_annotations_file)
        toolbar.addAction(open_annotations_file_action)

        # Image display area
        self.image_label = QLabel("Select a folder to start")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.image_label, 10)

        # Image count display
        self.image_count_label = QLabel()
        self.image_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.image_count_label, 1)

        # Monk scale
        self.monk_skin_tone_picker = ColorSamplesLayout(monk_skin_tone_colors)
        main_layout.addLayout(self.monk_skin_tone_picker)

        main_layout.addSpacing(20)

        self.fitzpatrick_skin_tone_picker = ColorSamplesLayout(fitzpatrick_colors)
        main_layout.addLayout(self.fitzpatrick_skin_tone_picker)

        # Image tracking variables
        self.image_names = []
        self.current_image_index = 0
        self.current_images_folder_path = None

        self.annotations_file_path = None


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

    def create_annotations_file(self):
        """
        Open a file dialog to let user choose location and name for annotations file.
        Provides robust error handling and user feedback.
        """
        # First, check if an image folder is selected
        if not hasattr(self, 'current_images_folder_path') or not self.current_images_folder_path:
            QMessageBox.warning(
                self,
                "No Image Folder",
                "Please select an image folder first before creating an annotations file."
            )
            return

        # Open file dialog to save annotations file
        try:
            # Suggest a default filename based on the image folder
            default_filename = os.path.basename(self.current_images_folder_path) + "_annotations.csv"

            # Open save file dialog with suggested filename
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Create Annotations File",
                default_filename,  # Default filename
                "CSV Files (*.csv)"
            )

            # If user cancels file selection
            if not file_path:
                return

            # Validate file path
            if not file_path:
                raise ValueError("No file path selected")

            # Ensure file has an extension
            if not file_path.lower().endswith(".csv"):
                file_path += '.csv'

            # Attempt to create (or overwrite) the file
            with open(file_path, 'w') as f:
                pass

            self.annotations_file_path = file_path

            # Provide positive user feedback
            QMessageBox.information(
                self,
                "Success",
                f"Annotations file created successfully:\n{file_path}"
            )

        except PermissionError:
            QMessageBox.critical(
                self,
                "Permission Error",
                "You do not have permission to write to this location. Please choose another folder."
            )
        except OSError as e:
            QMessageBox.critical(
                self,
                "File Creation Error",
                f"Could not create file. Error: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Unexpected Error",
                f"An unexpected error occurred: {str(e)}"
            )

    def open_annotations_file(self):
        pass

    def display_image(self, index: int):
        image_name = self.image_names[index]
        image_path = os.path.join(self.current_images_folder_path, image_name)
        pixmap = QPixmap(image_path)

        # Scale image to fit window while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)

        # Update image count label
        image_count_text = f"Image {self.current_image_index + 1} of {len(self.image_names)}: {image_name}"
        self.image_count_label.setText(image_count_text)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle left and right arrow key navigation"""
        if not self.image_names:
            return

        are_colors_selected = self.monk_skin_tone_picker.get_selected_index() is not None and self.fitzpatrick_skin_tone_picker.get_selected_index() is not None

        if event.key() == Qt.Key.Key_Left:
            if not are_colors_selected:
                QMessageBox.warning(self, "Colors not selected", "You must select both colors")
                return

            # Move to previous image
            self.current_image_index = (self.current_image_index - 1) % len(self.image_names)
            self.display_image(self.current_image_index)
            self.reset_both_color_pickers()

        elif event.key() == Qt.Key.Key_Right:
            if not are_colors_selected:
                QMessageBox.warning(self, "Colors not selected", "You must select both colors")
                return

            # Move to next image
            self.current_image_index = (self.current_image_index + 1) % len(self.image_names)
            self.display_image(self.current_image_index)
            self.reset_both_color_pickers()

    def reset_both_color_pickers(self):
        self.monk_skin_tone_picker.reset()
        self.fitzpatrick_skin_tone_picker.reset()

def main():
    app = QApplication(sys.argv)
    window = Annotator()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()