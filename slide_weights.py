__author__ = 'wartortell'

import random
import logging


class SlideWeights:
    def __init__(self):
        self.logger = logging.getLogger("Slide Types")
        self.logger.setLevel(logging.INFO)

        self.weights = {"Single GIF": 1,
                        "Full Slide GIF": 1,
                        "Single Image": 1,
                        "Full Slide Image": 1,
                        "Information": 4,
                        "Quotation": 1
                        }

        # The list used by Obfusion when determining which code block will be used
        self.weighted_list = []
        self.weighted_lookup = []

        # The list of values used for random code type choice
        self.code_types = []

        # Initiate the lists
        self.create_weighted_list()
        self.create_code_types()

    def set_weight(self, name, weight):
        """
        Description:
            Set a code type's weight
        :param name: string
        :param weight: int
        :return: None
        """

        if not (name in self.weights.keys()):
            self.logger.error("The code type %s is not known/implemented!" % name)
            return

        if not (type(weight) == int):
            self.logger.error("Weight values must be provided as integers: %s" % str(weight))
            return

        self.weights[name] = weight

        self.create_weighted_list()
        self.create_code_types()

    def set_all_weights(self, new_weights):
        """
        Description:
            Set all the weights to new values, useful for using predefined weight lists

        :param new_weights: dict: string->int
        :return: None
        """

        self.weights = new_weights

        self.create_weighted_list()
        self.create_code_types()

    def create_weighted_list(self):
        """
        Description:
            Create the weighted list based on the current weights

        :return: None
        """

        self.weighted_list = self.weights.keys()
        self.weighted_lookup = []

        for i in range(len(self.weighted_list)):
            for j in range(self.weights[self.weighted_list[i]]):
                self.weighted_lookup.append(i)

    def create_code_types(self):
        """
        Description:
            Fill the array with all entries that have any weight

        :return: None
        """

        self.code_types = []
        for key in self.weights.keys():
            if self.weights[key]:
                self.code_types.append(key)

    def show_weights(self):
        """
        Description:
            Prints the percentage weight of each code type

        :return: None
        """

        print("\nCurrent Weights:\n---------------------")
        for key in sorted(self.weights.keys()):
            print("%s: %2.2f%%" % (key, 100.0*float(self.weights[key])/float(len(self.weighted_lookup))))

    def choose_weighted(self):
        """
        Description:
            Select a weighted choice from the list of code types

        :return: string
        """
        return self.weighted_list[random.choice(self.weighted_lookup)]

    def choose_random(self):
        """
        Description:
            Choose a random code type (do not use weights)
            NOTE: code types with weight 0 will still be ignored by this function

        :return: string
        """

        return random.choice(self.code_types)

    def get_weights_string(self):
        weight_str = "Slide Weights:\n"

        total_weights = 0
        for key in self.weights.keys():
            total_weights += self.weights[key]

        for key in sorted(self.weights.keys()):
            weight_str += "  %s: %.2f%%\n" % (key, 100.0 * float(self.weights[key])/float(total_weights))

        return weight_str


