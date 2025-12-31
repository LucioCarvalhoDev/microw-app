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

        accounts = microw.parse_data_to_accounts(config)
        return accounts


def main(app):
    webview.start()
    webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
    app.destroy()

if __name__ == '__main__':
    app = webview.create_window("Test", url="./gui/index.html", js_api=Api())
    main(app)
    print("oi")