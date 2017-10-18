import os
import json

from helpers import default_logger, get_data_folder


class DataFarmer:
    def __init__(self, logger=None):
        self.logger = logger
        if not self.logger:
            self.logger = default_logger

        self.initialize_apis()
        self.initialize_paths()

    def initialize_apis(self):
        """
        Place holder function for set up of APIs used by this farmer
        :return: 
        """
        pass

    def initialize_paths(self):
        """
        Place holder function for setting up paths for this farmer
        :return: 
        """
        pass

    def farm_data(self, **kwargs):
        """
        Description: Place holder for an information retrieval function about what's been farmed
        
        :return: 
        """

        pass