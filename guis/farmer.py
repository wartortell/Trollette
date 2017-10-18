import os
import sys
import json
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from farmers.images import ImageFarmer
from farmers.gifs import GifFarmer
from helpers import SlideWeights


class TrolletteFarmerGUI(QMainWindow):
    
    def __init__(self):
        super().__init__()

        # Data
        #self.troll = Trollette()
        with open("terms.json", "r") as f:
            self.terms = json.load(f)

        # Widgets
        self.console = QTextBrowser()

        self.slide_weights = SlideWeights()

        # Set up the trollette console logger
        #self.troll.console = self.update_console

        #self.data_farmer = DataFarmer(self.update_console)
        self.image_farmer = ImageFarmer(self.update_console)
        self.gif_farmer = GifFarmer(self.update_console)

        self.init_ui()

    def create_menu(self):
        self.exit_action = QAction(QIcon(os.path.join("Resources", "power.png")), 'Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.triggered.connect(qApp.quit)

        self.troll_action = QAction(QIcon(os.path.join("Resources", "cage.png")), 'Troll', self)
        self.troll_action.setShortcut('Ctrl+T')
        self.troll_action.triggered.connect(self.start_troll)

        self.farm_image_action = QAction(QIcon(os.path.join("Resources", "turkey.png")), 'Farm Images', self)
        self.farm_image_action.setShortcut('Ctrl+I')
        self.farm_image_action.triggered.connect(self.farm_images)

        self.farm_gif_action = QAction(QIcon(os.path.join("Resources", "tractor.png")), 'Farm Gifs', self)
        self.farm_gif_action.setShortcut('Ctrl+G')
        self.farm_gif_action.triggered.connect(self.farm_gifs)

        self.farm_data_action = QAction(QIcon(os.path.join("Resources", "farmer.png")), 'Farm Data', self)
        self.farm_data_action.setShortcut('Ctrl+D')
        self.farm_data_action.triggered.connect(self.farm_data)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.setIconSize(QSize(100, 100))
        self.toolbar.addAction(self.troll_action)
        self.toolbar.addAction(self.farm_data_action)
        self.toolbar.addAction(self.farm_image_action)
        self.toolbar.addAction(self.farm_gif_action)
        self.addToolBarBreak()
        self.toolbar.addAction(self.exit_action)

    def create_selections(self):
        self.topic_label = QLabel("Talk Titles")
        self.topic_dropdown = QComboBox()
        self.topic_dropdown.addItems(self.terms["talk_titles"])
        self.topic_entry = QLineEdit()
        self.topic_add = QPushButton("Add Title")
        self.topic_add.term = "talk_titles"
        self.topic_add.dropdown = self.topic_dropdown
        self.topic_add.clicked.connect(self.add_entry)

        self.speaker_label = QLabel("Speakers")
        self.speaker_dropdown = QComboBox()
        self.speaker_dropdown.addItems(self.terms["speakers"])
        self.speaker_entry = QLineEdit()
        self.speaker_add = QPushButton("Add Speaker")
        self.speaker_add.term = "speakers"
        self.speaker_add.dropdown = self.speaker_dropdown
        self.speaker_add.clicked.connect(self.add_entry)

        self.image_label = QLabel("Images")
        self.image_dropdown = QComboBox()
        self.image_dropdown.addItems(self.terms["image_searches"])
        self.image_entry = QLineEdit()
        self.image_add = QPushButton("Add Image Term")
        self.image_add.term = "image_searches"
        self.image_add.dropdown = self.image_dropdown
        self.image_add.clicked.connect(self.add_entry)

        self.gif_label = QLabel("GIFs")
        self.gif_dropdown = QComboBox()
        self.gif_dropdown.addItems(self.terms["giphy_searches"])
        self.gif_entry = QLineEdit()
        self.gif_add = QPushButton("Add GIF Term")
        self.gif_add.term = "giphy_searches"
        self.gif_add.dropdown = self.gif_dropdown
        self.gif_add.clicked.connect(self.add_entry)

        self.entry_senders = {"talk_titles": self.topic_entry, "speakers": self.speaker_entry,
                              "image_searches": self.image_entry, "giphy_searches": self.gif_entry}

        self.weight_sliders = {}
        for weight in list(self.slide_weights.weights.keys()):
            self.weight_sliders[weight] = QSlider(Qt.Horizontal)
            self.weight_sliders[weight].setMinimum(0)
            self.weight_sliders[weight].setMaximum(100)
            self.weight_sliders[weight].setValue(self.slide_weights.weights[weight])
            self.weight_sliders[weight].valueChanged[int].connect(self.update_slide_weight)
            self.weight_sliders[weight].slide_type = weight

    def create_layout(self):

        # Layout panels
        self.main_widget = QWidget()
        self.main_hbox = QHBoxLayout()
        self.left_vbox = QVBoxLayout()
        self.right_vbox = QVBoxLayout()

        # Add selection layouts
        self.topic_hbox = QHBoxLayout()
        self.topic_hbox.addWidget(self.topic_entry)
        self.topic_hbox.addWidget(self.topic_add)

        self.left_vbox.addWidget(self.topic_label)
        self.left_vbox.addWidget(self.topic_dropdown)
        self.left_vbox.addLayout(self.topic_hbox)

        self.speaker_hbox = QHBoxLayout()
        self.speaker_hbox.addWidget(self.speaker_entry)
        self.speaker_hbox.addWidget(self.speaker_add)

        self.left_vbox.addWidget(self.speaker_label)
        self.left_vbox.addWidget(self.speaker_dropdown)
        self.left_vbox.addLayout(self.speaker_hbox)

        self.image_hbox = QHBoxLayout()
        self.image_hbox.addWidget(self.image_entry)
        self.image_hbox.addWidget(self.image_add)

        self.left_vbox.addWidget(self.image_label)
        self.left_vbox.addWidget(self.image_dropdown)
        self.left_vbox.addLayout(self.image_hbox)

        self.gif_hbox = QHBoxLayout()
        self.gif_hbox.addWidget(self.gif_entry)
        self.gif_hbox.addWidget(self.gif_add)

        self.left_vbox.addWidget(self.gif_label)
        self.left_vbox.addWidget(self.gif_dropdown)
        self.left_vbox.addLayout(self.gif_hbox)

        self.left_vbox.addWidget(QLabel("Slide Type Weights"))
        self.slider_grid = QGridLayout()
        slider_count = 0
        for weight in list(self.weight_sliders.keys()):
            self.slider_grid.addWidget(QLabel(weight), slider_count, 0)
            self.slider_grid.addWidget(self.weight_sliders[weight], slider_count, 1)
            slider_count += 1
        self.left_vbox.addLayout(self.slider_grid)

        self.left_vbox.addStretch(1)

        #self.right_vbox.addStretch(1)
        #self.right_vbox.addWidget(self.console)

        self.main_hbox.addLayout(self.left_vbox)
        self.main_hbox.addWidget(self.console)

        self.main_widget.setLayout(self.main_hbox)
        self.setCentralWidget(self.main_widget)

    def update_console(self, message):
        self.console.append(message)
        self.console.moveCursor(QTextCursor.End)
        QApplication.processEvents()


    def init_ui(self):

        self.create_menu()

        self.create_selections()

        self.console.setFixedWidth(800)
        self.console.setLineWrapMode(QTextEdit.NoWrap)
        #self.console.setFixedHeight(400)

        self.create_layout()

        # Handle Widgets
        self.setGeometry(100, 100, 1200, 700)
        self.setWindowTitle('Trollette')
        self.show()

    # UI Events

    def add_entry(self):
        sender_term = self.sender().term

        entry_info = self.entry_senders[sender_term].text()
        if (not entry_info) or (entry_info in self.terms[sender_term]):
            return

        self.terms[sender_term].append(entry_info)
        with open("terms.json", "w") as f:
            json.dump(self.terms, f, indent=4)


        entry_dropdown = self.sender().dropdown
        entry_dropdown.clear()
        entry_dropdown.addItems(self.terms[sender_term])

    def update_slide_weight(self, value):
        sending_slider = self.sender()
        self.troll.slide_weights.weights[sending_slider.slide_type] = value

    def start_troll(self):
        pass

    def farm_images(self):
        all_terms = self.terms["image_searches"]
        for k in list(self.terms["full_talk_titles"].keys()):
            all_terms.extend(self.terms["full_talk_titles"][k])

        self.image_farmer.farm_images(list(set(all_terms)))

    def farm_gifs(self):
        all_terms = self.terms["giphy_searches"]
        for k in list(self.terms["full_talk_titles"].keys()):
            all_terms.extend(self.terms["full_talk_titles"][k])

        self.image_farmer.farm_gifs(list(set(all_terms)))

    def farm_data(self):
        searches = []

        for k in list(self.terms["full_talk_titles"].keys()):
            searches.extend(self.terms["full_talk_titles"][k])

        for s in list(set(searches)):
            self.data_farmer.farm_all(s)

        #for i in range(self.topic_dropdown.count()):
        #    self.data_farmer.farm_all(self.topic_dropdown.itemText(i))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TrolletteFarmerGUI()
    sys.exit(app.exec_())
