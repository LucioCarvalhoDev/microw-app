import webview
import os
from pathlib import Path
import microw

class Api:
    def log(self, text):
        print(text)
    
    def load_exemple_data(self):
        config = microw.Config()
        config.set(microw.Flags.DELIMITER, ",")
        config.set(microw.Flags.INPUT_FILE, "./example.csv")

        file_lines = microw.load_file_lines(config)
        buff = file_lines[0].split(config.get(microw.Flags.DELIMITER))
        columns = len(buff)
        print(f"Detected {columns} columns.\n{buff}")
        columns_names = ""
        for i in range(columns):
            columns_names += f"col{i} "
        columns_names = columns_names.strip()
        config.set(microw.Flags.COLUMNS, columns_names)

        accounts = microw.parse_data_to_accounts(config, file_lines)
        return accounts


def main(app):
    webview.start(debug=True)
    webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
    app.destroy()

if __name__ == '__main__':
    app = webview.create_window("Test", url="./gui/index.html", js_api=Api())
    main(app)
    print("oi")