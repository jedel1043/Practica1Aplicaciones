const {app, BrowserWindow} = require('electron');

function createWindow() {
    let win = new BrowserWindow({
        // width: 950,
        // height: 600,
        width: 1150,
        height: 600,
        resizable: false,
        webPreferences: {
            nodeIntegration: true
        }
    });

    win.loadFile('index.html');
    // win.removeMenu();

    win.webContents.openDevTools();
}

app.on("ready", createWindow);