
import hljs from '../lib/highlight/es/highlight.js';
import hljsGrammar from '../lib/highlight/es/languages/ini.js'

hljs.registerLanguage('ini', hljsGrammar);

class Controller {
    constructor(view) {
        this.view = view
        this.data = []
        this.content = ""
        this.pyready = false
        this.fileSelector = null
        this.settings = {}
        this.maskNames = ["ramal", "password", "server", "label"]

        this.fileSelector = document.createElement('input');
        this.fileSelector.type = 'file';
        this.fileSelector.accept = '.csv';
        this.fileSelector.style.display = 'none';
        this.fileSelector.addEventListener('change', async (event) => {
            if (this.fileSelector.files.length > 0) {
                let fileContent = await this.fileSelector.files[0].text();
                var accounts = await window.pywebview.api.parse_csv_to_accounts(fileContent)
                for (let account of accounts) {
                    delete account.label
                }

                this.setData(accounts)
                this.update()
            }
        })

        document.getElementById("test-btn").onclick = () => {
            this.data.push({ id: this.data.length + 1, nome: "Teste", status: "Online" })
            this.update()
        }

        document.getElementById("load-data-btn").onclick = () => {
            this.fileSelector.click();
        }

        document.getElementById("clear_data_btn").onclick = () => {
            this.data = []
            this.update()
        }

        document.getElementById("download").onclick = () => {
            let link = document.createElement('a');
            let blob = new Blob([this.content], { type: 'text/plain' });
            link.href = window.URL.createObjectURL(blob);
            link.download = 'accounts.txt';
            link.click();
        }

        document.getElementById("form-settings").onchange = () => {
            let settings = Object.fromEntries(new FormData(document.getElementById("form-settings")));
            for (let checkboxElement of document.querySelectorAll("#form-settings input[type='checkbox'")) {
                settings[checkboxElement.name] = checkboxElement == "on"
            }
            this.settings = settings
            this.updateContent()
        }

        document.querySelector("thead").onchange = () => {
            console.log("mudança no thead")
            this.updateContent()
        }

        document.getElementById("reload").onclick = () => {
            this.updateContent()
        }

        window.controller = this
    }

    async setData(data) {
        this.data = data
        await this.updateContent()
        await this.updateTable()
    }

    async update() {
        this.updateTable()
        await this.updateContent()
        this.updatePreview()
    }

    getMaskedData() {
        let masks = {};
        const selectElementList = this.view.querySelectorAll("thead select");
        for (const select of selectElementList) {
            const columName = select.value

            if (!this.maskNames.includes(columName)) continue;

            masks[select.dataset.id] = columName
        }

        const maskedData = this.data.map(accountData => {
            const maskedAccount = {}
            for (let [key, value] of Object.entries(accountData)) {
                if (accountData[key].length == "") continue;
                const mask = masks[key]
                if (mask != undefined) key = mask
                maskedAccount[key] = value
            }
            return maskedAccount
        })

        return maskedData
    }

    updateForm() {
        document.getElementById("sort-by").innerHTML = `<option value="none"></option>` + this.getColumns().map(colName => `<option value="${colName}">${colName}</option>`).join("\n")
    }

    getColumns() {
        let columns = []

        if (this.data.length == 0) return columns;

        for (let key of Object.keys(this.data[0])) {
            columns.push(key)
        }

        return columns
    }

    getNamedColumns() {

    }

    updateTable() {
        if (this.data.length == 0) {
            this.empty_view()
            return
        }

        const tableHeader = this.view.querySelector("thead tr");
        tableHeader.innerHTML = ""
        for (let key in this.data[0]) {
            // console.log(key)
            let col = key
            tableHeader.innerHTML += `<th><select data-id="${col}"><option value="${col}">${col}</option>${this.maskNames.map(name => `<option value="${name}">${name}</option>`)}</select></th>`
        }

        let tbody = this.view.querySelector("tbody")
        tbody.innerHTML = ""
        for (let account of this.data) {
            let row = ""
            for (let key in account) {
                row += `<td>${account[key]}</td>`
            }
            tbody.innerHTML += row
        }
    }

    empty_view() {
        let tbody = this.view.querySelector("tbody")
        tbody.innerHTML = "<tr></tr>";
        this.view.querySelector("thead tr").innerHTML = "<th></th>";
    }

    async updateContent() {
        const data = this.getMaskedData()

        let content = await window.pywebview.api.build_content(data, this.settings);
        this.content = content
        this.updatePreview()
    }

    updatePreview() {
        let code_area = document.getElementById("preview_content")
        code_area.textContent = this.content;
        code_area.className = 'language-ini';
        delete code_area.dataset.highlighted;
        hljs.highlightElement(code_area);
    }

}

let controller = new Controller(document.querySelector("table"))
controller.empty_view()
controller.updateTable()
controller.updatePreview()