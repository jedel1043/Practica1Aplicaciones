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
    // Adquirir nombre de usuario
    let urlStr = window.location.href;
    let url = new URL(urlStr);
    let username = url.searchParams.get("username");

    // Contenedor de botones para subir cosas
    let uploadContainer = $(".main-content #container-upload");

    // Evento para subir carpetas
    uploadContainer.on("click", "#input-folder", async function pickSendDirs(e) {
        let dirs = await dialog.showOpenDialog({
            properties: ['openDirectory', 'multiSelections']
        }).catch(err => console.error(err));

        let paths = dirs.filePaths;

        //Llama script de python si paths tiene rutas
        if (paths) {
            optionsPython.args = [username, ...paths];
            new PythonShell("client/upload.py", optionsPython)
                .on('message', function (out) {
                    console.log(out);
                });
        }
    });

    // Evento para subir archivos
    uploadContainer.on("click", "#input-file", async function pickSendFiles(e) {
        let files = await dialog.showOpenDialog({
            properties: ['openFile', 'multiSelections']
        }).catch(err => console.error(err));

        let paths = files.filePaths;

        //Llama script de python si paths tiene rutas
        if (paths) {
            optionsPython.args = [username, ...paths];
            new PythonShell("client/upload.py", optionsPython)
                .on('message', function (out) {
                    console.log(out);
                });
        }
    });
});
