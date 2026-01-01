class Controller {
    constructor(view) {
        this.view = view
        this.data = []
        this.pyready = false
        this.fileSelector = null

        this.fileSelector = document.createElement('input');
        this.fileSelector.type = 'file';
        this.fileSelector.accept = '.csv';
        this.fileSelector.style.display = 'none';
        this.fileSelector.addEventListener('change', async (event) => {
            if (this.fileSelector.files.length > 0) {
                let fileContent = await this.fileSelector.files[0].text();
                this.data = await window.pywebview.api.parse_csv_to_accounts(fileContent)
                this.updateView()
            }
        })

        
        document.getElementById("test-btn").onclick = () => {
            this.data.push({id: this.data.length + 1, nome: "Teste", status: "Online"})
            this.updateView()
        }
        
        document.getElementById("load-data-btn").onclick = () => {
            this.fileSelector.click();
        }

        document.getElementById("clear_data_btn").onclick = () => {
            this.data = []
            this.updateView()
        }

        window.controller = this
    }

    updateView() {
        console.log(`updateView com ${this.data.length} itens`)
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
        let columns = Object.keys(this.data[0])
        this.view.querySelector("thead tr").innerHTML = ""
        for (let key in this.data[0]) {
            this.view.querySelector("thead tr").innerHTML += `<th>${key}</th>`
        }
    }

    empty_view() {
        let tbody = this.view.querySelector("tbody")
        tbody.innerHTML = "<tr></tr>";
        this.view.querySelector("thead tr").innerHTML = "<th></th>";
    }

}

let controller = new Controller(document.querySelector("table"))
controller.empty_view()
controller.updateView()
