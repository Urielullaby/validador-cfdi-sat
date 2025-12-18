const input = document.getElementById("xmlInput");
const hiddenInput = document.getElementById("hiddenInput");
const btnPdf = document.getElementById("btnPdf");
const btnZip = document.getElementById("btnZip");
const btnClear = document.getElementById("btnClear");
const form = document.getElementById("formCFDI");
const lista = document.getElementById("lista");
const contador = document.getElementById("contador");

let dataTransfer = new DataTransfer();

function renderLista() {
  lista.innerHTML = "";

  const files = Array.from(dataTransfer.files);
  const count = files.length;

  contador.textContent =
    count === 0
      ? "Ningún archivo seleccionado"
      : `${count} archivo(s) seleccionado(s)`;

  btnPdf.disabled = true;
  btnZip.disabled = true;

  if (count === 1) btnPdf.disabled = false;
  if (count > 1) btnZip.disabled = false;

  files.forEach((file, index) => {
    const li = document.createElement("li");
    li.textContent = file.name;

    const del = document.createElement("span");
    del.textContent = "x";
    del.className = "remove";
    del.onclick = () => {
      eliminarArchivo(index);
    };

    li.appendChild(del);
    lista.appendChild(li);
  });

  hiddenInput.files = dataTransfer.files;
}

function eliminarArchivo(index) {
  const files = Array.from(dataTransfer.files);
  dataTransfer = new DataTransfer();

  files.forEach((f, i) => {
    if (i !== index) dataTransfer.items.add(f);
  });

  renderLista();
}

input.addEventListener("change", () => {
  for (const file of input.files) {
    if (!file.name.toLowerCase().endsWith(".xml")) continue;

    const existe = Array.from(dataTransfer.files)
      .some(f => f.name === file.name);

    if (!existe && dataTransfer.files.length < 10) {
      dataTransfer.items.add(file);
    }
  }

  input.value = "";
  renderLista();
});

btnPdf.onclick = () => form.submit();
btnZip.onclick = () => form.submit();

btnClear.onclick = () => {
  dataTransfer = new DataTransfer();
  hiddenInput.files = dataTransfer.files;
  lista.innerHTML = "";
  contador.textContent = "Ningún archivo seleccionado";
  btnPdf.disabled = true;
  btnZip.disabled = true;
};
