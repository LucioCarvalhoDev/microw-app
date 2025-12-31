import sys
from enum import Enum
from pathlib import Path
import codecs
import re
from textwrap import wrap

MAN_DESCRIPTION = """
NOME
microw - convert data to MicroSIP accounts

USO
python3 microw.py [OPÇÔES]

DESCRIÇÂO
Utilitário para conversão de dados tabulares (CSV, TXT) em arquivos de 
configuração (.ini) para o softphone MicroSIP e variantes.
"""

MAN_FOOTER = """
EXEMPLOS
1. Formato padrão com separador de ponto e vírgula:
    python3 microw.py --delimiter ";"

2. Ignorando a 1ª coluna e formatando o nome de exibição:
    python3 microw.py --columns "_ ramal nome setor" --label-pattern "nome [setor]"

3. Usando um arquivo específico e adicionando conta fantasma:
    python3 microw.py --input-file lista_vendas.csv --add-ghost

CREDITOS
Desenvolvido por Lúcio Carvalho Almeida, Open Source.
Contato em luciocarvalhodev@gmail.com.
"""

ACCOUNT_TEMPLATE = r'''
[Account_]
label=$label
server=$server
proxy=$server
domain=$server
username=$ramal
password=$password
authID=$ramal
'''

GHOST_TEMPLATE = r'''
[Account_]
label=Desconectado
server=0.0.0.0
proxy=0.0.0.0
domain=0.0.0.0
username=0000
password=1234
authID=0000
'''

VALID_AUTO_ANSWER_VALUES = ["all", "no", "button"]
VALID_DENY_INCOMING_VALUES = ["all", "no", "server", "user", "button"]

class Flags(Enum):
    COLUMNS = "columns"
    DELIMITER = "delimiter"
    LABEL_PATTERN = "label-pattern"
    SET_PASSWORD = "set-password"
    SET_SERVER = "set-server"
    ADD_GHOST = "add-ghost"
    INPUT_FILE = "input-file"
    OUTPUT_FILE = "output-file"
    SET_TEMPLATE = "set-template"
    READ_ENCODING = "read-encoding"
    WRITE_ENCODING = "write-encoding"
    HELP = "help"
    SORT = "sort"
    SORT_BY = "sort-by"
    DENY_INCOMING = "deny-incoming"
    AUTO_ANSWER = "auto-answer"

    @classmethod
    def from_str(cls, name: str):
        normalized_flag_name = name.replace("-", "_").upper()
        if not normalized_flag_name in cls.__members__:
            error_string = f"O argumento '--{name}' não corresponde a uma flag válida."
            raise ValueError(error_string)    
        return cls[normalized_flag_name]
    
    def to_str(self):
        return self._value_

# Quantidade de argumentos esperados
class FlagSchema(Enum):
    NoArgument = 0
    Argument = 1

