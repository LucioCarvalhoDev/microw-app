import webview
import os
from pathlib import Path
import microw

class Api:
    def log(self, text):
        print(text)
    
    def parse_csv_to_accounts(self, text: str):
        config = microw.Config()
        config.set(microw.Flags.DELIMITER, ",")

        file_lines = text.splitlines()
        
        buff = file_lines[0].split(config.get(microw.Flags.DELIMITER))
        columns = len(buff)
        columns_names = ""
        for i in range(columns):
            columns_names += f"col{i} "
        columns_names = columns_names.strip()
        config.set(microw.Flags.COLUMNS, columns_names)
        return microw.parse_data_to_accounts(config, file_lines)
        


def main(app):
    webview.start(debug=True)
    webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
    app.destroy()

if __name__ == '__main__':
    app = webview.create_window("Test", url="./gui/index.html", js_api=Api())
    main(app)
    print("oi")