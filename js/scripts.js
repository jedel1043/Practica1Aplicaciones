var path = require("path");

//Python Shell
const { PythonShell } = require("python-shell");

var optionsPython = {
    // mode: 'json',
    pythonOptions: ['-u'],
    scriptPath: path.join(__dirname, 'engine/'),
    args: []
};
//Inicializar Server
let ScriptServer = new PythonShell("server/server.py", optionsPython);

ScriptServer.on('message', function(out){
    console.log(out);
})

$(document).ready(function(){
    //Adquirir nombre de Usuario
    let urlStr = window.location.href;
    let url = new URL(urlStr);
    let username = url.searchParams.get("username");
    
    

    const UploadContent = $(".main-content #container-upload");
    //Boton para subir Carpeta
    UploadContent.on("change", "#input-folder", function(e){
        // console.log($(this))
        //Obtener la ruta de la carpeta
        let folder = $(this)[0].files[0]
        let arrAllPath = folder.path.split("\\");
        let startPath = folder.webkitRelativePath.split("/")[0];
        //Formar ruta completa
        let strPath = "C://";
        for (let i = 1; i < arrAllPath.length; i++) {
            const element = arrAllPath[i];
            strPath = strPath +  element + "/";
            if(element == startPath){
                break;
            }
        }
        //Llamar script de python
        optionsPython.args = [username, strPath];
        let ScriptUploadFolder = new PythonShell("client/upload.py", optionsPython);

        ScriptUploadFolder.on('message', function(out){
            console.log(out);
        })
    })
    
})