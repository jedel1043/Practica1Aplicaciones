const dropZone = document.getElementById("drag-zone");
const filePicker = document.getElementById("filepicker");
if (dropZone) {
    const hoverClassName = "hover";

    // Handle drag* events to handle style
    // Add the css you want when the class "hover" is present
    dropZone.addEventListener("dragenter", function (e) {
        e.preventDefault();
        dropZone.classList.add(hoverClassName);
    });

    dropZone.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropZone.classList.add(hoverClassName);
    });

    dropZone.addEventListener("dragleave", function (e) {
        e.preventDefault();
        dropZone.classList.remove(hoverClassName);
    });

    // This is the most important event, the event that gives access to files
    dropZone.addEventListener("drop", function (e) {
        e.preventDefault();
        dropZone.classList.remove(hoverClassName);

        const files = Array.from(e.dataTransfer.files);
        console.log(files);
        // TODO do somethings with files...
    });
}

filePicker.addEventListener("change", function(event){
    let files = event.target.files;

    for (let i=0; i<files.length; i++) {
      let item = files[i];
      console.log(item.webkitRelativePath);
    };
  
}, false);
