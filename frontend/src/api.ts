export type Analysis = {
  objeto: string; material: 'papel'|'plastico'|'metal'|'vidro'|'misto'|'desconhecido';
  identificacao_inconclusiva: boolean; observacao: string; orientacao: string|null;
  cuidados: string|null; fonte_orientacao: string|null; data_atualizacao: string|null;
  orientacao_provisoria: boolean;
};
export async function analyze(file: File): Promise<Analysis> {
  const form = new FormData(); form.append('imagem', file);
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 65000);
  try {
    const response = await fetch('/api/analises', { method: 'POST', body: form, signal: controller.signal });
    const body = await response.json().catch(() => null);
    if (!response.ok) throw new Error(typeof body?.detail === 'string' ? body.detail : 'Não foi possível analisar a imagem. Tente novamente.');
    return body;
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw new Error('A análise demorou. Tente novamente.');
    if (error instanceof TypeError) throw new Error('Não foi possível conectar ao servidor. Verifique a conexão.');
    throw error;
  } finally { window.clearTimeout(timeout); }
}
