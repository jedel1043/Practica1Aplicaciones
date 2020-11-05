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

const baseFile = $(`
<li>
    <a href="#">
        <i class="element-icon far fa-file"></i>
    </a>
</li>
`)

const baseFolder = $(`
<li class="folder-element">
    <div class="title-container">
        <a href="#" class="main-title">
            <i class="fas fa-angle-down arrow-icon"></i>
            <i class="element-icon far fa-folder"></i>
        </a>
        <div class="btn-container">
            <!-- <a href="#" class="btn btn-download">
                <i class="far fa-arrow-alt-circle-down"></i>
            </a> -->
            <a href="#"  class="btn btn-delete">
                <i class="far fa-times-circle"></i>
            </a>
        </div>
    </div>
    <ul class="subfolder"></ul>
</li>
`)





$(document).ready(function () {
    // Adquirir nombre de usuario
    var urlStr = window.location.href;
    var url = new URL(urlStr);
    var username = url.searchParams.get("username");
    let userdata;

    optionsPython.args = [username];

    new PythonShell("client/get.py", optionsPython)
        .on('message', function (out) {
            userdata = JSON.parse(out);
            // Contenedor de carpetas
            var folders = $("#folders").empty();

            if (Object.keys(userdata).length != 0) {

                (function printTree(obj, elem) {
                    obj.dirs.forEach(newDirObj => {
                        newDirDOM = baseFolder.clone(true);
                        newDirDOM.children().first().children().first().append(newDirObj.name)

                        elem.append(newDirDOM);
                        printTree(newDirObj, newDirDOM.children().eq(1));
                    });

                    obj.files.forEach(filename => {
                        newFileDOM = baseFile.clone(true);
                        newFileDOM.children().first().append(filename)
                        elem.append(newFileDOM);
                    });
                })(userdata, folders);
            }
        });

    // Contenedor de botones para subir cosas
    var uploadContainer = $(".main-content #container-upload");

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
                    if (out == "finished") {
                        console.log("entró");
                        location.reload();
                    }
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
            upload = new PythonShell("client/upload.py", optionsPython)
                .on('message', out => {
                    console.log(out);
                    if (out == "finished") {
                        console.log("entró");
                        location.reload();
                    }
                });
        }
    });
});