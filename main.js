const {app, BrowserWindow} = require('electron');

function createWindow() {
    const win = new BrowserWindow({
        width: 950,
        height: 600,
        webPreferences: {
            nodeIntegration: true
        },
        resizable: false
    });

    win.loadFile('index.html');
    // win.removeMenu();

    // win.webContents.openDevTools();
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow()
    }
})