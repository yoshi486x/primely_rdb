import collections
import configparser
import json
import numpy as np
import os
import pandas as pd
import pathlib

# TODO uncomment out the utils and rollback line 29 and 30
try:
    from primely import utils
except:
    pass

# import global parameters from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
JSON_DIR_PATH = config['STORAGE']['JSON']
GRAPHS_DIR_PATH = config['STORAGE']['GRAPH']
INCOME_GRAPH_NAME = config['FILENAME']['GRAPH']

PAID_DATE = 'paid_date'


class CollecterModel(object):

    def __init__(self, filenames=None, base_dir=None, dataframe=None, figure=None):
        if not base_dir:
            base_dir = utils.get_base_dir_path(__file__)
            # base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.base_dir = base_dir
        if not filenames:
            filenames = self.get_json_filenames()
        self.filenames = filenames
        self.dataframe = dataframe
        self.figure = figure

    def get_json_filenames(self, filenames=[]):
        """Set json file path.
        Use given json filenames if set on calls, otherwise use default.
        
        :type filenames: list
        :rtype filenames: list
        """

        json_full_dir_path = pathlib.Path(self.base_dir, JSON_DIR_PATH)
        if len(filenames) == 0:
            for item in os.listdir(json_full_dir_path):
                filenames.append(item)
        return filenames

    # TODO: 20200410 Implement aws source to this func.
    # Enable category input and process accordingly
    def create_base_table(self):
        """Create base tablefor """
        df = self.dataframe
        dataframes = []

        # Loop
        """TODO dict data loaded from json file will have some broken structures.
        In detail, values with blank space are separeted into multiple columns"""
        for filename in self.filenames:
            dates, keys, values, indexes = [], [], [], []

            file_path = pathlib.Path(JSON_DIR_PATH, filename)
            with open(file_path, 'r') as json_file:
                # data = json.load(json_file)
                dict_data = json.load(json_file)
            
            """Exclude table name from json file"""
            # for key in data.keys():
            #     name = key
            # dict_data = data[name].pop()

            """Single key extraction"""
            dates, keys, values = [], [], []
            date = dict_data[PAID_DATE]
            for key, value in dict_data['incomes'].items():
                values.append(value)
                keys.append(key)
                dates.append(date)
            df = pd.DataFrame({'date': dates, 'type': keys, 'income': values})
            dataframes.append(df)

        # Combine tables of each json file
        df = pd.concat(dataframes)
        table = pd.pivot_table(df, index='date', columns='type', values='income', fill_value=0)
        
        self.dataframe = table

    def rename_columns(self):
        renames = ['Alfa', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot',
             'Golf', 'Hotel', 'India', 'Juliett', 'Kilo', 'LIma', 'Mike', 
             'November', 'Oscar', 'Papa', 'Quebec', 'Romeo', 'Sierra']
        df = self.dataframe

        col_num = len(df.columns)
        renames = renames[:col_num]
        col_dict = dict(zip(df.columns, renames))
        self.dataframe = df.rename(columns=col_dict)

    def camouflage_values(self, camouflage=False):

        if camouflage is True:
            try:
                from models import camouflage
            except:
                try:
                    import camouflage
                except:
                    return
            self.dataframe = camouflage.camouflage(self.dataframe)

    def sort_table(self):

        try:
            from primely.models import sorting
        except:
            import sorting

        df = sorting.sort_table(self.dataframe)
        self.dataframe = df


RESPONSE_TEMPLATE = {'incomes': {}, 'deductions': {}, 'attendances': {}}
class OrganizerModel(object):
    def __init__(self, dataframe=None):
        self.dataframe = dataframe
        self.response = RESPONSE_TEMPLATE

    def update_response(self, category=None):
        # print('response:', self.response)
        rows = {'rows': list(self.dataframe.index)}
        columns = {'columns': list(self.dataframe.columns)}
        # v_array = self.dataframe.to_numpy()
        v_array = self.dataframe.values
        values = {'values': v_array.tolist()}

        # print('response:', response)
        self.response[category].update(rows)
        self.response[category].update(columns)
        self.response[category].update(values)
        # print(self.response)

    def export_response_in_json(self):
        try:
            from primely.models import recording
        except:
            import recording
        dest_info = {
            'filename': 'paycheck_timechart.json',
            'dir_path': config['STORAGE']['REPORT'],
            'file_path': None
        }
        recording_model = recording.RecordingModel(**dest_info)
        recording_model.record_data_in_json(self.response)


# TODO create graph output files if it doesn't exist
class PlotterModel(object):

    def __init__(self, dataframe=None):
        self.dataframe = dataframe

    def save_graph_to_image(self):
        file_path = pathlib.Path(GRAPHS_DIR_PATH, INCOME_GRAPH_NAME)
        ax = self.dataframe.plot(
            figsize=(15, 10), kind='bar', stacked=True, grid=True, sharey=False,
            title='Income breakdown **Sample data was used for this graph**',
            )
        ax.set_ylabel('amount of income [yen]')
        fig = ax.get_figure()
        fig.savefig(file_path)

def main():
    visual = CollecterModel(None)
    # print(visual.filenames)
    visual.create_base_table()
    visual.rename_columns()
    visual.sort_table()
    # visual.camouflage_values(True)
    
    myDataframe = visual.dataframe

    organizer = OrganizerModel(myDataframe)
    organizer.update_response('incomes')


if __name__ == "__main__":
    main()