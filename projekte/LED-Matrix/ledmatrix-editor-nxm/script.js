const matrixElement = document.getElementById("matrix");
const outputElement = document.getElementById("output");
const bitInfoElement = document.getElementById("bitInfo");

const rowsInput = document.getElementById("rowsInput");
const colsInput = document.getElementById("colsInput");
const resizeButton = document.getElementById("resizeButton");

const clearButton = document.getElementById("clearButton");
const fillButton = document.getElementById("fillButton");
const invertButton = document.getElementById("invertButton");

const formatRadios = document.querySelectorAll('input[name="format"]');

let rows = 8;
let cols = 8;
let matrix = createEmptyMatrix(rows, cols);

function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

function readSizeInputs() {
    rows = clamp(Number(rowsInput.value), 2, 11);
    cols = clamp(Number(colsInput.value), 2, 19);

    rowsInput.value = rows;
    colsInput.value = cols;
}

function createEmptyMatrix(rowCount, colCount) {
    const data = [];

    for (let row = 0; row < rowCount; row++) {
        data[row] = [];

        for (let col = 0; col < colCount; col++) {
            data[row][col] = 0;
        }
    }

    return data;
}

function resizeMatrix() {
    readSizeInputs();

    const oldMatrix = matrix;
    const oldRows = oldMatrix.length;
    const oldCols = oldMatrix[0]?.length || 0;

    matrix = createEmptyMatrix(rows, cols);

    const rowsToCopy = Math.min(rows, oldRows);
    const colsToCopy = Math.min(cols, oldCols);

    for (let row = 0; row < rowsToCopy; row++) {
        for (let col = 0; col < colsToCopy; col++) {
            matrix[row][col] = oldMatrix[row][col];
        }
    }

    createMatrixDisplay();
}

function createMatrixDisplay() {
    matrixElement.innerHTML = "";

    matrixElement.style.gridTemplateColumns = `repeat(${cols}, 38px)`;
    matrixElement.style.gridTemplateRows = `repeat(${rows}, 38px)`;

    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
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
    updateBitInfo();
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
    let text = `bild = [  # ${rows} Zeilen x ${cols} Spalten\n`;

    for (let row = 0; row < rows; row++) {
        const bits = matrix[row].join("");

        text += "    0b" + bits;

        if (row < rows - 1) {
            text += ",";
        }

        text += "\n";
    }

    text += "]";

    return text;
}

function createCOutput() {
    let text = `byte bild[${rows}] = {  // ${rows} Zeilen x ${cols} Spalten\n`;

    for (let row = 0; row < rows; row++) {
        const bits = matrix[row].join("");

        text += "    0b" + bits;

        if (row < rows - 1) {
            text += ",";
        }

        text += "\n";
    }

    text += "};";

    return text;
}

function updateBitInfo() {
    let colText = "Spalte:   ";
    let bitText = "Bitwert:  ";

    for (let col = 0; col < cols; col++) {
        colText += String(col).padStart(2, " ") + " ";
        bitText += String(cols - 1 - col).padStart(2, " ") + " ";
    }

    bitInfoElement.textContent = colText + "\n" + bitText;
}

function clearMatrix() {
    matrix = createEmptyMatrix(rows, cols);
    updateDisplay();
}

function fillMatrix() {
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            matrix[row][col] = 1;
        }
    }

    updateDisplay();
}

function invertMatrix() {
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            matrix[row][col] = matrix[row][col] ? 0 : 1;
        }
    }

    updateDisplay();
}

resizeButton.addEventListener("click", resizeMatrix);
rowsInput.addEventListener("change", resizeMatrix);
colsInput.addEventListener("change", resizeMatrix);

clearButton.addEventListener("click", clearMatrix);
fillButton.addEventListener("click", fillMatrix);
invertButton.addEventListener("click", invertMatrix);

formatRadios.forEach((radio) => {
    radio.addEventListener("change", updateOutput);
});

createMatrixDisplay();
