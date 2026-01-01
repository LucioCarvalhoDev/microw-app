# microw-app

A GUI application to convert tabular data (CSV) into MicroSIP account configuration files (.ini) that wraps the CLI utility _microw_.

## Features

- Convert CSV/TXT files to MicroSIP .ini configuration files
- Customizable column mapping and labels
- Support for sorting, password setting, server configuration
- Add ghost accounts
- GUI interface for interactive use
- CLI for batch processing

## Installation

1. Clone or download the repository.
2. Install the required dependencies by running:

   ```bash
   ./init.sh
   ```

## Usage

### GUI from script

Run the GUI application:

```bash
python main.py
```

This will open a web-based interface where you can upload CSV files and generate MicroSIP configurations interactively.

### GUI from executable

To build a standalone executable using PyInstaller execute `compile.sh`.

### CLI

Use the original utility at [microw](https://github.com/LucioCarvalhoDev/microw).

## Credits

Developed by Lúcio Carvalho Almeida, Open Source.  
Contact: luciocarvalhodev@gmail.com

## License

This project is open source. Please refer to the code for licensing details.