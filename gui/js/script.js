class Controller {
    constructor(view) {
        this.view = view
        this.data = []
    }

    update_view() {
        let tbody = this.view.querySelector("tbody")
        tbody.innerHTML = ""
        for (let account of this.data) {
            let row = ""
            for (let key in account) {
                row += `<td>${account[key]}</td>`
            }
            tbody.innerHTML += row
        }
        let columns = Object.keys(this.data[0]).length
        this.view.querySelector("thead tr").innerHTML = ""
        for (let key in this.data[0]) {
            this.view.querySelector("thead tr").innerHTML += `<th>${key}</th>`
        }
    }

}

let controller = new Controller(document.querySelector("table"))
window.onload = () => {
    let interval = setInterval(() => {
        if (window.pywebview && window.pywebview.api)
            clearInterval(interval)
            window.pywebview.api.load_exemple_data().then((data) => {
                controller.data = data;
                controller.update_view();
            })
    }, 500);
}