# Os métodos dessa classe recebem instancias de Flags
class Config:
    def __init__(self):
        self.flags = {}
        self.define_flag(flag=Flags.COLUMNS, schema=FlagSchema.Argument, default="ramal label", man="""Define a ordem das colunas no arquivo de entrada. Use nomes de variáveis (ex: ramal, password) ou '_' para ignorar uma coluna específica.""")
        self.define_flag(flag=Flags.SET_PASSWORD, schema=FlagSchema.Argument, default=None, man="Quando presente determina uma única senha para ser usada por todas as contas.")
        self.define_flag(flag=Flags.SET_SERVER, schema=FlagSchema.Argument, default=None, man="Quando presente determina o servidor de todas as contas.")
        self.define_flag(flag=Flags.DELIMITER, schema=FlagSchema.Argument, default=",", man="""Define qual string será considerada como seprador das colunas de cada linha do input.""")
        self.define_flag(flag=Flags.LABEL_PATTERN, schema=FlagSchema.Argument, default="label", man="""Template para customizar o nome de exibição. Substitui nomes de variáveis pelos seus valores.""")
        self.define_flag(flag=Flags.HELP, schema=FlagSchema.NoArgument, default=False, man="""Exibe o manual.""")
        self.define_flag(flag=Flags.ADD_GHOST, schema=FlagSchema.NoArgument, default=False, man="""Se presente, adiciona uma conta de 'Desconectado' como o primeiro perfil da lista.""")
        self.define_flag(flag=Flags.SET_TEMPLATE, schema=FlagSchema.Argument, default=None, man="""Fornece o caminho para um arquivo que servira como template.""")
        self.define_flag(flag=Flags.INPUT_FILE, schema=FlagSchema.Argument, default="./input.txt", man="""Caminho do arquivo de origem dos dados.""")
        self.define_flag(flag=Flags.OUTPUT_FILE, schema=FlagSchema.Argument, default="./output.ini", man="""Caminho onde o arquivo .ini será gerado.""")
        self.define_flag(flag=Flags.READ_ENCODING, schema=FlagSchema.Argument, default="utf-8", man=f"Codificação do arquivo lido por '--{Flags.INPUT_FILE}'")
        self.define_flag(flag=Flags.WRITE_ENCODING, schema=FlagSchema.Argument, default="utf-8", man="Codificação do arquivos gerados.")
        self.define_flag(flag=Flags.SORT, schema=FlagSchema.NoArgument, default=False, man="""Ordena as contas no arquivo final. Caso não presente preservará a ordem das linhas do input.""")
        self.define_flag(flag=Flags.SORT_BY, schema=FlagSchema.Argument, default="ramal", man="""Define qual coluna será usada para ordenação alfabética.""")
        self.define_flag(flag=Flags.DENY_INCOMING, schema=FlagSchema.Argument, default="button", man="""Define se o aplicativo irá rejeitar ligações automaticamente.\nValores possíveis: all, no, server, user, button""")
        self.define_flag(flag=Flags.AUTO_ANSWER, schema=FlagSchema.Argument, default="button", man="""Habilita o atendimento automático de chamadas.\nValores possíveis: all, no, button""")

    def generate_flags_man(self):
        res = [MAN_DESCRIPTION]
        for flag in Flags:
            res.append(self.flag_man(flag))

        res.append(MAN_FOOTER)

        return "\n".join(res)

    def flag_man(self, flag: Flags):
        ident = "    " * 5

        lines = wrap(self.flags[flag]["man"], 60)
        lines[0] = (f"--{flag.to_str()}{ident}"[0:len(ident)] + lines[0])

        for i in range(len(lines)-1):
            lines[i+1] = ident + lines[i+1]
        
        return "\n".join(lines)

    def load_args(self, args: list[str]):
        while len(args):
            argument = args.pop(0)
            if argument[:2] == "--":
                argument = argument[2:]
            
            flag = Flags.from_str(argument)
            
            if self.schema(flag) == FlagSchema.Argument:
                if len(args) == 0:
                    msg_error = f"Flag '--{argument}' exige um argumento."
                    raise ValueError(msg_error)
                self.set(flag, codecs.decode(args.pop(0), "unicode_escape"))
            else:
                self.set(flag, not self.getDefault(flag))
    
    def define_flag(self, flag: Flags, schema: FlagSchema, default, man: str):
        self.flags[flag] = {
            "schema": schema,
            "default": default,
            "man": man
        }
    
    def _validate_setting(self, setting: Flags):
        if not isinstance(setting, Flags):
            raise ValueError(f"'{setting}' is not a valid flag.")

        return setting.value
    
    def get(self, setting):
        self._validate_setting(setting)
        return self.flags[setting].get("value", self.flags[setting]["default"])
    
    def getDefault(self, setting):
        self._validate_setting(setting)
        return self.flags[setting]["default"]

    def set(self, setting, value):
        self._validate_setting(setting)

        if setting == Flags.DENY_INCOMING:
            if not value in VALID_DENY_INCOMING_VALUES:
                error_msg = f"Valor '{value}' inválido para '--{setting.to_str()}'. Valores válidos: {', '.join(VALID_DENY_INCOMING_VALUES)}."
                raise ValueError(error_msg)
        if setting == Flags.AUTO_ANSWER:
            if not value in VALID_AUTO_ANSWER_VALUES:
                error_msg = f"Valor '{value}' inválido para '--{setting.to_str()}'. Valores válidos: {', '.join(VALID_DENY_INCOMING_VALUES)}."
                raise ValueError(error_msg)
        self.flags[setting]["value"] = value
    
    def schema(self, setting):
        self._validate_setting(setting)
        return self.flags[setting]["schema"]

