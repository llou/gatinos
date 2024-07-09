// Gatinos.com
//
async function jsonRpcRequest(method, params) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: method,
        params: params,
        id: 1
      })
    })

    const data = await response.json();
    if (data.error) {
        throw new Error(data.error.message);
    }
    return data.result;
};

function alternar_comida_usuario(colonia_slug, ano, mes, dia) {
  document.getElementsByTagName("html")[0].style.cursor = "wait";
  jsonRpcRequest("alternar_comida_usuario", [colonia_slug, ano, mes, dia]).then(() => {window.location.reload()})
}

function avistar_gato(colonia_slug, gato_slug) {
  jsonRpcRequest("avistar_gato", [colonia_slug, gato_slug]).then(() => 
  window.location.reload())
}

function nuevo_codigo_qr() {
  jsonRpcRequest("nuevo_codigo_qr", []).then(() => {
    setTimeout( () => {window.location.reload() }, 500)
  })
}

function borrar_codigo_qr() {
  jsonRpcRequest("borrar_codigo_qr", []).then(() => {
    setTimeout( () => {window.location.reload() }, 500)
  })
}

function fabrica_de_estados(nombre) {
  async (colonia_slug, gato_slug) => {
      await jasonRpcRequest(nombre, [colonia_slug, gato_slug])
      window.location.reload()
  }
}

const capturar = fabrica_de_estados("capturar");
const liberar = fabrica_de_estados("liberar");
const desaparecer = fabrica_de_estados("desaparecer");
const olvidar = fabrica_de_estados("olvidar");
const morir = fabrica_de_estados("morir");
