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
    var urlStr = window.location.href;
    var url = new URL(urlStr);
    var username = url.searchParams.get("username");
    // Contenedor de botones para subir cosas
    var uploadContainer = $(".main-content #container-upload");

    optionsPython.args = [username];

    new PythonShell("client/get.py", optionsPython)
        .on('message', function (out) {
            let userdata = JSON.parse(out);
            // Contenedor de carpetas
            var folders = $("#folders").empty();

            if (Object.keys(userdata).length != 0) {
                (function printTree(obj, elem, oldPath) {
                    obj.dirs.forEach(newDirObj => {
                        let newPath = path.join(oldPath, newDirObj.name);

                        let newDirDOM = $(`
                            <li class="folder-element" path="${newPath}">
                                <div class="title-container">
                                    <a href="#" class="main-title">
                                        <i class="fas fa-angle-down arrow-icon"></i>
                                        <i class="element-icon far fa-folder"></i>
                                        ${newDirObj.name}
                                    </a>
                                    <div class="btn-container">
                                        <a href="#" class="btn btn-download">
                                            <i class="far fa-arrow-alt-circle-down"></i>
                                        </a>
                                        <a href="#"  class="btn btn-delete">
                                            <i class="far fa-times-circle"></i>
                                        </a>
                                    </div>
                                </div>
                                <ul class="subfolder"></ul>
                            </li>
                        `);

                        elem.append(newDirDOM);
                        printTree(newDirObj, newDirDOM.children().eq(1), newPath);
                    });

                    obj.files.forEach(filename => {
                        let newPath = path.join(oldPath, filename);
                        newFileDOM = $(`
                            <li path="${newPath}">
                                <div class="title-container">
                                    <a href="#" class="main-title">
                                        <i class="element-icon far fa-file"></i>
                                        ${filename}
                                    </a>
                                    <div class="btn-container">
                                        <a href="#" class="btn btn-download">
                                            <i class="far fa-arrow-alt-circle-down"></i>
                                        </a>
                                        <a href="#"  class="btn btn-delete">
                                            <i class="far fa-times-circle"></i>
                                        </a>
                                    </div>
                                </div>
                            </li>
                        `);
                        elem.append(newFileDOM);
                    });
                })(userdata, folders, "");

                $(".btn-download").on("click", function dlHandler(e) {
                    e.preventDefault();
                    fPath = $(this).closest("li").attr("path");
                    optionsPython.args = [username, fPath];
                    new PythonShell("client/download.py", optionsPython)
                        .on('message', function (out) {
                            if (out == "finished") {
                                console.log("Correctly downloaded path");
                            }
                        });
                });

                $(".btn-delete").on("click", function dlHandler(e) {
                    e.preventDefault();
                    fPath = $(this).closest("li").attr("path");
                    optionsPython.args = [username, fPath];
                    new PythonShell("client/delete.py", optionsPython)
                        .on('message', function (out) {
                            if (out == "finished") {
                                console.log("Correctly deleted path");
                                location.reload();
                            }
                        });
                });

                $(".folder-element").on("click", "> .title-container", function hideChildren(e) {
                    e.preventDefault();

                    $(this).next().toggle();
                    $(this).find(".arrow-icon").toggleClass("rotated");
                });
            }
        });

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
