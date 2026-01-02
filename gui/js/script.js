
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
                this.data = accounts
                this.update()
            }
        })
        
        document.getElementById("test-btn").onclick = () => {
            this.data.push({id: this.data.length + 1, nome: "Teste", status: "Online"})
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

        window.controller = this
    }

    async update() {
        this.updateTable()
        await this.updateContent()
        this.updatePreview()
        this.updateForm()
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

    updateTable() {
        if (this.data.length == 0) {
            this.empty_view()
            return
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

        this.view.querySelector("thead tr").innerHTML = ""
        for (let key in this.data[0]) {
            this.view.querySelector("thead tr").innerHTML += `<th>${key}</th>`
        }

        this.getColumns()
    }

    empty_view() {
        let tbody = this.view.querySelector("tbody")
        tbody.innerHTML = "<tr></tr>";
        this.view.querySelector("thead tr").innerHTML = "<th></th>";
    }

    async updateContent() {
        let content = await window.pywebview.api.build_content(this.data);
        this.content = content
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