import os
import sys
import json
import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from generators.powerpoint import PowerpointGenerator

#from trollette import Trollette
#from data_farmer import DataFarmer
#from image_farmer import ImageFarmer
#from deck_generator import DeckGenerator


class QImageButton(QLabel):

    pushed = pyqtSignal()

    def __init(self, parent):
        QLabel.__init__(self, parent)

    def mousePressEvent(self, ev):
        self.pushed.emit()


class TitleSelectionWidget(QDialog):
    def __init__(self, parent=None, titles=list()):
        QDialog.__init__(self, parent)

        self.parent = parent

        self.vbox = QVBoxLayout()

        self.titles = titles
        self.talk_button = QPushButton(self.titles[0])
        self.vbox.addWidget(self.talk_button)
        self.talk_button.clicked[bool].connect(self.title_chosen)

        self.nope_count = 0

        pixmap = QPixmap(os.path.join("Resources", "lana_nope_600.png"))
        self.nope_button = QImageButton(self)
        self.nope_button.setPixmap(pixmap)
        self.nope_button.setMask(pixmap.mask())
        self.nope_button.pushed.connect(self.nooooope)

        self.vbox.addWidget(self.nope_button)

        self.setLayout(self.vbox)

    def title_chosen(self, pressed):
        source = self.sender()
        self.parent.current_talk = source.text()
        self.close()

    def nooooope(self):
        self.nope_count += 1

        if self.nope_count >= 2:
            self.nope_button.setParent(None)

        if self.nope_count < 3:
            self.talk_button.setText(self.titles[self.nope_count])


class TrolletteGeneratorGUI(QMainWindow):

    def __init__(self):
        super().__init__()

        # Data
        self.generator = PowerpointGenerator(self.update_console)
        with open("terms.json", "r") as f:
            self.terms = json.load(f)

        self.troll_image = os.path.join("Resources", "trollerate.png")

        self.used_talks = []

        self.init_ui()

        self.current_talk = ""

    def update_console(self, message):
        self.console.append(message)
        self.console.moveCursor(QTextCursor.End)
        QApplication.processEvents()

    def create_widgets(self):
        self.weight_sliders = {}
        for weight in list(self.generator.slide_weights.weights.keys()):
            self.weight_sliders[weight] = QSlider(Qt.Horizontal)
            self.weight_sliders[weight].setMinimum(0)
            self.weight_sliders[weight].setMaximum(100)
            self.weight_sliders[weight].setValue(self.generator.slide_weights.weights[weight])
            self.weight_sliders[weight].valueChanged[int].connect(self.update_slide_weight)
            self.weight_sliders[weight].slide_type = weight

    def update_slide_weight(self, value):
        sending_slider = self.sender()
        self.generator.slide_weights.weights[sending_slider.slide_type] = value


    def init_ui(self):

        self.create_widgets()


        self.main_widget = QWidget()
        self.main_vbox = QVBoxLayout()

        pixmap = QPixmap(os.path.join("Resources", "cage.png"))
        self.troll_button = QImageButton(self)
        self.troll_button.setPixmap(pixmap)
        self.troll_button.setMask(pixmap.mask())
        self.troll_button.pushed.connect(self.start_troll)
        self.main_vbox.addWidget(self.troll_button, alignment=Qt.AlignCenter)

        self.speaker_selection = QComboBox()
        self.speaker_selection.addItem("")
        self.speaker_selection.addItems(self.terms["speakers"])

        self.slider_label = QLabel("Slide Type Weights")
        self.slider_grid = QGridLayout()
        slider_count = 0
        for weight in list(self.weight_sliders.keys()):
            self.slider_grid.addWidget(QLabel(weight), slider_count, 0)
            self.slider_grid.addWidget(self.weight_sliders[weight], slider_count, 1)
            slider_count += 1
        self.main_vbox.addWidget(self.slider_label)
        self.main_vbox.addLayout(self.slider_grid)

        self.speaker_hbox = QHBoxLayout()
        self.speaker_hbox.addWidget(QLabel("Speaker:"))
        self.speaker_hbox.addWidget(self.speaker_selection)

        self.main_vbox.addLayout(self.speaker_hbox)

        # Widgets
        self.console = QTextBrowser()
        self.console.setLineWrapMode(QTextEdit.NoWrap)
        self.main_vbox.addWidget(self.console)

        self.main_widget.setLayout(self.main_vbox)
        self.setCentralWidget(self.main_widget)

        # Handle Widgets
        self.setGeometry(100, 100, 800, 500)
        self.setWindowTitle('Trollette')
        self.show()

    def get_talk_choices(self, count):
        picks = set()
        ts = list(self.terms["full_talk_titles"].keys())
        while len(picks) < count:
            picks.add(random.choice(ts))

        return list(picks)

    # UI Events
    def start_troll(self):

        self.current_talk = ""

        title_chooser = TitleSelectionWidget(self, self.get_talk_choices(3))
        title_chooser.setGeometry(QRect(100, 100, 400, 200))
        title_chooser.exec_()

        presenter = self.speaker_selection.currentText()
        if not presenter:
            presenter = random.choice(self.terms["fake_speakers"])

        if self.current_talk:
            slide_path = self.generator.generate_slide_deck(self.current_talk, presenter, 12, 15)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = TrolletteGeneratorGUI()
    sys.exit(app.exec_())
