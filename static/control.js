const input = document.getElementById("xmlInput");
const btnPdf = document.getElementById("btnPdf");
const btnZip = document.getElementById("btnZip");

input.addEventListener("change", () => {
  const count = input.files.length;

  // reset
  btnPdf.disabled = true;
  btnZip.disabled = true;

  if (count === 1) {
    btnPdf.disabled = false;
  }

  if (count > 1) {
    btnZip.disabled = false;
  }
});
