const { dialog } = require('electron').remote

//Python Shell
const { PythonShell } = require("python-shell");
const path = require("path");

var optionsPython = {
    // mode: 'json',
    pythonOptions: ['-u'],
    scriptPath: path.join(__dirname, 'engine/'),
    args: []
};

$(document).ready(function () {
    //Adquirir nombre de Usuario
    let urlStr = window.location.href;
    let url = new URL(urlStr);
    let username = url.searchParams.get("username");

    //LLenar el archivo con los archivos del usuario

    //Boton para subir Carpeta
    $(".main-content #container-upload")
        .on("click", "#input-folder", function (e) {
            dialog.showOpenDialog({
                properties: ['openDirectory']
            }).then(function dialogResult(data) {
                let paths = data.filePaths;
                //Llamar script de python
                if (paths) {
                    optionsPython.args = [username, ...paths];
                    new PythonShell("client/upload.py", optionsPython)
                        .on('message', function (out) {
                            console.log(out);
                        });
                }
            }).catch(err => console.error(err));
        })
        .on("click", "#input-file", function (e) {
            dialog.showOpenDialog({
                properties: ['openFile', 'multiSelections']
            }).then(function dialogResult(data) {
                let paths = data.filePaths;
                //Llamar script de python
                if (paths) {
                    optionsPython.args = [username, ...paths];
                    new PythonShell("client/upload.py", optionsPython)
                        .on('message', function (out) {
                            console.log(out);
                        });
                }
            }).catch(err => console.error(err));
        });
})