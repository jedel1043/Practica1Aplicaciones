const {app, BrowserWindow} = require('electron');
const { PythonShell } = require('python-shell');
const path = require("path");

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

function createWindow() {
    let win = new BrowserWindow({
        // width: 950,
        // height: 600,
        width: 1150,
        height: 600,
        resizable: false,
        webPreferences: {
            enableRemoteModule: true,
            nodeIntegration: true
        }
    });

    win.loadFile('index.html');
    // win.removeMenu();

    win.webContents.openDevTools();
}

app.on("ready", createWindow);

app.on("window-all-closed", function closeUp(){
    if (process.platform != 'darwin'){
        // end the input stream and allow the server to exit
        ScriptServer.childProcess.kill('SIGINT');
        app.quit();
    }
})