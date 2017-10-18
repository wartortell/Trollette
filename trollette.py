import sys
import argparse
from PyQt5.QtWidgets import QApplication

from farmers import *
from guis import TrolletteFarmerGUI, TrolletteGeneratorGUI
from helpers import default_logger, get_data_folder


class Trollette:
    def __init__(self):
        self.gif_farmer = GifFarmer
        self.image_farmer = ImageFarmer()
        self.quote_farmer = QuoteFarmer()
        self.text_farmer = TextFarmer()

    def farm_topic(self, topic, title, threshold):
        # Create our topic farming list
        topics = topic.split(",")
        topics.append(" ".join(topics))

        self.text_farmer.farm_data(topic=topic, threshold=threshold)


def get_arg_parser():
    parser = argparse.ArgumentParser()

    # Farming Argumemts
    parser.add_argument("-t", "--topic",
                        action="store",
                        help="Farm a topic for image and text data pertaining to it. " +
                             "Can use a commas to separate for multiple topics. " +
                             "When using this method, specify --threshold and --title as well. ")

    parser.add_argument("-i", "--title",
                        action="store",
                        help="The title for the presentation on the farmed topic will be.")

    parser.add_argument("-r", "--threshold",
                        action="store",
                        default="5",
                        help="The threshold for how much data to store for each topic.")

    parser.add_argument("-ct", "--check_topic",
                        action="store",
                        help="Check how much data you have about a specific topic.")

    parser.add_argument("-lt", "--list_topics",
                        action="store_true",
                        help="Get the list of possible talks.")

    # Generator Arguments
    parser.add_argument("-gt", "--generate_topic",
                        action="store",
                        help="Generate a slide deck for the provided topic")

    parser.add_argument("-ga", "--generate_all",
                        action="store_topic",
                        help="Generate a slide deck for all topics with an appropriate amount of data")

    # GUI Arguments
    parser.add_argument("-gf", "--gui_farmer",
                        action="store_true",
                        help="Start the data farming GUI")

    parser.add_argument("-gg", "--gui_generator",
                        action="store_true",
                        help="Start the deck generator GUI")

    return parser


def run_trollette():
    parser = get_arg_parser()
    args = parser.parse_args()

    troll = Trollette()

    if args.topic:
        if not args.title or not args.threshold:
            default_logger("You must use the --title and --threshold options with the --farm_topic option.")
            parser.print_help()
            exit()

        troll.farm_topic(args.topic, args.title, args.threshold)

    elif args.check_topic:
        pass

    elif args.list_topic:
        pass

    elif args.generate_topic:
        pass

    elif args.generate_all:
        pass

    elif args.gui_farmer:
        app = QApplication(sys.argv)
        _ = TrolletteFarmerGUI()
        sys.exit(app.exec_())

    elif args.gui_generator:
        app = QApplication(sys.argv)
        _ = TrolletteGeneratorGUI()
        sys.exit(app.exec_())

    else:
        parser.print_help()

    exit(0)


if __name__ == "__main__":
    run_trollette()
