const equipamento = document.querySelector('#equipamento_id');
const retirada = document.querySelector('#data_retirada');
const devolucao = document.querySelector('#data_prevista');
const estimativa = document.querySelector('#estimativa');

function atualizarEstimativa() {
  if (!equipamento || !retirada.value || !devolucao.value) return;
  const inicio = new Date(`${retirada.value}T00:00:00`);
  const fim = new Date(`${devolucao.value}T00:00:00`);
  const dias = Math.max(Math.round((fim - inicio) / 86400000), 1);
  const diaria = Number(equipamento.selectedOptions[0].dataset.diaria);
  estimativa.textContent = fim >= inicio
    ? `Estimativa: ${(dias * diaria).toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})}`
    : 'A data de devolução deve ser posterior à retirada.';
}

[equipamento, retirada, devolucao].forEach((campo) => campo?.addEventListener('change', atualizarEstimativa));
atualizarEstimativa();

