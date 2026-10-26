import { useEffect, useRef, useState } from 'react';
import { analyze, type Analysis } from './api';
const labels = { papel: 'Papel, papelão', plastico: 'Plástico', metal: 'Metal', vidro: 'Vidro', misto: 'Material misto', desconhecido: 'Material desconhecido' };
export default function App() {
  const [page, setPage] = useState<'home'|'upload'|'result'>('home');
  const [file, setFile] = useState<File|null>(null);
  const [preview, setPreview] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<Analysis|null>(null);
  const [history, setHistory] = useState<Analysis[]>([]);
  const title = useRef<HTMLHeadingElement>(null);
  const input = useRef<HTMLInputElement>(null);
  useEffect(() => { title.current?.focus(); }, [page, busy, result]);
  useEffect(() => { if (!file) { setPreview(''); return; } const url = URL.createObjectURL(file); setPreview(url); return () => URL.revokeObjectURL(url); }, [file]);
  function choose(selected?: File) {
    setError(''); setResult(null);
    if (!selected) return;
    setFile(null);
    if (!['image/jpeg','image/png'].includes(selected.type)) { setError('Envie uma imagem JPEG ou PNG.'); return; }
    if (!selected.size || selected.size > 5*1024*1024) { setError('Escolha uma imagem não vazia de até 5 MB.'); return; }
    setFile(selected);
  }
  function reset() { setFile(null); setResult(null); setError(''); setPage('upload'); if (input.current) input.current.value = ''; }
  async function submit() {
    if (!file || busy) return;
    setBusy(true); setError('');
    try { const data = await analyze(file); setResult(data); setHistory(h => [data, ...h].slice(0, 5)); setPage('result'); }
    catch (e) { setError(e instanceof Error ? e.message : 'Não foi possível analisar.'); }
    finally { setBusy(false); }
  }
  return <div className="app">
    <header className="brand"><button className="brand-button" onClick={() => { if (!busy) setPage('home'); }} aria-label="Ecomigo — início"><img src="/assets/wordmark.svg" alt="Ecomigo" width="136" height="33"/></button><span>Pequenas atitudes. Novos caminhos.</span></header>
    <main>
      {page === 'home' ? <section className="welcome">
        <div className="identity"><img src="/assets/logo.svg" alt="" width="246" height="246"/><img src="/assets/wordmark.svg" alt="Ecomigo" width="272" height="66"/></div>
        <div><p className="eyebrow">UM NOVO OLHAR PARA OS RESÍDUOS</p><h1 ref={title} tabIndex={-1}>O seu lixo vale mais</h1><p>Uma fotografia é o primeiro passo. Identifique o possível material do seu resíduo e descubra como buscar o descarte adequado.</p><button className="primary" onClick={reset}>Começar a reciclar <span aria-hidden="true">→</span></button><small>Papel · Plástico · Metal · Vidro</small></div>
      </section> : page === 'upload' ? <section className="upload" aria-busy={busy}>
        <div className="screen-heading"><button className="back" disabled={busy} onClick={() => setPage('home')} aria-label="Voltar ao início">←</button><h1 ref={title} tabIndex={-1}>{busy ? 'Analisando sua imagem' : 'Pesquisar por imagem'}</h1></div>
        <p className="upload-intro">Fotografe um único objeto, com boa iluminação e fundo simples.</p>
        <div className="viewfinder">{preview && <img className="preview" src={preview} alt="Pré-visualização da imagem selecionada"/>}{!preview && <p>Seu próximo passo<br/>começa com uma foto</p>}{busy && <div className="loading" role="status"><span className="spinner"/>Identificando o possível material…</div>}</div>
        <div className="upload-actions"><label className={'secondary ' + (busy ? 'disabled' : '')}> {file ? 'Substituir imagem' : 'Escolher imagem'}<input ref={input} type="file" accept="image/jpeg,image/png" disabled={busy} onChange={e => choose(e.target.files?.[0])}/></label><label className={'secondary ' + (busy ? 'disabled' : '')}>Tirar foto<input type="file" accept="image/jpeg,image/png" capture="environment" disabled={busy} onChange={e => choose(e.target.files?.[0])}/></label></div>
        <small>JPEG ou PNG · Até 5 MB</small>{file && <p className="filename">{file.name}</p>}
        {error && <p className="error" role="alert">{error}</p>}
        <button className="primary" disabled={!file || busy} onClick={submit}>{busy ? 'Analisando…' : 'Analisar imagem'} <span aria-hidden="true">→</span></button>
        <p className="privacy">A foto será enviada ao serviço de IA para análise. O Ecomigo não armazena sua imagem. Evite incluir pessoas ou dados pessoais.</p>
      </section> : result && <section className={'result ' + result.material}>
        <div className="screen-heading"><button className="back" onClick={reset} aria-label="Realizar outra análise">←</button><h1 ref={title} tabIndex={-1}>Detalhes</h1></div>
        <div className="material-banner"><h2>{labels[result.material]}</h2>{result.material === 'plastico' && !result.identificacao_inconclusiva && <img src="/assets/plastico.svg" alt="" width="117" height="138"/>}</div>
        <div className="result-body"><p className="eyebrow">{result.identificacao_inconclusiva ? 'PRECISAMOS DE MAIS DETALHES' : 'IDENTIFICAÇÃO VISUAL ESTIMADA'}</p><h2>{result.objeto}</h2><p>{result.observacao}</p>
        {result.identificacao_inconclusiva ? <div className="notice"><h3>Identificação inconclusiva</h3><p>Não foi possível indicar um descarte com segurança. Tente outra foto do objeto isolado e de suas marcações. Para itens perigosos ou materiais mistos, consulte o serviço local responsável.</p></div> : result.orientacao ? <><h3>Como descartar?</h3><p>{result.orientacao}</p><h3>Cuidados</h3><p>{result.cuidados}</p><div className="notice"><strong>Orientação geral provisória</strong><p>Confirme as regras e os materiais aceitos na sua cidade.</p><small>{result.fonte_orientacao}<br/>Atualização: {result.data_atualizacao}</small></div></> : <div className="notice"><h3>Orientação não cadastrada</h3><p>A base ainda não contém orientação para este material. Consulte a coleta local antes do descarte.</p></div>}
        <button className="primary" onClick={reset}>Analisar outra imagem <span aria-hidden="true">→</span></button></div>
      </section>}
      {page === 'home' && history.length > 0 && <section className="history"><h2>Análises desta visita</h2><p>Disponíveis somente enquanto esta página estiver aberta.</p>{history.map((item, i) => <button key={i} onClick={() => {setResult(item); setPage('result');}}>{item.objeto}<span>{labels[item.material]} →</span></button>)}</section>}
    </main><footer>Ecomigo · Projeto acadêmico de Sistemas Inteligentes Aplicados</footer>
  </div>;
}
