import webview
import microw

class Api:
    def log(self, text):
        print(text)
    
    def parse_csv_to_accounts(self, text: str):
        config = microw.Config()
        config.set(microw.Flags.DELIMITER, ",")

        file_lines = text.splitlines()
        
        config.set(microw.Flags.COLUMNS, self.generate_columns(text))
        return microw.parse_data_to_accounts(config, file_lines)

    def build_content(self, accounts: list[dict]):
        config = microw.Config()
        config.set(microw.Flags.DELIMITER, ",")

        return microw.build_content(config, accounts)
    
    def generate_columns(self, text: str):
        config = microw.Config()
        config.set(microw.Flags.DELIMITER, ",")

        file_lines = text.splitlines()
        
        buff = file_lines[0].split(config.get(microw.Flags.DELIMITER))
        columns = len(buff)
        columns_names = ""
        for i in range(columns):
            columns_names += f"col{i} "
        return columns_names.strip()
        


def main(app):
    
    webview.start(debug=True, gui='edge') # type: ignore
    webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
    app.destroy()

if __name__ == '__main__':
    app = webview.create_window("Test", url="./gui/index.html", js_api=Api())
    main(app)
    print("oi")