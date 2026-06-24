const matrixElement = document.getElementById("matrix");
const outputElement = document.getElementById("output");

const clearButton = document.getElementById("clearButton");
const fillButton = document.getElementById("fillButton");
const invertButton = document.getElementById("invertButton");

const formatRadios = document.querySelectorAll('input[name="format"]');

let matrix = createEmptyMatrix();

function createEmptyMatrix() {
    const data = [];

    for (let row = 0; row < 8; row++) {
        data[row] = [];

        for (let col = 0; col < 8; col++) {
            data[row][col] = 0;
        }
    }

    return data;
}

function createMatrixDisplay() {
    matrixElement.innerHTML = "";

    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const led = document.createElement("button");

            led.type = "button";
            led.className = "led";
            led.dataset.row = row;
            led.dataset.col = col;
            led.setAttribute("aria-label", `Zeile ${row}, Spalte ${col}`);

            led.addEventListener("click", () => {
                toggleLed(row, col);
            });

            matrixElement.appendChild(led);
        }
    }

    updateDisplay();
}

function toggleLed(row, col) {
    matrix[row][col] = matrix[row][col] ? 0 : 1;
    updateDisplay();
}

function updateDisplay() {
    const leds = document.querySelectorAll(".led");

    leds.forEach((led) => {
        const row = Number(led.dataset.row);
        const col = Number(led.dataset.col);

        led.classList.toggle("on", matrix[row][col] === 1);
    });

    updateOutput();
}

function getSelectedFormat() {
    return document.querySelector('input[name="format"]:checked').value;
}

function updateOutput() {
    const format = getSelectedFormat();

    if (format === "python") {
        outputElement.textContent = createPythonOutput();
    } else {
        outputElement.textContent = createCOutput();
    }
}

function createPythonOutput() {
    let text = "bild = [\n";

    for (let row = 0; row < 8; row++) {
        const bits = matrix[row].join("");

        text += "    0b" + bits;

        if (row < 7) {
            text += ",";
        }

        text += "\n";
    }

    text += "]";

    return text;
}

function createCOutput() {
    let text = "byte bild[8] = {\n";

    for (let row = 0; row < 8; row++) {
        const bits = matrix[row].join("");

        text += "    0b" + bits;

        if (row < 7) {
            text += ",";
        }

        text += "\n";
    }

    text += "};";

    return text;
}

function clearMatrix() {
    matrix = createEmptyMatrix();
    updateDisplay();
}

function fillMatrix() {
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            matrix[row][col] = 1;
        }
    }

    updateDisplay();
}

function invertMatrix() {
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            matrix[row][col] = matrix[row][col] ? 0 : 1;
        }
    }

    updateDisplay();
}

clearButton.addEventListener("click", clearMatrix);
fillButton.addEventListener("click", fillMatrix);
invertButton.addEventListener("click", invertMatrix);

formatRadios.forEach((radio) => {
    radio.addEventListener("change", updateOutput);
});

createMatrixDisplay();
