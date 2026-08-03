

let indent = true;
let timeout;
let timeout1;
function submitText() {
    const mcode = document.getElementById("input").value
    if (mcode) {
        let lines = mcode.split(/\r?\n/);
        lines = lines.filter(line => line.trim() && !line.trim().startsWith("#"));
        let jumpList = [];
        let lmcode = "";
        lines.forEach((line, index) => {
            let words = line.trim().split(/\s+/);
            let firstWord = words[0]; 
            if (firstWord === "jump") {
                let secondWord = words[1];
                jumpList.push(parseInt(secondWord));
            }
        });
        lines.forEach((line, index) => {
            let words = line.trim().split(/\s+/);
            let firstWord = words[0];
            if (jumpList.includes(index)) {
                lmcode += "j" + String(index) + ":" + "\n";
            }
            if (firstWord === "jump" && !isNaN(parseInt(words[1])) && parseInt(words[1]) >= 0 ) {
                if (indent == false) {
                    lmcode +=`${words[0]} j${words[1]} ${words.slice(2).join(" ")}\n`
                } else {
                    lmcode +=`    ${words[0]} j${words[1]} ${words.slice(2).join(" ")}\n`
                }
                
            } else {
                // lmcode += "    " + (words.join(" ")) + "\n";
                if (indent == false) {
                    lmcode += `${words.join(" ")}\n`
                } else {
                    lmcode += `    ${words.join(" ")}\n`
                }
            }
        });
    const output = document.getElementById("output");
    output.value = lmcode
    }
}

function copy() {
    let copyText = document.getElementById("output").value;
    statusElement = document.getElementById("status");
    statusElement.style.transition = "none";
    statusElement.style.opacity = "1";
    navigator.clipboard.writeText(copyText).then(() => {
        statusElement.textContent = "Text copied to clipboard!";
      }).catch(err => {
        statusElement.textContent= "Failed to copy text.";
        console.error('Error copying text: ', err);
      });

      if (timeout) {
        clearTimeout(timeout);
      }

      if (timeout1) {
        clearTimeout(timeout1);
      }

      timeout = setTimeout(() => {
        statusElement.style.transition = "opacity 1.5s ease";
        statusElement.style.opacity = "0";
        timeout1 = setTimeout(() => {
            statusElement.textContent= "";
        }, 1500);
      }, 1000);
    // copyText.select();
    // copyText.setSelectionRange(0, 99999);
    // document.execCommand("copy");
    // document.getElementById("status").textContent = "Text copied to clipboard!";
    }
    

function toggleButton() {
    indent = !indent;
    
    const button = document.getElementById("toggleButton");
    button.className = indent ? "toggled" : "untoggled";


}