def load_file_lines(config: Config) -> list[str]:
    input_file = Path(config.get(Flags.INPUT_FILE))
    if not input_file.exists():
        error_msg = f"Arquivo de input especificado '{input_file.name}' não encontrado."
        raise ValueError(error_msg)
    input_lines = [line.strip() for line in input_file.open("r", encoding=config.get(Flags.READ_ENCODING)).readlines()]
    return input_lines

def parse_data_to_accounts(config: Config, input_lines: list[str]) -> list[dict[str, str]]:
    accounts_settings = []
    columns = config.get(Flags.COLUMNS).split(" ")
    label_pattern = config.get(Flags.LABEL_PATTERN)

    for line in input_lines:
        if not line: continue
        
        data = [field.strip() for field in line.split(config.get(Flags.DELIMITER))]
        account_data = {}

        # Mapeia os dados ignorando o caractere '_'
        for i in range(min(len(data), len(columns))):
            column_name = columns[i]
            if column_name != "_":
                account_data[column_name] = data[i]
        
        # Customização do $label
        formated_pattern = label_pattern
        # Encontra nomes de variaveis para substituição no label_pattern
        for pattern_part in re.finditer(r"[a-zA-Z]+", label_pattern):
            pattern = pattern_part.group()
            if pattern in columns:
                formated_pattern = formated_pattern.replace(pattern, data[columns.index(pattern)]) 

        account_data["label"] = formated_pattern
        accounts_settings.append(account_data)
    
    if config.get(Flags.SORT) : accounts_settings.sort(key=lambda account : account[config.get(Flags.SORT_BY)])
    return accounts_settings

def build_content(config: Config, accounts_settings: list[dict[str, str]]) -> str:
    result = f"[Settings]\ndenyIncoming={config.get(Flags.DENY_INCOMING)}\nautoAnswer={config.get(Flags.AUTO_ANSWER)}\n\n"

    if config.get(Flags.ADD_GHOST):
        result += GHOST_TEMPLATE
    
    current_account_template = ACCOUNT_TEMPLATE

    if not config.get(Flags.SET_TEMPLATE) is None:
        current_account_template = Path(config.get(Flags.SET_TEMPLATE)).read_text(encoding=config.get(Flags.READ_ENCODING))
    if not config.get(Flags.SET_PASSWORD) is None:
        current_account_template = current_account_template.replace("$password", config.get(Flags.SET_PASSWORD))
    if not config.get(Flags.SET_SERVER) is None:
        current_account_template = current_account_template.replace("$server", config.get(Flags.SET_SERVER))

    for account in accounts_settings:
        new_entry = current_account_template
        for column_name, value in account.items():
            new_entry = new_entry.replace("$" + column_name, str(value))
        
        result += new_entry.strip() + "\n"

    result = result.strip()

    id = 1
    while "Account_" in result:
        result = result.replace("Account_", f"Account{id}", 1)
        id += 1

    return result


if __name__ == "__main__":
    config = Config()
    config.load_args(sys.argv[1:])
    
    if config.get(Flags.HELP):
        print(config.generate_flags_man())
        sys.exit(0)

    input_lines = load_file_lines(config)
    accounts = parse_data_to_accounts(config, input_lines)
    output_file = Path(config.get(Flags.OUTPUT_FILE))
    content = build_content(config, accounts)
    output_file.write_text(content, encoding=config.get(Flags.WRITE_ENCODING))
    print(f"Sucesso: {len(accounts)} contas criadas em '{output_file}'.")