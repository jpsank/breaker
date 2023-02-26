
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

const selected = [];

function drawSeq(name, seq, i) {
    let y = 15 + i*15;
    ctx.fillStyle = 'black';
    ctx.fillText(name, 0, y);
    for (let j = 0; j < seq.length; j++) {
        let cell = seq[j];
        let x = 200 + j*10;
        if (cell == '-') {
            ctx.fillStyle = 'gray';
        } else {
            ctx.fillStyle = (data.SS_cons[j] == '<' || data.SS_cons[j] == '>') ? 'blue' : 'black';
            for (const [i2, j2] of selected) {
                if (i == i2 && j == j2) {
                    ctx.fillStyle = 'yellow';
                }
            }
        }
        ctx.fillText(cell, x, y);
    }
}

function view() {
    ctx.font = '12px monospace';
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    console.log(selected);
    let msa = data["msa"];
    drawSeq('SS_cons', data.SS_cons, 0);
    let i = 1;
    for (const seq of Object.values(msa)) {
        drawSeq(seq.name, seq.seq, ++i);
    }
}

let dragging = false;

function mouseDown(event) {
    dragging = true;
}

function mouseUp(event) {
    dragging = false;
}

function mouseMove(event) {
    if (!dragging) {
        return;
    }
    let x = event.clientX;
    let y = event.clientY;
    let rect = canvas.getBoundingClientRect();
    let x2 = x - rect.left;
    let y2 = y - rect.top;
    let i = Math.round((y2 - 15) / 15);
    let j = Math.round((x2 - 200) / 10);
    selected.push([i, j]);
    view();
}

canvas.addEventListener('mousemove', mouseMove);
canvas.addEventListener('mousedown', mouseDown);
canvas.addEventListener('mouseup', mouseUp);

canvas.addEventListener('keydown', function(event) {
    // left
    if (event.key == 'ArrowLeft') {
        for (const [i, j] of selected) {
        }
        view();
    }
    // right
    if (event.key == 'ArrowRight') {
            
        view();
    }
});


window.onload = function() {
    view();
}

// let selected = [];
// function clickCell(seq, idx) {
//     selected.push([seq, idx]);
//     console.log(seq, idx);
// }
